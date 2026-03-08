"""ANSI terminal renderer for termad ads."""

from __future__ import annotations

import os
import sys
import threading
import time
from typing import TextIO

from .ad import Ad

CSI = "\x1b["
ENTER_ALT_SCREEN = "\x1b[?1049h"
EXIT_ALT_SCREEN = "\x1b[?1049l"
HIDE_CURSOR = "\x1b[?25l"
SHOW_CURSOR = "\x1b[?25h"
CLEAR_SCREEN = CSI + "2J"
CURSOR_HOME = CSI + "H"
RESET_SGR = CSI + "0m"


class Renderer:
    """Renders animated ads using ANSI cursor control."""

    def __init__(self, output: TextIO | None = None, min_columns: int = 80, min_rows: int = 24) -> None:
        self._output = output if output is not None else sys.stdout
        self._min_columns = min_columns
        self._min_rows = min_rows

    def render(
        self,
        ad: Ad,
        *,
        stop_event: threading.Event,
        dismiss_event: threading.Event,
        resize_event: threading.Event,
    ) -> None:
        """Render an ad until dismiss, timeout, or shutdown."""
        if not self._is_tty():
            return

        start_time = time.monotonic()
        frame_index = 0
        x = 0
        y = 0
        vx = 1
        vy = 1

        self._output.write(ENTER_ALT_SCREEN + HIDE_CURSOR + CLEAR_SCREEN + CURSOR_HOME)
        self._output.flush()

        try:
            while not stop_event.is_set() and not dismiss_event.is_set():
                elapsed = time.monotonic() - start_time
                if elapsed >= ad.duration:
                    break

                if resize_event.is_set():
                    resize_event.clear()

                frame_text = ad.frames[frame_index % len(ad.frames)]
                sprite_lines = frame_text.splitlines() or [""]
                sprite_height = len(sprite_lines)
                sprite_width = max((len(line) for line in sprite_lines), default=0)

                columns, rows = self._get_terminal_size()
                max_x = max(columns - sprite_width, 0)
                max_y = max(rows - sprite_height, 0)

                if x < 0:
                    x = 0
                    vx = abs(vx)
                elif x > max_x:
                    x = max_x
                    vx = -abs(vx)

                if y < 0:
                    y = 0
                    vy = abs(vy)
                elif y > max_y:
                    y = max_y
                    vy = -abs(vy)

                self._draw_frame(sprite_lines, x, y, columns, rows, ad)
                frame_index += 1

                next_x = x + vx
                next_y = y + vy

                if next_x < 0 or next_x > max_x:
                    vx *= -1
                    next_x = x + vx

                if next_y < 0 or next_y > max_y:
                    vy *= -1
                    next_y = y + vy

                x = max(0, min(max_x, next_x))
                y = max(0, min(max_y, next_y))

                frame_duration = 1.0 / ad.frame_rate
                end_wait = time.monotonic() + frame_duration
                while time.monotonic() < end_wait:
                    if stop_event.is_set() or dismiss_event.is_set():
                        break
                    time.sleep(0.02)
        finally:
            self._output.write(RESET_SGR + SHOW_CURSOR + EXIT_ALT_SCREEN)
            self._output.flush()

    def _draw_frame(self, sprite_lines: list[str], x: int, y: int, columns: int, rows: int, ad: Ad) -> None:
        self._output.write(CLEAR_SCREEN + CURSOR_HOME)

        for line_number, line in enumerate(sprite_lines):
            row = y + line_number + 1
            if row < 1 or row > rows:
                continue
            if x >= columns:
                continue

            visible = line[: max(columns - x, 0)]
            if not visible:
                continue

            self._output.write(f"{CSI}{row};{x + 1}H{visible}")

        advertiser = ad.metadata.get("advertiser", "")
        url = ad.metadata.get("url", "")
        footer = f"{advertiser}  {url}".strip()[:columns]
        if footer:
            self._output.write(f"{CSI}{rows};1H{footer}")

        self._output.flush()

    def _get_terminal_size(self) -> tuple[int, int]:
        try:
            size = os.get_terminal_size(self._output.fileno())
            columns = max(size.columns, 1)
            rows = max(size.lines, 1)
            return columns, rows
        except OSError:
            return self._min_columns, self._min_rows

    def _is_tty(self) -> bool:
        return bool(getattr(self._output, "isatty", lambda: False)())
