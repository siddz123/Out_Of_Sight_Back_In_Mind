# FocusGhost

A minimal macOS menu bar app that beats "out of sight, out of mind" and crushes completion dopamine.

Set a focus goal, and FocusGhost lives in your menu bar watching what app and browser tab you're actually on. Drift onto Discord, YouTube, Reddit, or a Terminal procrastination session for five minutes straight and the title pulses red in your peripheral vision. Snap back to work and it goes green instantly. Mark the task complete and you get a chime, a banner, and a clean slate.

## Features

- **Always-visible focus goal** in the menu bar (`🟢 ship the demo`)
- **Distraction detection** for both native apps and browser tabs
  - Native apps: Discord, Spotify, Terminal, Twitter, Facebook
  - Browser domains (Chrome / Safari / Arc / Brave): youtube.com, x.com, twitter.com, reddit.com, instagram.com, tiktok.com, facebook.com, netflix.com
- **Peripheral-vision warning**: after 5 consecutive minutes on a distraction, the title flashes red (`⚠️ ship the demo`) every 0.7 seconds
- **Instant recovery**: the moment you switch back to a productive app, the title resets to green
- **Completion dopamine hump**: marking a task done plays the macOS Glass chime, fires a "Task Smashed!" banner, and resets everything

## Install

```bash
git clone https://github.com/siddz123/Out_Of_Sight_Back_In_Mind.git
cd Out_Of_Sight_Back_In_Mind
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```

## Run

```bash
./venv/bin/python app.py
```

Look for `🎯 Set Focus` in the top-right of your menu bar.

## Usage

1. Click `🎯 Set Focus` → **🔄 Change Focus Goal** → type your goal → **Set Goal**. Title becomes `🟢 [goal]`.
2. Work normally. If you drift onto a blacklisted app or browser tab for 5+ minutes, the title flashes red.
3. The first time it reads a browser URL, macOS will prompt **"Python wants to control [Chrome/Safari/Arc/Brave]"** — click **OK**. Without this permission, browser tab detection silently no-ops.
4. When done, click `🟢 [goal]` → **✅ Mark as Complete**. Chime + banner + reset.
5. **Quit FocusGhost** to exit.

## Configuration

Edit the top of `app.py`:

| Constant | Default | What it does |
|---|---|---|
| `DISTRACTION_BLACKLIST` | `['Discord', 'Spotify', 'Twitter', 'Facebook', 'Terminal']` | Native macOS app names that count as distractions |
| `DOMAIN_BLACKLIST` | `['youtube.com', 'x.com', ...]` | Domains that count as distractions when open in a supported browser. Matches subdomains too. |
| `BROWSER_SCRIPTS` | Chrome, Safari, Arc, Brave | Browsers FocusGhost can read tabs from. Add more by writing the relevant AppleScript. |
| `DISTRACTION_THRESHOLD` | `5` | How many consecutive 60s ticks of distraction trigger the warning |
| `FLASH_INTERVAL` | `0.7` | Seconds between red ↔ system-color flashes during the warning state |

## How it works

- Polls `NSWorkspace.sharedWorkspace().activeApplication()` every 60 seconds for the frontmost app.
- If the app is a supported browser, runs a one-line AppleScript via `osascript` to grab the active tab's URL, then matches the domain against the blacklist.
- Distraction counter increments on each blacklisted tick; resets the instant a non-distraction tick fires.
- Warning state replaces the menu bar title with an `NSAttributedString` colored `NSColor.systemRedColor()`, and a 0.7s timer toggles it back and forth with the system color to produce the flash.

## Requirements

- macOS (uses AppKit, NSWorkspace, `osascript`, and `afplay`)
- Python 3.8+
- `rumps` and `pyobjc` (installed via `requirements.txt`)
