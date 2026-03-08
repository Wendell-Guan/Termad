#!/usr/bin/env python3
"""Open Claw style terminal demo with Mac mini campaign ad."""

from __future__ import annotations

import argparse
from datetime import datetime
import itertools
from pathlib import Path
import random
import sys
import time


def _import_termad():
    try:
        import termad  # type: ignore

        return termad
    except ImportError:
        repo_root = Path(__file__).resolve().parents[1]
        sys.path.insert(0, str(repo_root / "termad"))
        import termad  # type: ignore

        return termad


termad = _import_termad()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Open Claw demo for termad")
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Short run for smoke checks.",
    )
    return parser.parse_args()


def now() -> str:
    return datetime.now().strftime("%H:%M:%S")


def emit(line: str = "", delay: float = 0.0) -> None:
    print(line)
    if delay > 0:
        time.sleep(delay)


def type_cmd(command: str, char_delay: float) -> None:
    sys.stdout.write("$ ")
    sys.stdout.flush()
    for ch in command:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(char_delay)
    sys.stdout.write("\n")
    sys.stdout.flush()


def spinner(label: str, duration: float, interval: float = 0.08) -> None:
    wheel = itertools.cycle("⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏")
    end = time.monotonic() + duration
    while time.monotonic() < end:
        sys.stdout.write(f"\r{label} {next(wheel)}")
        sys.stdout.flush()
        time.sleep(interval)
    sys.stdout.write("\r" + " " * (len(label) + 6) + "\r")
    sys.stdout.flush()


def print_header(pause: float) -> None:
    emit("╭──────────────────────────────────────────────────────────────╮")
    emit("│                    Open Claw (simulated)                    │")
    emit("├──────────────────────────────────────────────────────────────┤")
    emit("│ workspace: /Users/dev/open-claw/edge-ingest                 │")
    emit("│ profile: midnight-release                                   │")
    emit("│ target: macOS-arm64 build matrix                            │")
    emit("╰──────────────────────────────────────────────────────────────╯")
    emit("", delay=pause)


def run_session(*, quick: bool) -> None:
    cmd_delay = 0.01 if quick else 0.052
    line_delay = 0.015 if quick else 0.34
    think_time = 1.2 if quick else 8.6

    type_cmd("openclaw run --profile midnight --optimize=latency", cmd_delay)
    spinner("Open Claw planning pipeline", think_time)

    log_lines = [
        "Agent > Reading telemetry windows from production shards.",
        "Agent > Proposing cache-aware task graph for Mac mini dev kits.",
        "Agent > Executing patchset in safe order.",
        "",
        f"[{now()}] tool.exec  rg --files src/",
        f"[{now()}] tool.exec  pytest tests/test_scheduler.py -q",
    ]

    for line in log_lines:
        emit(line, delay=line_delay)

    tests = [
        "tests/test_scheduler.py::test_task_priority PASSED",
        "tests/test_scheduler.py::test_retry_budget PASSED",
        "tests/test_scheduler.py::test_deadline_backpressure PASSED",
        "tests/test_scheduler.py::test_idle_mode PASSED",
    ]

    for t in tests:
        step = random.uniform(0.12, 0.20) if quick else random.uniform(0.72, 1.44)
        spinner(f"Running {t.split('::')[-1].split()[0]}", step, interval=0.05)
        emit(t, delay=line_delay)

    emit("", delay=line_delay)
    emit("Agent > Optimization complete. Baseline improved by 18.4%.", delay=line_delay)
    emit("Agent > Suggestion: keep this Mac mini profile for nightly builds.", delay=line_delay)


def wait_for_idle() -> None:
    emit("")
    emit("Open Claw monitor is now idle.")
    emit("Pause ~10s to view the full sponsor sequence.")
    emit("Press Enter to close session.")
    input("> ")


def main() -> int:
    args = parse_args()
    ad_path = (
        Path(__file__).resolve().parents[1]
        / "termad"
        / "termad"
        / "assets"
        / "open_claw_macmini_ad.json"
    )

    termad.init(idle_seconds=10)
    termad.load_ad(str(ad_path))

    try:
        print_header(pause=0.03 if args.quick else 0.30)
        run_session(quick=args.quick)

        # Re-arm timer right before waiting for user input.
        termad.init(idle_seconds=10)
        wait_for_idle()

        emit("Session closed.")
        return 0
    finally:
        termad.stop()


if __name__ == "__main__":
    raise SystemExit(main())
