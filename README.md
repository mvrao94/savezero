# SaveZero

### Bulk-delete your Instagram saved posts in minutes.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Selenium](https://img.shields.io/badge/Selenium-4.15+-green.svg)](https://www.selenium.dev/)

---

## The Problem

Have **thousands of saved Instagram posts** you'll never look at again?

Instagram gives you no good way to bulk-delete them. You'd have to click "Unsave" thousands of times manually.

## The Solution

**SaveZero** automates the cleanup locally through your Chrome session. It works with your existing login, automatically resumes after crashes, and **never asks for your Instagram password**.

### Why SaveZero?

- ✅ **Actually fast**: Clear 2,000+ saved posts without clicking Unsave thousands of times
- ✅ **Completely local**: Runs on your machine using your Chrome profile
- ✅ **Zero credentials stored**: You log in once through Chrome, SaveZero reuses that session
- ✅ **Self-healing**: Automatically recovers from browser crashes or connection drops
- ✅ **Built-in safety**: Paces requests and stops when common action-block signals are detected

> **Important**: SaveZero is designed to pace requests and halt on known action-block signals, but this **does not guarantee** that Instagram won't restrict an account. Use at your own discretion.

---

## Demo

<!-- TODO: Add 15-30 second GIF showing:
     - Instagram → 2,847 saved posts
     - SaveZero running
     - Automatic cleanup
     - 0 saved posts
     - Terminal output
-->

_Demo GIF coming soon!_

---

## How It Works

**SaveZero** offers two modes:

1. **Fast In-Browser API Mode (Default)**: Direct asynchronous fetch calls from your authenticated browser session — clears posts with minimal overhead
2. **Visual UI Mode**: Full browser automation with DOM traversal and simulated clicks

Both modes include:
- **Tiered cooldowns**: Micro-breathers every 40 posts, 15-min rest every 1,000 posts, 1-hour rest every 2,000 posts
- **Self-healing recovery**: Handles dropped Chrome connections, system sleep, or renderer crashes
- **Dynamic selector resolution**: Works around Instagram's obfuscated CSS classes using relative XPaths and ARIA attributes

---

## Quickstart

### Prerequisites

- **Python 3.8+** installed
- **Google Chrome** installed

### Installation

### 1. Clone the Repository
```bash
git clone https://github.com/mvrao94/savezero.git
cd savezero
```

### 2. Optional Manual Installation
```bash
python -m pip install .
```
The launchers can also create a project-local `.venv` and install missing dependencies automatically.

### 3. Optional Configuration
Command-line arguments are sufficient for normal package usage; no `.env` file is required:
```bash
savezero --username your_instagram_username --mode api
```

To keep a username, mode, or runtime tuning values as defaults, copy the example environment file:
```bash
# On Linux / macOS:
cp .env.example .env

# On Windows (PowerShell):
copy .env.example .env
```

Open `.env` and set any desired defaults:
```env
INSTAGRAM_USERNAME=your_instagram_username
CLEANER_MODE=api
```

### 3. Run SaveZero

**On Windows:**
```powershell
.\run.bat --username your_instagram_username
```
You can also run `run.bat` without arguments when `INSTAGRAM_USERNAME` is set in `.env`; otherwise it prompts for the username.
When `--mode` is omitted, the launcher uses the fast in-browser API mode by default. Add `--mode ui` to use visual browser clicks instead.

**On Linux / macOS:**
```bash
chmod +x run.sh
./run.sh --username your_instagram_username
```
You can also run `./run.sh` without arguments when `INSTAGRAM_USERNAME` is set in `.env`; otherwise it prompts for the username.
The launcher prefers a local `.venv`, creates one when possible, and installs missing dependencies. When using WSL or Git Bash on Windows without `python3-venv`, it can use a dependency-ready `python.exe` installation.

**Direct Python CLI:**
```bash
python cleaner.py --username your_instagram_username
```

**Installed CLI:**
```bash
savezero --username your_instagram_username
savezero --url "https://www.instagram.com/your_username/saved/all-posts/"
```

---

## Configuration

### CLI Options

The supported command-line options override corresponding `.env` defaults directly:

```bash
python cleaner.py --help
# or, after pip install .:
savezero --help

usage examples:
  python cleaner.py --username your_instagram_username
  run.bat --username your_instagram_username
  ./run.sh --username your_instagram_username
  savezero --username your_instagram_username
  savezero --url "https://www.instagram.com/your_username/saved/all-posts/"
  savezero --username your_instagram_username --mode ui

options:
  -h, --help            Show this help message and exit
  -u, --username USER   Instagram username to clear saved posts for
  -m, --mode {api,ui}   Clearing mode: 'api' (fast ~1.5s/post) or 'ui' (visual clicks)
  --url URL             Direct custom URL for a specific saved collection

If `--mode` is omitted, API mode is selected by default. API mode is the fast mode; use `--mode ui` only when visual browser interaction is needed.

The `run.bat` and `run.sh` launchers automatically create a project environment and install missing dependencies. Direct Python execution requires the project to be installed first.
```

### Environment Variables (`.env`)

For persistent configuration, copy `.env.example` to `.env` and customize:

| Variable | Default | Description |
| :--- | :--- | :--- |
| `INSTAGRAM_USERNAME` | *(Optional)* | Default username; `--username` takes precedence |
| `TARGET_SAVED_URL` | `https://www.instagram.com/{user}/saved/all-posts/` | Custom collection URL override |
| `CLEANER_MODE` | `api` | Default mode; `--mode` takes precedence |
| `API_MIN_DELAY` | `1.2` | Minimum seconds between API unsaves |
| `API_MAX_DELAY` | `2.0` | Maximum seconds between API unsaves |
| `BATCH_SIZE_BEFORE_PAUSE` | `40` | Posts cleared before taking a quick micro-rest |
| `BATCH_PAUSE_MIN` | `30.0` | Minimum micro-rest duration (seconds) |
| `BATCH_PAUSE_MAX` | `60.0` | Maximum micro-rest duration (seconds) |
| `PAUSE_EVERY_1000_MINUTES` | `15` | Minutes to rest after every 1,000 posts |
| `PAUSE_EVERY_2000_MINUTES` | `60` | Minutes to rest after every 2,000 posts (1 hour) |
| `CHROME_USER_DATA_DIR` | `~/.savezero_session` | Dedicated Chrome session directory |

---

## How Authentication Works

1. On the first run, the script opens a dedicated Google Chrome automation window and pauses at an **Authentication Gate**.
2. Log into your Instagram account and complete 2FA in that browser window.
3. The script automatically detects successful authentication, saves session cookies to `~/.savezero_session`, and begins clearing.
4. **All future runs will automatically reuse this session without prompting for login again.**

---

## Safety & Rate Limiting

**Important considerations:**

- **Private action**: Unsaving posts is a private action on your own library and does not trigger public spam flags
- **Velocity limits**: Instagram enforces hourly action velocity limits; SaveZero's built-in pauses help pace requests
- **Auto-halt protection**: API mode stops on `429` responses or `"checkpoint_required"` signals; both modes scan for known action-block indicators
- **Not foolproof**: Detection is not comprehensive — use at your own discretion

**SaveZero is designed to pace requests and stop when common action-block signals are detected. This does not guarantee that Instagram won't restrict an account.**

---

## Technical Architecture

<details>
<summary>Click to expand technical details</summary>

### Dynamic Selector Resolution
Bypasses fragile, obfuscated CSS classes by utilizing relative XPaths, semantic ARIA attributes, and self-healing selector priority caching.

### Dual Execution Engines
- **In-Browser API Mode (Default)**: Direct asynchronous fetch calls from the active authenticated browser session (~1.5s/post, ~2,000+ posts/hour).
- **Visual UI Mode**: Full DOM traversal, modal lifecycle validation, and simulated clicks.

### Tiered Milestone Throttling
- Micro-breathers: Randomized 30s to 60s pauses every 40 posts.
- Hourly rest: 15-minute cooldown every 1,000 posts.
- Multi-hour rest: 1-hour cooldown every 2,000 posts.

### Self-Healing Browser Recovery
Automatically catches dropped DevTools connections, system sleep interruptions, or renderer crashes, relaunching Chrome and seamlessly resuming without losing progress.

</details>

---

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## Roadmap

- [ ] Add comprehensive test suite
- [ ] Create demo GIF/video
- [ ] PyPI package distribution
- [ ] Support for multiple Instagram accounts
- [ ] Progress export/import for long-running sessions
- [ ] Collection-specific clearing (not just "All Posts")

---

## Security

See [SECURITY.md](SECURITY.md) for security policy and vulnerability reporting.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Legal & Trademark Disclaimer

SaveZero is an independent open-source project and is not affiliated with, sponsored by, or endorsed by Meta Platforms, Inc. or Instagram. "Instagram", "Insta", and "Meta" are registered trademarks of Meta Platforms, Inc.

**This tool is intended for personal data management and fair-use collection hygiene. Use responsibly in accordance with Instagram's Terms of Service.**
