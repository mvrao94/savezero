# SaveZero 🚀

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Selenium](https://img.shields.io/badge/Selenium-4.15+-green.svg)](https://www.selenium.dev/)

**SaveZero** is a self-healing Python automation tool designed to help manage large Instagram saved collections while pacing requests and stopping when common action-block signals are detected. It cannot guarantee that Instagram will not restrict an account.

---

## ✨ Features

- ⚡ **Dual Execution Modes**:
  - **Fast In-Browser API Mode (Default)**: Executes asynchronous unsave calls directly via your authenticated browser session (`~1.5s per post`, clearing **~2,000+ posts/hour** without UI rendering lags).
  - **Visual UI Mode**: Traverses the grid, inspects modal states, and simulates organic mouse clicks.
- 🛡️ **Tiered Milestone Cooldowns**:
  - Micro-breathers (randomized 30s to 60s every 40 posts) to reduce request bursts.
  - **15-minute rest every 1,000 posts** to cool down hourly activity.
  - **1-hour rest every 2,000 posts** to reset multi-hour account action limits.
- 🔄 **Self-Healing Session Recovery**:
  - Automatically handles dropped Chrome DevTools connections, system sleep, or browser crashes by cleanly reattaching and resuming from where it left off.
- 🎯 **Dynamic Selector Resolution**:
  - Decoupled from fragile, obfuscated CSS classes (e.g. `._aagw`); relies on relative XPaths, semantic ARIA labels, and mathematical Base64 media-ID decoding.
- 🔒 **Zero Credentials Stored**:
  - Never asks for your Instagram password. Authentication is performed directly by you inside a local, dedicated Chrome profile (`~/.savezero_session`).

---

## 📋 Prerequisites

- **Python 3.8+** installed.
- **Google Chrome** installed.

---

## 🚀 Quickstart

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

### 4. Run the Script

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

## 🛠️ CLI Options

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

---

## ⚙️ Environment Variables (`.env`)

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

## 🔐 How Authentication Works

1. On the first run, the script opens a dedicated Google Chrome automation window and pauses at an **Authentication Gate**.
2. Log into your Instagram account and complete 2FA in that browser window.
3. The script automatically detects successful authentication, saves session cookies to `~/.savezero_session`, and begins clearing.
4. **All future runs will automatically reuse this session without prompting for login again.**

---

## 🛡️ Rate-Limiting & Safety Recommendations

- **Private Action Safety**: Unsaving posts is a private action on your own library and does not trigger public spam flags.
- **Velocity Management**: Instagram enforces hourly action velocity limits. The built-in milestone pauses are pacing measures, not a guarantee that temporary action blocks will be avoided.
- **Auto-Halt Protection**: API mode halts on a `429` response or an API response containing `"checkpoint_required"`. Both modes also scan for a set of known action-block indicators, but detection is not comprehensive.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## ⚠️ Legal & Trademark Disclaimer
SaveZero is an independent open-source project and is not affiliated with, sponsored by, or endorsed by Meta Platforms, Inc. or Instagram. "Instagram", "Insta", and "Meta" are registered trademarks of Meta Platforms, Inc. This tool is intended for personal data management and fair-use collection hygiene. Use responsibly in accordance with platform terms.
