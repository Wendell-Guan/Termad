#!/usr/bin/env python3
"""Claude Code style terminal demo for termad idle ad playback."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import itertools
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
    parser = argparse.ArgumentParser(description="Claude Code style demo for termad")
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Shorten animation timings for fast verification.",
    )
    return parser.parse_args()


def ts() -> str:
    return datetime.now().strftime("%H:%M:%S")


def slow_print(line: str = "", *, delay: float = 0.0) -> None:
    print(line)
    if delay > 0:
        time.sleep(delay)


def type_command(command: str, *, char_delay: float) -> None:
    sys.stdout.write("$ ")
    sys.stdout.flush()
    for ch in command:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(char_delay)
    sys.stdout.write("\n")
    sys.stdout.flush()


def spinner(label: str, *, duration: float, interval: float = 0.1) -> None:
    symbols = itertools.cycle("⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏")
    end = time.monotonic() + duration
    while time.monotonic() < end:
        sym = next(symbols)
        sys.stdout.write(f"\r{label} {sym}")
        sys.stdout.flush()
        time.sleep(interval)
    sys.stdout.write("\r" + " " * (len(label) + 6) + "\r")
    sys.stdout.flush()


def show_header(*, pause: float) -> None:
    slow_print("╭──────────────────────────────────────────────────────────────╮")
    slow_print("│                    Claude Code (simulated)                  │")
    slow_print("├──────────────────────────────────────────────────────────────┤")
    slow_print("│ workspace: /Users/dev/project/fizzbuzz-enterprise           │")
    slow_print("│ branch: feature/rules-engine                                │")
    slow_print("│ model: claude-sonnet-4                                      │")
    slow_print("╰──────────────────────────────────────────────────────────────╯")
    slow_print("", delay=pause)


def show_context(*, line_delay: float) -> None:
    lines = [
        "You can also write a more compact version using Python's string concatenation approach,",
        "which scales better if you ever want to add more rules (like 'Jazz' for multiples of 7).",
        "",
        "def fizzbuzz_flexible(n):",
        "    for i in range(1, n + 1):",
        "        result = ''",
        "        if i % 3 == 0:",
        "            result += 'Fizz'",
        "        if i % 5 == 0:",
        "            result += 'Buzz'",
        "        print(result or i)",
        "",
        "Write the enterprise version. Make no mistakes.",
    ]
    for line in lines:
        slow_print(line, delay=line_delay)


def run_simulated_turn(*, args: argparse.Namespace) -> None:
    char_delay = 0.010 if args.quick else 0.045
    line_delay = 0.015 if args.quick else 0.32
    think_delay = 1.2 if args.quick else 8.5

    type_command(
        "claude --dangerously-skip-permissions \"Refactor fizzbuzz with pluggable rules\"",
        char_delay=char_delay,
    )

    spinner("Thinking", duration=think_delay)

    assistant_lines = [
        "Assistant  > I will update src/fizzbuzz.py and run tests.",
        "Assistant  > Applying patch...",
        "",
        "diff --git a/src/fizzbuzz.py b/src/fizzbuzz.py",
        "@@ -1,8 +1,18 @@",
        "+RULES = [(3, 'Fizz'), (5, 'Buzz')]",
        "+",
        "+def render_token(value: int, rules=RULES) -> str:",
        "+    token = ''.join(word for divisor, word in rules if value % divisor == 0)",
        "+    return token or str(value)",
        " ",
        " def fizzbuzz(n: int):",
        "     for i in range(1, n + 1):",
        "-        if i % 15 == 0:",
        "-            print('FizzBuzz')",
        "-        elif i % 3 == 0:",
        "-            print('Fizz')",
        "-        elif i % 5 == 0:",
        "-            print('Buzz')",
        "-        else:",
        "-            print(i)",
        "+        print(render_token(i))",
        "",
        f"[{ts()}] tool.run  pytest -q",
    ]

    for line in assistant_lines:
        slow_print(line, delay=line_delay)

    test_steps = [
        "tests/test_fizzbuzz.py::test_fizz PASSED",
        "tests/test_fizzbuzz.py::test_buzz PASSED",
        "tests/test_fizzbuzz.py::test_fizzbuzz PASSED",
        "tests/test_fizzbuzz.py::test_default_number PASSED",
    ]

    for step in test_steps:
        spin = random.uniform(0.10, 0.20) if args.quick else random.uniform(0.60, 1.00)
        spinner(f"Running {step.split('::')[-1].split()[0]}", duration=spin, interval=0.05)
        slow_print(step, delay=line_delay)

    slow_print("", delay=line_delay)
    slow_print("Assistant  > Done. Refactor complete and tests passed.", delay=line_delay)
    slow_print("Assistant  > Tip: create reusable prompts in .claude/skills/ for repeated tasks.", delay=line_delay)


def wait_for_idle_trigger() -> None:
    slow_print("")
    slow_print("Tinkering...")
    slow_print("  Tip: Create skills by adding .md files to .claude/skills/ in your project")
    slow_print("  or ~/.claude/skills/ for skills that work in any project")
    slow_print("")
    slow_print("Press Enter to end this session.")
    slow_print("Pause here for ~10 seconds to let termad show the idle sponsor animation.")
    input("> ")


def main() -> int:
    args = parse_args()

    ad_path = Path(__file__).resolve().parents[1] / "termad" / "termad" / "assets" / "mcd_night_ad.json"

    termad.init(idle_seconds=10)
    termad.load_ad(str(ad_path))

    try:
        show_header(pause=0.02 if args.quick else 0.25)
        show_context(line_delay=0.015 if args.quick else 0.22)
        slow_print("")
        run_simulated_turn(args=args)

        # Re-arm right before the final idle phase so trigger timing is predictable.
        termad.init(idle_seconds=10)

        wait_for_idle_trigger()
        slow_print("Session ended.")
        return 0
    finally:
        termad.stop()


if __name__ == "__main__":
    raise SystemExit(main())
