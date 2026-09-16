import logging
from .config import Settings
from .scheduler import run_forever

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")

def main():
    s = Settings.from_env()
    run_forever(
        ["Replace this with today's approved message."],
        s.interval_minutes * 60,
        lambda m: logging.info("Prepared: %s", m),
    )

if __name__ == "__main__":
    main()
