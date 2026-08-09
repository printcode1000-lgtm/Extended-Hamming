"""Reference Hamming (11,7) and extended Hamming (12,7) models.

Bit positions are one-based. Parity occupies positions 1, 2, 4, and 8.
Data D1..D7 occupies positions 3, 5, 6, 7, 9, 10, and 11.
The overall parity P0 is appended at position 12.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations, product
from typing import Iterable, Sequence

DATA_POSITIONS = (3, 5, 6, 7, 9, 10, 11)
PARITY_POSITIONS = (1, 2, 4, 8)


def _bits(data: int | Sequence[int]) -> tuple[int, ...]:
    if isinstance(data, int):
        if not 0 <= data < 128:
            raise ValueError("A seven-bit data word must be in [0, 127].")
        return tuple((data >> i) & 1 for i in range(7))
    values = tuple(int(v) for v in data)
    if len(values) != 7 or any(v not in (0, 1) for v in values):
        raise ValueError("Expected exactly seven binary values D1..D7.")
    return values


def encode_11_7(data: int | Sequence[int]) -> tuple[int, ...]:
    """Return positions 1..11 using even parity."""
    d1, d2, d3, d4, d5, d6, d7 = _bits(data)
    p1 = d1 ^ d2 ^ d4 ^ d5 ^ d7
    p2 = d1 ^ d3 ^ d4 ^ d6 ^ d7
    p4 = d2 ^ d3 ^ d4
    p8 = d5 ^ d6 ^ d7
    return (p1, p2, d1, p4, d2, d3, d4, p8, d5, d6, d7)


def encode_12_7(data: int | Sequence[int]) -> tuple[int, ...]:
    """Return an extended codeword with overall even parity at position 12."""
    base = encode_11_7(data)
    p0 = 0
    for bit in base:
        p0 ^= bit
    return base + (p0,)


def syndrome(codeword: Sequence[int]) -> int:
    if len(codeword) < 11:
        raise ValueError("At least 11 bits are required.")
    syn = 0
    for parity in PARITY_POSITIONS:
        check = 0
        for pos in range(1, 12):
            if pos & parity:
                check ^= int(codeword[pos - 1])
        if check:
            syn |= parity
    return syn


@dataclass(frozen=True)
class DecodeResult:
    data: tuple[int, ...]
    corrected_codeword: tuple[int, ...]
    status: str
    syndrome: int
    overall_parity_error: bool


def decode_12_7(received: Sequence[int]) -> DecodeResult:
    """Decode SEC-DED and distinguish correctable from detected double errors."""
    if len(received) != 12 or any(int(v) not in (0, 1) for v in received):
        raise ValueError("Expected a 12-bit binary codeword.")
    work = [int(v) for v in received]
    syn = syndrome(work)
    overall = bool(sum(work) & 1)
    if syn == 0 and not overall:
        status = "no_error"
    elif syn != 0 and overall:
        work[syn - 1] ^= 1
        status = "single_error_corrected"
    elif syn == 0 and overall:
        work[11] ^= 1
        status = "overall_parity_error_corrected"
    else:
        status = "double_error_detected"
    data = tuple(work[pos - 1] for pos in DATA_POSITIONS)
    return DecodeResult(data, tuple(work), status, syn, overall)


def inject(codeword: Sequence[int], positions: Iterable[int]) -> tuple[int, ...]:
    result = list(codeword)
    for position in positions:
        if not 1 <= position <= len(result):
            raise ValueError(f"Invalid one-based error position: {position}")
        result[position - 1] ^= 1
    return tuple(result)


def exhaustive_verification() -> dict[str, int]:
    counts = {"data_words": 0, "single_errors": 0, "double_errors": 0}
    for word in range(128):
        data = _bits(word)
        codeword = encode_12_7(data)
        no_error = decode_12_7(codeword)
        assert no_error.data == data and no_error.status == "no_error"
        counts["data_words"] += 1
        for position in range(1, 13):
            decoded = decode_12_7(inject(codeword, (position,)))
            assert decoded.data == data
            assert decoded.status in {
                "single_error_corrected",
                "overall_parity_error_corrected",
            }
            counts["single_errors"] += 1
        for positions in combinations(range(1, 13), 2):
            decoded = decode_12_7(inject(codeword, positions))
            assert decoded.status == "double_error_detected"
            counts["double_errors"] += 1
    return counts


def all_vectors() -> list[dict[str, object]]:
    rows = []
    for word, values in enumerate(product((0, 1), repeat=7)):
        rows.append({
            "word": word,
            "data_d1_to_d7": list(values),
            "hamming_11_7": list(encode_11_7(values)),
            "extended_12_7": list(encode_12_7(values)),
        })
    return rows

