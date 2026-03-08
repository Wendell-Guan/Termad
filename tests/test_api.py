from __future__ import annotations

import importlib

import pytest


class FakeMonitor:
    instances: list["FakeMonitor"] = []

    def __init__(self, *, idle_seconds: float, ad) -> None:
        self.idle_seconds = idle_seconds
        self.ad = ad
        self.start_calls = 0
        self.stop_calls = 0
        self.show_now_calls = 0
        self.mark_activity_calls = 0
        self.set_idle_seconds_calls: list[float] = []
        self.set_ad_calls: list = []
        FakeMonitor.instances.append(self)

    def start(self) -> None:
        self.start_calls += 1

    def stop(self) -> None:
        self.stop_calls += 1

    def show_now(self) -> None:
        self.show_now_calls += 1

    def mark_activity(self) -> None:
        self.mark_activity_calls += 1

    def set_idle_seconds(self, idle_seconds: float) -> None:
        self.set_idle_seconds_calls.append(idle_seconds)

    def set_ad(self, ad) -> None:
        self.set_ad_calls.append(ad)


@pytest.fixture
def termad_module():
    import termad

    mod = importlib.reload(termad)
    yield mod
    mod.stop()


def sample_ad_payload() -> dict:
    return {
        "frames": ["AA\nBB"],
        "frame_rate": 2,
        "duration": 3,
        "metadata": {
            "advertiser": "ACME",
            "url": "https://example.com",
        },
    }


def test_init_idempotent(monkeypatch, termad_module) -> None:
    FakeMonitor.instances.clear()
    monkeypatch.setattr(termad_module, "IdleMonitor", FakeMonitor)

    termad_module.init(idle_seconds=10)
    assert len(FakeMonitor.instances) == 1

    monitor = FakeMonitor.instances[0]
    assert monitor.start_calls == 1

    termad_module.init(idle_seconds=12)
    assert len(FakeMonitor.instances) == 1
    assert monitor.start_calls == 2
    assert monitor.set_idle_seconds_calls == [12.0]
    assert monitor.mark_activity_calls == 1


def test_load_ad_updates_running_monitor(monkeypatch, termad_module) -> None:
    FakeMonitor.instances.clear()
    monkeypatch.setattr(termad_module, "IdleMonitor", FakeMonitor)

    termad_module.init(idle_seconds=10)
    monitor = FakeMonitor.instances[0]

    termad_module.load_ad(sample_ad_payload())
    assert monitor.set_ad_calls
    assert monitor.set_ad_calls[-1].metadata["advertiser"] == "ACME"


def test_load_ad_rejects_bad_source(termad_module) -> None:
    with pytest.raises(ValueError, match="dict or a JSON"):
        termad_module.load_ad(123)


def test_show_now_without_init(monkeypatch, termad_module) -> None:
    FakeMonitor.instances.clear()
    monkeypatch.setattr(termad_module, "IdleMonitor", FakeMonitor)

    termad_module.show_now()

    assert len(FakeMonitor.instances) == 1
    monitor = FakeMonitor.instances[0]
    assert monitor.start_calls == 1
    assert monitor.show_now_calls == 1


def test_stop_is_safe_to_call_multiple_times(monkeypatch, termad_module) -> None:
    FakeMonitor.instances.clear()
    monkeypatch.setattr(termad_module, "IdleMonitor", FakeMonitor)

    termad_module.init(idle_seconds=10)
    monitor = FakeMonitor.instances[0]

    termad_module.stop()
    termad_module.stop()

    assert monitor.stop_calls == 1
