import hashlib

from backend_v2.utils.hashing import generate_atom_hash


def test_generate_atom_hash_without_mandate() -> None:
    text = " This is a test atom "
    result = generate_atom_hash(text)
    expected = hashlib.md5(b"This is a test atom").hexdigest()
    assert result == expected


def test_generate_atom_hash_with_mandate() -> None:
    text = "This is a test atom "
    mandate = "_MANDATE"
    result = generate_atom_hash(text, mandate)
    expected = hashlib.md5(b"This is a test atom_MANDATE").hexdigest()
    assert result == expected
