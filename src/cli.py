from __future__ import annotations

from .daily_content import build_pack

def main() -> None:
    print("Signal Bot Auto Responder — review mode")
    print("This tool prepares content; it does not automatically post to Signal.")
    source = input("\nToday's message: ").strip()
    pack = build_pack(source)
    print("\n24 review slots:")
    for i, text in enumerate(pack.variations, 1):
        print(f"{i:02d}. {text}")
    print("\nNo messages were sent.")

if __name__ == "__main__":
    main()
