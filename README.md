# termad

**Idle-time ASCII ads for CLI apps, rendered directly in the terminal and dismissed on any keypress.**

<div align="center">
  <img src="./assets/readme/campaign-mcd.gif" alt="termad demo in terminal" width="880" />
</div>

## Problem -> Solution (First Screen)

- **Problem:** CLI apps have dead time (long scans, waiting prompts, paused sessions) that is hard to monetize or sponsor without opening browsers/popups.
- **Solution:** `termad` watches terminal idle time and plays campaign animations in the same TTY using ANSI frames.
- **User safety:** any keypress dismisses the ad immediately and restores terminal state.

## Install + Demo (3 Commands)

```bash
git clone https://github.com/Wendell-Guan/Termad.git
cd Termad && python -m pip install -e '.[dev]'
python examples/demo_open_claw.py --quick
```

Package-only install:

```bash
pip install termad
```

## 2-Minute Quickstart

1. Install `termad` (`pip install termad`).
2. Add one `init(...)` call in your CLI app startup.
3. Optionally load a custom JSON ad and test with `show_now()`.

```python
import termad

# Start idle monitor (idempotent)
termad.init(idle_seconds=30)

# Optional: use your own campaign asset
termad.load_ad("path/to/ad.json")

# Optional: force preview during development
termad.show_now()

# On shutdown
termad.stop()
```

## Use Cases

- **Open-source CLI maintainers:** add sponsor slots to cover hosting/maintenance costs.
- **Devtool companies:** run product-awareness campaigns in real coding environments.
- **Community projects/events:** ship seasonal or community messages as lightweight terminal creatives.
- **Internal platform teams:** display approved internal notices in custom enterprise CLIs.

## Campaign Showcase

<table>
  <tr>
    <td width="33%">
      <img src="./assets/readme/campaign-mcd.gif" alt="McDonald's campaign in terminal shell (animated)" />
      <br />
      <b>McDonald's Midnight Fuel</b>
      <br />
      Asset: <code>termad/assets/mcd_night_ad.json</code>
    </td>
    <td width="33%">
      <img src="./assets/readme/campaign-lobster.gif" alt="Open Claw lobster campaign in terminal shell (animated)" />
      <br />
      <b>Open Claw Lobster Persona</b>
      <br />
      Asset: <code>termad/assets/open_claw_macmini_ad.json</code>
    </td>
    <td width="33%">
      <img src="./assets/readme/campaign-macmini.gif" alt="Mac mini sponsorship campaign in terminal shell (animated)" />
      <br />
      <b>Mac mini Precision Sponsor</b>
      <br />
      Asset: <code>termad/assets/open_claw_macmini_ad.json</code>
    </td>
  </tr>
</table>

## FAQ

### Who is this for?

`termad` is for people who own CLI attention surfaces: maintainers of terminal tools, platform teams, and sponsors who want terminal-native distribution.

### What are alternatives?

- No monetization/sponsorship at all (simplest path).
- Static banner text inside command output.
- Web-based ads outside the terminal.

`termad` is useful when you want richer visuals while staying inside a TTY workflow.

### What are current limitations?

- Primary target: macOS terminal environments.
- Best in interactive TTY sessions (Terminal.app / iTerm2).
- If `stdin`/`stdout` are not TTYs, `termad` safely no-ops.
- This is still alpha; API/runtime details may evolve.

## Public API

```python
import termad

termad.init(idle_seconds=30)
termad.load_ad("path/to/ad.json")  # or pass a dict
termad.show_now()                   # dev preview
termad.stop()                       # safe to call repeatedly
```

API notes:

- `init(idle_seconds=30)` is idempotent.
- Re-calling `init(...)` updates config and refreshes idle timer.
- `load_ad(...)` accepts JSON path (`str`) or in-memory `dict`.

## Ad Format

```json
{
  "frames": [
    "line 1\nline 2"
  ],
  "frame_rate": 12,
  "duration": 10,
  "metadata": {
    "advertiser": "ACME",
    "url": "https://example.com"
  }
}
```

Required fields:

- `frames`: list of multi-line ASCII strings
- `frame_rate`: frames per second (`> 0`)
- `duration`: max display seconds before auto-dismiss (`> 0`)
- `metadata.advertiser`: string
- `metadata.url`: string

## Demo Commands

```bash
# Core idle behavior (DVD-style)
python examples/demo_cli.py

# Claude Code style session + campaign
python examples/demo_claude_code.py

# Open Claw style session + campaign
python examples/demo_open_claw.py
```

Quick smoke variants:

```bash
python examples/demo_cli.py --quick
python examples/demo_claude_code.py --quick
python examples/demo_open_claw.py --quick
```

## Release Notes Structure

This repo follows:

- `CHANGELOG.md` with Keep a Changelog format.
- `.github/release.yml` categories for generated GitHub release notes.

## Roadmap

### V1: Terminal ads for humans

Deliver stable terminal-native campaign playback and sponsor-ready creative tooling.

### V2: Agent-facing sponsored discovery

Move from visual creatives to machine-readable sponsored capability listings for agents.

### V3: Open protocol for agent distribution

Evolve into a transparent, auditable ad/discovery protocol for agent-native software ecosystems.

## Contributing

- Read [CONTRIBUTING.md](./CONTRIBUTING.md).
- For sponsorship ideas, open an issue with title format: `[Sponsorship] Brand Name - Campaign Idea`.
- Include target audience, campaign message, landing URL, and expected run window.

## Project Structure

```text
termad/
├── termad/
│   ├── __init__.py
│   ├── monitor.py
│   ├── renderer.py
│   ├── ad.py
│   └── assets/
│       ├── dvd_ad.json
│       ├── mcd_night_ad.json
│       └── open_claw_macmini_ad.json
├── examples/
│   ├── demo_cli.py
│   ├── demo_claude_code.py
│   └── demo_open_claw.py
├── tests/
├── .github/workflows/ci.yml
├── LICENSE
├── CHANGELOG.md
├── CONTRIBUTING.md
├── README.md
└── pyproject.toml
```

## License

[MIT](./LICENSE)
