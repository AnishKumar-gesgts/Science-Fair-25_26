"""Classical decoders used after measuring the repetition code."""

from collections.abc import Sequence


def _validate_bits(bits: Sequence[int], name: str) -> tuple[int, ...]:
    values = tuple(bits)
    if not values:
        raise ValueError(f"{name} must contain at least one bit")
    if any(bit not in (0, 1) for bit in values):
        raise ValueError(f"{name} must contain only 0 and 1")
    return values


def majority_decode(data_bits: Sequence[int]) -> int | None:
    """Return the strict majority value, or ``None`` when the vote is tied."""
    values = _validate_bits(data_bits, "data_bits")
    ones = sum(values)
    zeros = len(values) - ones
    if ones == zeros:
        return None
    return int(ones > zeros)


def loss_aware_decode(
    data_bits: Sequence[int], loss_flags: Sequence[int]
) -> int | None:
    """Decode after removing data qubits whose corresponding flag is one.

    Returning ``None`` represents an honest abstention: the observed information
    is insufficient to make a strict-majority decision.
    """
    data = _validate_bits(data_bits, "data_bits")
    flags = _validate_bits(loss_flags, "loss_flags")
    if len(data) != len(flags):
        raise ValueError("data_bits and loss_flags must have the same length")

    survivors = tuple(bit for bit, flag in zip(data, flags) if flag == 0)
    if not survivors:
        return None
    return majority_decode(survivors)
