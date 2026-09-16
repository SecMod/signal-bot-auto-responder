# Signal Bot Auto Responder

Linux project for preparing and reviewing **authorized** Signal group content.

## V2 control panel

The local Tkinter control panel now provides:
- Daily message entry
- Generate exactly 24 editorial variations
- Review/edit each variation
- Approve individual variations
- Save approved packs to SQLite
- Local status display

Run it with:

```bash
python3 -m venv .venv
source .venv/bin/activate
python run_gui.py
```

On Debian/Ubuntu, if Tkinter is missing, install the distribution package:

```bash
sudo apt install python3-tk
```

## Important platform limitation

The project does **not** implement unattended Signal posting, CAPTCHA solving, anti-bot bypasses, fingerprint spoofing, invisible-character tricks, or UI automation intended to evade platform controls. The GUI prepares and stores content for human review.

## Project layout

- `src/daily_content.py` — 24-variation content generation
- `src/gui.py` — local control panel
- `src/storage.py` — SQLite persistence
- `src/scheduler.py` — generic local scheduler
- `src/signal_client.py` — transport boundary
- `tests/` — automated tests
- `systemd/` — service template


<!-- CI verification -->
