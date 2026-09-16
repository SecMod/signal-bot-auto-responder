from pathlib import Path

from src.daily_content import generate_variations


OUTPUT = Path("data/messages.txt")


def main() -> None:
    source = input("Enter today's message: ").strip()

    if not source:
        raise SystemExit("Message cannot be empty.")

    variations = generate_variations(source)

    print()
    print("=" * 70)
    print("24 MESSAGE VARIATIONS")
    print("=" * 70)

    for number, message in enumerate(variations, 1):
        print(f"{number:02d}. {message}")

    print()
    answer = input("Save these 24 variations? [y/N]: ").strip().lower()

    if answer != "y":
        print("Nothing was saved.")
        return

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(variations) + "\n", encoding="utf-8")

    print()
    print(f"Saved 24 variations to {OUTPUT}")


if __name__ == "__main__":
    main()
