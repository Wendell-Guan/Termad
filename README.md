![termad banner](./cp_image_1772996928140.png)

# termad

<p align="center">
  <b>From Terminal Ads to Agent Ad Protocol</b><br/>
  <i>Phase 1 wins attention. Phase 2 defines the standard.</i>
</p>

<p align="center">
  <a href="#roadmap">Roadmap</a>
  ·
  <a href="#campaign-showcase">Campaign Showcase</a>
  ·
  <a href="#sponsorship">Sponsorship</a>
  ·
  <a href="#install">Install</a>
  ·
  <a href="#public-api">API</a>
  ·
  <a href="#demo-cli">Demo</a>
</p>

**Status:** Alpha (`v0.1.0-alpha.1`, package version `0.1.0a1`)

> "Every media shift creates a new ad protocol.
> Agent-native software needs an Agent-native ad protocol."

`termad` started as an idle-time ad runtime for terminal apps.
It now has a bigger mission: evolve into the open protocol layer for Agent-era sponsorship and distribution.

Today: it plays ads in a real terminal shell without opening extra windows or hijacking normal I/O.
Next: it moves from creative-only assets to machine-readable sponsored capability offers for Agents.

## Roadmap

### Step 1 (v1): Human-visible terminal ads

Ship the original `termad` experience (including the DVD bounce ad) as a polished open-source package.

Goals:

- Build awareness for the name `termad`.
- Earn GitHub stars and developer mindshare.
- Prove that terminal-native ad experiences can be memorable without breaking UX.

### Step 2 (v2): Agent Ad Protocol

Evolve from "ads people watch" to "sponsored capability offers Agents can evaluate safely."

Planned direction:

- Define an open, machine-readable sponsorship schema.
- Add transparent sponsored markers and auditable decision logs.
- Support outcome-based attribution: considered -> selected -> successful task completion.
- Keep decision integrity: sponsors can buy discovery, not forced selection.

## Why this design works now

- Native terminal shell look: no browser tab, no popup window.
- Instant entry/exit: show on idle, dismiss on any keypress.
- Campaign-ready creative: logo -> product -> message -> CTA.
- Clear migration path from demo virality to protocol-level infrastructure.

## Campaign Showcase

<table>
  <tr>
    <td width="33%">
      <img src="./assets/readme/campaign-mcd.gif" alt="McDonald's campaign in terminal shell (animated)" />
      <br />
      <b>McDonald's Midnight Fuel</b>
      <br />
      Logo + fries + burger + late-night CTA, designed for coding-after-dark sessions.
      <br />
      Asset: <code>termad/assets/mcd_night_ad.json</code>
    </td>
    <td width="33%">
      <img src="./assets/readme/campaign-lobster.gif" alt="Open Claw lobster campaign in terminal shell (animated)" />
      <br />
      <b>Open Claw Lobster Persona</b>
      <br />
      Character-led brand identity sequence for memorable terminal presence.
      <br />
      Asset: <code>termad/assets/open_claw_macmini_ad.json</code>
    </td>
    <td width="33%">
      <img src="./assets/readme/campaign-macmini.gif" alt="Mac mini sponsorship campaign in terminal shell (animated)" />
      <br />
      <b>Mac mini Precision Sponsor</b>
      <br />
      Hardware sponsorship-style frame set focused on performance and quiet power.
      <br />
      Asset: <code>termad/assets/open_claw_macmini_ad.json</code>
    </td>
  </tr>
</table>

## Sponsorship

Want to run ads in developer terminals? You can sponsor a campaign with termad and distribute it through our ad-network style integration. We support campaign onboarding, creative integration, and multi-project ad distribution with revenue-share options.

### Available Sponsor Slots

| Slot | Format | Placement | Suitable For |
| --- | --- | --- | --- |
| Hero Idle Slot | 6-20s animated ASCII | Main idle trigger in demo and CLI waiting scenes | Consumer brands, food & beverage, lifestyle |
| Character Story Slot | Multi-frame mascot sequence | Persona-led campaign block | IP brands, games, community campaigns |
| Hardware Sponsor Slot | Product-focused storyboard | Performance/dev-tool themed scenes | Hardware, cloud infra, dev tooling |

### Contact

- GitHub: [@Wendell-Guan](https://github.com/Wendell-Guan)
- Open an issue with title: `[Sponsorship] Brand Name - Campaign Idea`
- Include: target audience, campaign message, landing URL, expected run window

## Demo Commands for Campaign Content

Run these to recreate the branded terminal-ad feeling:

```bash
# McDonald's sequence
python examples/demo_claude_code.py

# Lobster + Mac mini sequence
python examples/demo_open_claw.py

# Core engine behavior (DVD-style default ad)
python examples/demo_cli.py
```

## Support and Limitations

- Primary runtime target: macOS terminal environments.
- Best tested in interactive TTY sessions (Terminal.app / iTerm2).
- If `stdin`/`stdout` are not TTYs, `termad` intentionally runs in safe no-op mode.
- Alpha caveat: API and behavior may evolve while hardening the SDK.

## Install

```bash
pip install termad
```

For local development in this repo:

```bash
pip install -e '.[dev]'
```

## Public API

```python
import termad

# Minimal integration
termad.init(idle_seconds=30)

# Load a custom ad
termad.load_ad("path/to/ad.json")

# Manually trigger (for testing)
termad.show_now()

# Stop monitoring
termad.stop()
```

### API notes

- `init(idle_seconds=30)` is idempotent.
- Calling `init(...)` again updates configuration and refreshes the idle timer.
- `load_ad(...)` accepts either:
  - a JSON file path (`str`), or
  - an in-memory Python `dict`.
- `stop()` is safe to call multiple times.

## Ad Format

Ads must provide these fields:

- `frames`: list of multi-line ASCII strings
- `frame_rate`: frames per second (`> 0`)
- `duration`: max display seconds before auto-dismiss (`> 0`)
- `metadata`: object containing:
  - `advertiser` (string)
  - `url` (string)

Example:

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

Validation failures raise `ValueError` with explicit messages.

## Built-in Example Ad

Bundled at `termad/assets/dvd_ad.json`:

- Bouncing logo behavior (DVD-style diagonal motion).
- Edge collision on all four boundaries (velocity inversion by axis).
- Includes tagline:
  - `"This idle time brought to you by termad."`

Additional campaign example at `termad/assets/mcd_night_ad.json`:

- Multi-frame sponsor creative: logo -> fries -> burger -> late-night message.
- Designed for the Claude Code style demo.

Additional campaign example at `termad/assets/open_claw_macmini_ad.json`:

- High-fidelity storyboard creative with lobster-inspired ASCII frames.
- Mac mini-focused sponsor copy for late-night coding sessions.

## Rendering and Terminal Behavior

- Uses ANSI alternate screen buffer (`\x1b[?1049h` / `\x1b[?1049l`).
- Hides cursor during playback and restores it on exit.
- Clears frame background every tick to avoid ghosting.
- Handles `SIGWINCH` terminal resize gracefully.
- Minimum supported layout target: `80x24`.

If `stdin`/`stdout` are not TTYs, `termad` runs in safe no-op mode and prints a warning to stderr.

## Demo CLI

Run the fake `dep-audit` scanner:

```bash
python examples/demo_cli.py
```

Quick smoke mode:

```bash
python examples/demo_cli.py --quick
```

Demo flow:

1. Simulates a realistic dependency security scan with progress + logs.
2. Prints a vulnerability report.
3. Waits for user acknowledgement.
4. During idle wait, `termad` shows the bouncing logo ad.

This demo uses a 10-second idle trigger.
Default timing is tuned for asciinema-style recordings in the 60-90 second range.

## Claude Code Style Demo

Run a second demo that simulates a realistic Claude Code terminal session, then idles and triggers a multi-frame campaign ad (logo -> fries -> burger -> message):

```bash
python examples/demo_claude_code.py
```

Quick smoke mode:

```bash
python examples/demo_claude_code.py --quick
```

This demo uses:

- idle trigger: 10 seconds
- ad asset: `termad/assets/mcd_night_ad.json`

## Open Claw Style Demo

Run a third demo that simulates an `Open Claw` terminal workflow and triggers a high-fidelity Mac mini campaign ad:

```bash
python examples/demo_open_claw.py
```

Quick smoke mode:

```bash
python examples/demo_open_claw.py --quick
```

This demo uses:

- idle trigger: 10 seconds
- ad asset: `termad/assets/open_claw_macmini_ad.json`
- playback: ~26 seconds

## Release and Validation

One-command local release check:

```bash
python -m pip install -e '.[dev]' && pytest && python -m build && python -m twine check dist/*
```

Minimal manual acceptance checklist (real TTY):

1. Run `python examples/demo_open_claw.py`.
2. Wait ~10 seconds at the final prompt and confirm the ad starts.
3. Press any key or Enter and confirm terminal state restores correctly.
4. Run quick regressions:
   - `python examples/demo_cli.py --quick`
   - `python examples/demo_claude_code.py --quick`
   - `python examples/demo_open_claw.py --quick`

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
