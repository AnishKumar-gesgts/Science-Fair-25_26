import pytest

from loss_aware_qec.experiment import (
    ExperimentConfig,
    parse_measurement,
    run_experiment,
)


def test_parse_measurement_respects_qiskit_bit_order():
    data, flags = parse_measurement("101010")
    assert data == (0, 1, 0)
    assert flags == (1, 0, 1)


def test_no_loss_is_decoded_perfectly():
    result = run_experiment(
        ExperimentConfig(
            loss_probability=0.0,
            false_positive_probability=0.0,
            false_negative_probability=0.0,
            shots_per_input=100,
        )
    )
    assert result.standard.success_rate == 1.0
    assert result.loss_aware.success_rate == 1.0
    assert result.loss_aware.coverage == 1.0


def test_certain_loss_exposes_the_difference_between_decoders():
    result = run_experiment(
        ExperimentConfig(
            loss_probability=1.0,
            false_positive_probability=0.0,
            false_negative_probability=0.0,
            shots_per_input=100,
        )
    )
    assert result.standard.success_rate == 0.5
    assert result.loss_aware.success_rate == 0.5
    assert result.loss_aware.coverage == 0.5
    assert result.loss_aware.conditional_accuracy == 1.0


@pytest.mark.parametrize("field", ["loss_probability", "false_negative_probability"])
def test_invalid_probabilities_are_rejected(field):
    with pytest.raises(ValueError):
        ExperimentConfig(**{field: 1.1})
