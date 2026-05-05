import hashlib


def generate_atom_hash(text: str, mandate: str | None = None) -> str:
    """Generates an MD5 hash for a given atom text and an optional mandate.

    This centralizes the V2 architecture's deterministic atom hashing,
    ensuring that the LLM's outputs correctly map to scoring criteria
    even if the string composition logic evolves.

    Args:
        text (str): The core evaluated statement or claim.
        mandate (str | None): Optional EvaluationMandate modifier appended to the end.

    Returns:
        str: MD5 hex digest.
    """
    if mandate:
        full_text = f"{text.strip()}{mandate}"
    else:
        full_text = text.strip()
    return hashlib.md5(full_text.encode("utf-8")).hexdigest()
