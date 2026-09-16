"""Editorial message variation boundary.

Variations are intended for ordinary content editing and user review. This
module does not implement anti-abuse evasion.
"""
def generate_variations(base_text: str, count: int = 24) -> list[str]:
    if not base_text.strip():
        raise ValueError("base_text cannot be empty")
    if count < 1:
        raise ValueError("count must be positive")
    return [base_text.strip() for _ in range(count)]
