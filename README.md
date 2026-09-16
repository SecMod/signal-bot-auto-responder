# Signal Bot Auto Responder

Linux project for preparing and scheduling **authorized, human-reviewed** Signal group content.

## Current MVP
- Python project structure
- 15-minute scheduling model
- 24 content slots
- Daily message/content-pack workflow
- Logging and tests
- systemd template for the local application
- Signal transport boundary kept separate from content preparation

## Important platform limitation

Signal's current Terms of Service prohibit bulk messaging and auto-messaging. The project therefore does **not** implement unattended automatic posting to Signal, CAPTCHA solving, anti-bot bypasses, fingerprint spoofing, invisible-character tricks, or UI automation intended to evade platform controls.

The current workflow prepares content for review. A human should perform the actual posting where permitted.

## Daily workflow

1. Enter the day's base message.
2. Generate a 24-slot content pack.
3. Review/edit the variants.
4. Post approved content manually where permitted.
5. Keep the scheduler available for reminders/logging rather than unattended Signal delivery.

## Development

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pytest
python -m src.cli
```

Configuration is available through `.env.example`.
