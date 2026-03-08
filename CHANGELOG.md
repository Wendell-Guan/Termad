# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.0a1] - 2026-03-07

### Added
- Initial public alpha for `termad` idle ASCII ad SDK on macOS terminals.
- Public API: `init`, `load_ad`, `show_now`, `stop`.
- Built-in DVD-style ad and campaign demo ad assets.
- Demo CLIs: `demo_cli.py`, `demo_claude_code.py`, `demo_open_claw.py`.
- Basic CI, tests, packaging, and release validation workflow.

### Notes
- This is an alpha release. API and behavior may change in future versions.
- Cross-platform behavior is not guaranteed yet; macOS TTY workflows are the target.
