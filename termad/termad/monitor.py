"""Background idle monitor for termad."""

from __future__ import annotations

import io
import select
import signal
import sys
import threading
import time
import termios
import tty
from contextlib import contextmanager
from typing import TextIO

from .ad import Ad, load_builtin_ad
from .renderer import Renderer


class IdleMonitor:
    """Monitors stdin idle state and triggers ad rendering."""

    def __init__(
        self,
        *,
        idle_seconds: float = 30.0,
        ad: Ad | None = None,
        poll_interval: float = 0.1,
        input_stream: TextIO | None = None,
        output_stream: TextIO | None = None,
    ) -> None:
        if idle_seconds <= 0:
            raise ValueError("idle_seconds must be greater than 0.")

        self.stop_event = threading.Event()
        self.show_now_event = threading.Event()
        self.dismiss_event = threading.Event()
        self.resize_event = threading.Event()

        self._idle_seconds = float(idle_seconds)
        self._poll_interval = max(float(poll_interval), 0.01)
        self._input_stream = input_stream if input_stream is not None else sys.stdin
        self._output_stream = output_stream if output_stream is not None else sys.stdout
        self._renderer = Renderer(output=self._output_stream)

        self._ad_lock = threading.Lock()
        self._state_lock = threading.Lock()
        self._monitor_lock = threading.Lock()

        self._ad: Ad = ad if ad is not None else load_builtin_ad()
        self._last_activity = time.monotonic()
        self._monitor_thread: threading.Thread | None = None
        self._render_thread: threading.Thread | None = None
        self._ad_active = False
        self._warned_no_tty = False

        self._interactive = self._is_interactive_tty()
        self._sigwinch_installed = False
        self._previous_sigwinch_handler = None

    def start(self) -> None:
        """Start idle monitoring in a daemon thread."""
        with self._monitor_lock:
            if self._monitor_thread is not None and self._monitor_thread.is_alive():
                self._mark_activity()
                return

            self.stop_event.clear()
            self.show_now_event.clear()
            self.dismiss_event.clear()
            self.resize_event.clear()
            self._mark_activity()

            self._install_sigwinch_handler()
            if not self._interactive and not self._warned_no_tty:
                print(
                    "termad: stdin/stdout is not a TTY; idle monitoring is running in no-op mode.",
                    file=sys.stderr,
                )
                self._warned_no_tty = True

            self._monitor_thread = threading.Thread(
                target=self._run,
                name="termad-monitor",
                daemon=True,
            )
            self._monitor_thread.start()

    def stop(self) -> None:
        """Stop idle monitoring and any active ad rendering."""
        self.stop_event.set()
        self.show_now_event.set()
        self.dismiss_event.set()

        monitor_thread = self._monitor_thread
        render_thread = self._render_thread

        if monitor_thread is not None and monitor_thread.is_alive():
            monitor_thread.join(timeout=2.0)
        if render_thread is not None and render_thread.is_alive():
            render_thread.join(timeout=2.0)

        with self._monitor_lock:
            self._monitor_thread = None
            self._render_thread = None
            self._ad_active = False

        self._uninstall_sigwinch_handler()

    def show_now(self) -> None:
        """Trigger ad rendering immediately."""
        self.show_now_event.set()

    def set_idle_seconds(self, idle_seconds: float) -> None:
        """Update idle threshold while running."""
        if idle_seconds <= 0:
            raise ValueError("idle_seconds must be greater than 0.")
        with self._state_lock:
            self._idle_seconds = float(idle_seconds)

    def set_ad(self, ad: Ad) -> None:
        """Swap the active ad definition."""
        with self._ad_lock:
            self._ad = ad

    def mark_activity(self) -> None:
        """Reset idle timer to now."""
        self._mark_activity()

    def _run(self) -> None:
        if not self._interactive:
            while not self.stop_event.wait(self._poll_interval):
                continue
            return

        while not self.stop_event.is_set():
            self._poll_for_input()
            self._reap_renderer_if_finished()

            if self.stop_event.is_set():
                break

            if self._ad_active:
                continue

            if self.show_now_event.is_set():
                self.show_now_event.clear()
                self._start_renderer()
                continue

            now = time.monotonic()
            with self._state_lock:
                idle_seconds = self._idle_seconds
                elapsed = now - self._last_activity

            if elapsed >= idle_seconds:
                self._start_renderer()

    def _poll_for_input(self) -> None:
        try:
            ready, _, _ = select.select([self._input_stream], [], [], self._poll_interval)
        except (OSError, ValueError, io.UnsupportedOperation):
            time.sleep(self._poll_interval)
            return

        if ready:
            self._mark_activity()
            if self._ad_active:
                self.dismiss_event.set()

    def _start_renderer(self) -> None:
        with self._state_lock:
            if self._ad_active:
                return
            self._ad_active = True

        with self._ad_lock:
            ad_snapshot = self._ad

        self.dismiss_event.clear()
        self.resize_event.clear()
        self.show_now_event.clear()

        self._render_thread = threading.Thread(
            target=self._render_worker,
            name="termad-renderer",
            daemon=True,
            args=(ad_snapshot,),
        )
        self._render_thread.start()

    def _render_worker(self, ad: Ad) -> None:
        try:
            with self._cbreak_input_mode():
                self._renderer.render(
                    ad,
                    stop_event=self.stop_event,
                    dismiss_event=self.dismiss_event,
                    resize_event=self.resize_event,
                )
        except Exception as exc:  # pragma: no cover - defensive logging path
            print(f"termad: renderer error: {exc}", file=sys.stderr)
        finally:
            self.dismiss_event.clear()
            self.show_now_event.clear()
            self._mark_activity()
            with self._state_lock:
                self._ad_active = False

    def _reap_renderer_if_finished(self) -> None:
        thread = self._render_thread
        if thread is None:
            return
        if thread.is_alive():
            return

        thread.join(timeout=0)
        self._render_thread = None
        with self._state_lock:
            self._ad_active = False

    def _mark_activity(self) -> None:
        with self._state_lock:
            self._last_activity = time.monotonic()

    def _is_interactive_tty(self) -> bool:
        input_tty = bool(getattr(self._input_stream, "isatty", lambda: False)())
        output_tty = bool(getattr(self._output_stream, "isatty", lambda: False)())
        return input_tty and output_tty

    def _install_sigwinch_handler(self) -> None:
        if threading.current_thread() is not threading.main_thread():
            return
        if self._sigwinch_installed:
            return

        self._previous_sigwinch_handler = signal.getsignal(signal.SIGWINCH)
        signal.signal(signal.SIGWINCH, self._handle_sigwinch)
        self._sigwinch_installed = True

    def _uninstall_sigwinch_handler(self) -> None:
        if not self._sigwinch_installed:
            return

        if threading.current_thread() is not threading.main_thread():
            return

        previous = self._previous_sigwinch_handler
        if previous is None:
            previous = signal.SIG_DFL

        signal.signal(signal.SIGWINCH, previous)
        self._sigwinch_installed = False

    def _handle_sigwinch(self, signum: int, frame: object) -> None:
        self.resize_event.set()

        previous = self._previous_sigwinch_handler
        if callable(previous) and previous is not self._handle_sigwinch:
            try:
                previous(signum, frame)
            except Exception:
                pass

    @contextmanager
    def _cbreak_input_mode(self):
        if not self._interactive:
            yield
            return

        try:
            fd = self._input_stream.fileno()
        except (AttributeError, io.UnsupportedOperation):
            yield
            return

        try:
            old_attrs = termios.tcgetattr(fd)
        except termios.error:
            yield
            return

        try:
            tty.setcbreak(fd)
            yield
        finally:
            try:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_attrs)
            except termios.error:
                pass
