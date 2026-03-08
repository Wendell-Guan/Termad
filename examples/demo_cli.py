#!/usr/bin/env python3
"""Demo CLI for termad: a fake dependency vulnerability scanner."""

from __future__ import annotations

import argparse
from collections import deque
from datetime import datetime
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

LOG_MESSAGES = [
    "Resolving dependency graph for workspace packages...",
    "Fetching CVE feed delta from advisory mirror us-west-2...",
    "Correlating transitive package fingerprints against SBOM...",
    "Validating lockfile integrity against supply-chain policy...",
    "Inspecting post-install scripts for privilege escalation patterns...",
    "Comparing package signatures against trusted publisher set...",
    "Evaluating semver drift against approved baseline manifests...",
    "Scanning native extension bundles for suspicious exports...",
    "Checking licenses and legal policy constraints for production use...",
    "Mapping reachable vulnerable code paths using static call graph...",
    "Matching suspicious dependency updates against known typo-squat list...",
    "Computing exploitability score using execution context heuristics...",
]

PACKAGES = [
    "urllib3",
    "requests",
    "pyyaml",
    "jinja2",
    "cryptography",
    "pydantic",
    "sqlalchemy",
    "numpy",
    "aiohttp",
    "pillow",
    "gunicorn",
    "django",
]

SEVERITIES = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="dep-audit demo for termad")
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run a short demo loop for local smoke checks.",
    )
    return parser.parse_args()


def timestamp() -> str:
    return datetime.now().strftime("%H:%M:%S")


def progress_bar(width: int, ratio: float) -> str:
    filled = int(width * ratio)
    return "[" + "#" * filled + "-" * (width - filled) + "]"


def print_header() -> None:
    print("dep-audit Enterprise Dependency Security Scanner v4.7.2")
    print("Policy Profile: production-strict / SOC2 / PCI")
    print("Target: ./  (python, node, and mixed lockfile detection)")
    print()


def run_scan(*, total_seconds: float) -> None:
    total_steps = 120
    step_sleep = total_seconds / total_steps
    recent_logs: deque[str] = deque(maxlen=8)

    for step in range(total_steps + 1):
        ratio = step / total_steps
        bar = progress_bar(width=38, ratio=ratio)
        speed = random.randint(160, 360)
        sys.stdout.write(f"\rScanning dependencies {bar} {ratio * 100:6.2f}%  {speed} pkg/s")
        sys.stdout.flush()

        if step > 0 and step % 5 == 0:
            sys.stdout.write("\n")
            message = LOG_MESSAGES[(step // 5 - 1) % len(LOG_MESSAGES)]
            recent_logs.append(f"[{timestamp()}] INFO  {message}")
            print(recent_logs[-1])

            package = random.choice(PACKAGES)
            severity = random.choice(SEVERITIES)
            cve = f"CVE-202{random.randint(1, 5)}-{random.randint(1000, 9999)}"
            print(
                f"[{timestamp()}] TRACE Candidate finding queued: {package:<12} {severity:<8} {cve}"
            )

        time.sleep(step_sleep)

    print("\n")


def print_report(*, pace: float) -> None:
    report_lines = [
        "Scan complete. Building remediation report...",
        "",
        "Summary",
        "  Dependencies analyzed:            1,184",
        "  Vulnerabilities detected:         27",
        "  Reachable vulnerabilities:         6",
        "  Policy violations (critical):      2",
        "",
        "Top actionable findings",
        "  1) CRITICAL  CVE-2024-4872  pyyaml<6.0.3    upgrade to >=6.0.3",
        "  2) HIGH      CVE-2025-1029  aiohttp<3.11    upgrade to >=3.11.2",
        "  3) HIGH      CVE-2023-9164  pillow<10.5     pin to 10.5.1",
        "",
        "Recommendation: block release until critical findings are remediated.",
    ]

    for line in report_lines:
        print(line)
        time.sleep(pace)


def main() -> int:
    args = parse_args()

    ad_path = Path(__file__).resolve().parents[1] / "termad" / "termad" / "assets" / "dvd_ad.json"

    termad.init(idle_seconds=10)
    termad.load_ad(str(ad_path))

    try:
        print_header()
        run_scan(total_seconds=7.0 if args.quick else 24.0)
        print_report(pace=0.03 if args.quick else 0.22)

        # Re-arm the monitor right before waiting for user acknowledgement.
        termad.init(idle_seconds=10)

        print()
        print("Awaiting analyst acknowledgement. Press Enter to exit.")
        print("If you pause here for ~10 seconds, termad will present an idle sponsor screen.")
        input("> ")
        print("Session closed.")
        return 0
    finally:
        termad.stop()


if __name__ == "__main__":
    raise SystemExit(main())
