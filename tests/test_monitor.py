from __future__ import annotations

from contextlib import nullcontext

import pytest

from termad.ad import load_ad_from_dict
from termad.monitor import IdleMonitor


class DummyStream:
    def __init__(self, *, tty: bool, fd: int = 0) -> None:
        self._tty = tty
        self._fd = fd

    def isatty(self) -> bool:
        return self._tty

    def fileno(self) -> int:
        return self._fd


def sample_ad():
    return load_ad_from_dict(
        {
            "frames": ["A"],
            "frame_rate": 2,
            "duration": 1,
            "metadata": {
                "advertiser": "ACME",
                "url": "https://example.com",
            },
        }
    )


def test_monitor_rejects_non_positive_idle_seconds() -> None:
    with pytest.raises(ValueError, match="idle_seconds"):
        IdleMonitor(idle_seconds=0)


def test_poll_for_input_marks_activity_and_dismiss(monkeypatch) -> None:
    stream = DummyStream(tty=True)
    monitor = IdleMonitor(idle_seconds=1, ad=sample_ad(), input_stream=stream, output_stream=stream)

    activity_calls = {"count": 0}

    def mark_activity() -> None:
        activity_calls["count"] += 1

    monkeypatch.setattr(monitor, "_mark_activity", mark_activity)
    monkeypatch.setattr("termad.monitor.select.select", lambda *_: ([stream], [], []))

    monitor._ad_active = True
    monitor._poll_for_input()

    assert activity_calls["count"] == 1
    assert monitor.dismiss_event.is_set()


def test_poll_for_input_handles_select_errors(monkeypatch) -> None:
    stream = DummyStream(tty=True)
    monitor = IdleMonitor(idle_seconds=1, ad=sample_ad(), input_stream=stream, output_stream=stream)

    def boom(*_args, **_kwargs):
        raise OSError("select failed")

    monkeypatch.setattr("termad.monitor.select.select", boom)
    monkeypatch.setattr("termad.monitor.time.sleep", lambda *_: None)

    monitor._poll_for_input()


def test_run_triggers_show_now(monkeypatch) -> None:
    stream = DummyStream(tty=True)
    monitor = IdleMonitor(idle_seconds=30, ad=sample_ad(), input_stream=stream, output_stream=stream)

    monitor._interactive = True
    calls = {"count": 0}

    monkeypatch.setattr(monitor, "_poll_for_input", lambda: None)
    monkeypatch.setattr(monitor, "_reap_renderer_if_finished", lambda: None)

    def fake_start_renderer() -> None:
        calls["count"] += 1
        monitor.stop_event.set()

    monkeypatch.setattr(monitor, "_start_renderer", fake_start_renderer)

    monitor.show_now_event.set()
    monitor._run()

    assert calls["count"] == 1


def test_run_non_interactive_returns_when_stopped() -> None:
    stream = DummyStream(tty=False)
    monitor = IdleMonitor(idle_seconds=1, ad=sample_ad(), input_stream=stream, output_stream=stream)

    monitor.stop_event.set()
    monitor._run()


def test_render_worker_resets_state(monkeypatch) -> None:
    stream = DummyStream(tty=True)
    monitor = IdleMonitor(idle_seconds=1, ad=sample_ad(), input_stream=stream, output_stream=stream)

    monitor._ad_active = True
    monitor.show_now_event.set()
    monitor.dismiss_event.set()

    calls = {"render": 0, "activity": 0}

    monkeypatch.setattr(monitor, "_cbreak_input_mode", lambda: nullcontext())

    def fake_render(*_args, **_kwargs) -> None:
        calls["render"] += 1

    def fake_mark_activity() -> None:
        calls["activity"] += 1

    monkeypatch.setattr(monitor._renderer, "render", fake_render)
    monkeypatch.setattr(monitor, "_mark_activity", fake_mark_activity)

    monitor._render_worker(sample_ad())

    assert calls["render"] == 1
    assert calls["activity"] == 1
    assert not monitor.dismiss_event.is_set()
    assert not monitor.show_now_event.is_set()
    assert monitor._ad_active is False
