"""Public API for termad."""

from __future__ import annotations

import threading
from pathlib import Path
from typing import Any

from .ad import Ad, load_ad_from_dict, load_ad_from_json, load_builtin_ad
from .monitor import IdleMonitor

__all__ = ["init", "load_ad", "show_now", "stop"]

_controller_lock = threading.Lock()
_monitor: IdleMonitor | None = None
_current_ad: Ad = load_builtin_ad()
_current_idle_seconds: float = 30.0


def init(idle_seconds: float = 30) -> None:
    """Initialize (or reconfigure) termad idle monitoring."""
    global _monitor, _current_idle_seconds

    if idle_seconds <= 0:
        raise ValueError("idle_seconds must be greater than 0.")

    _current_idle_seconds = float(idle_seconds)

    with _controller_lock:
        monitor = _monitor
        if monitor is None:
            monitor = IdleMonitor(idle_seconds=_current_idle_seconds, ad=_current_ad)
            _monitor = monitor
        else:
            monitor.set_idle_seconds(_current_idle_seconds)
            monitor.set_ad(_current_ad)
            monitor.mark_activity()

    monitor.start()


def load_ad(source: str | dict[str, Any]) -> None:
    """Load a custom ad from JSON path or dict schema."""
    global _current_ad

    ad: Ad
    if isinstance(source, dict):
        ad = load_ad_from_dict(source)
    elif isinstance(source, (str, Path)):
        ad = load_ad_from_json(source)
    else:
        raise ValueError("source must be a dict or a JSON file path.")

    with _controller_lock:
        _current_ad = ad
        if _monitor is not None:
            _monitor.set_ad(ad)


def show_now() -> None:
    """Trigger ad rendering immediately."""
    with _controller_lock:
        monitor = _monitor

    if monitor is None:
        init(idle_seconds=_current_idle_seconds)
        with _controller_lock:
            monitor = _monitor

    if monitor is not None:
        monitor.show_now()


def stop() -> None:
    """Stop background monitoring and ad rendering."""
    global _monitor

    with _controller_lock:
        monitor = _monitor
        _monitor = None

    if monitor is not None:
        monitor.stop()
