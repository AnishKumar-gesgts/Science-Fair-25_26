import pytest

from loss_aware_qec.decoders import loss_aware_decode, majority_decode


@pytest.mark.parametrize(
    ("bits", "expected"),
    [
        ((0, 0, 0), 0),
        ((0, 0, 1), 0),
        ((1, 1, 0), 1),
        ((1, 1, 1), 1),
        ((0, 1), None),
    ],
)
def test_majority_decode(bits, expected):
    assert majority_decode(bits) == expected


def test_loss_aware_decoder_removes_flagged_values():
    assert loss_aware_decode((0, 1, 1), (1, 0, 0)) == 1
    assert loss_aware_decode((0, 0, 1), (0, 1, 1)) == 0


def test_loss_aware_decoder_abstains_without_a_strict_vote():
    assert loss_aware_decode((0, 0, 0), (1, 1, 1)) is None
    assert loss_aware_decode((0, 1, 1), (0, 0, 1)) is None


@pytest.mark.parametrize(
    ("data", "flags"),
    [
        ((), ()),
        ((0, 2), (0, 0)),
        ((0, 1), (0,)),
    ],
)
def test_loss_aware_decoder_rejects_invalid_inputs(data, flags):
    with pytest.raises(ValueError):
        loss_aware_decode(data, flags)
