from __future__ import annotations

import threading

from termad.ad import load_ad_from_dict
from termad.renderer import (
    CLEAR_SCREEN,
    ENTER_ALT_SCREEN,
    EXIT_ALT_SCREEN,
    HIDE_CURSOR,
    Renderer,
    SHOW_CURSOR,
)


class DummyOutput:
    def __init__(self, *, tty: bool) -> None:
        self._tty = tty
        self._parts: list[str] = []
        self.flush_count = 0

    def write(self, text: str) -> int:
        self._parts.append(text)
        return len(text)

    def flush(self) -> None:
        self.flush_count += 1

    def isatty(self) -> bool:
        return self._tty

    def fileno(self) -> int:
        return 1

    @property
    def text(self) -> str:
        return "".join(self._parts)


def sample_ad():
    return load_ad_from_dict(
        {
            "frames": ["HELLO\nWORLD"],
            "frame_rate": 120,
            "duration": 0.03,
            "metadata": {
                "advertiser": "ACME",
                "url": "https://example.com",
            },
        }
    )


def test_render_writes_ansi_lifecycle_sequences() -> None:
    output = DummyOutput(tty=True)
    renderer = Renderer(output=output)

    renderer.render(
        sample_ad(),
        stop_event=threading.Event(),
        dismiss_event=threading.Event(),
        resize_event=threading.Event(),
    )

    assert ENTER_ALT_SCREEN in output.text
    assert HIDE_CURSOR in output.text
    assert CLEAR_SCREEN in output.text
    assert SHOW_CURSOR in output.text
    assert EXIT_ALT_SCREEN in output.text
    assert "HELLO" in output.text


def test_render_no_tty_is_noop() -> None:
    output = DummyOutput(tty=False)
    renderer = Renderer(output=output)

    renderer.render(
        sample_ad(),
        stop_event=threading.Event(),
        dismiss_event=threading.Event(),
        resize_event=threading.Event(),
    )

    assert output.text == ""


def test_render_clips_when_terminal_is_small() -> None:
    output = DummyOutput(tty=True)
    renderer = Renderer(output=output)
    renderer._get_terminal_size = lambda: (5, 2)  # type: ignore[method-assign]

    ad = load_ad_from_dict(
        {
            "frames": ["123456789\nabcdefghi"],
            "frame_rate": 60,
            "duration": 0.02,
            "metadata": {
                "advertiser": "ACME",
                "url": "https://example.com",
            },
        }
    )

    renderer.render(
        ad,
        stop_event=threading.Event(),
        dismiss_event=threading.Event(),
        resize_event=threading.Event(),
    )

    assert EXIT_ALT_SCREEN in output.text
