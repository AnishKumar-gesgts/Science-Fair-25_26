"""Experiment runner and metrics for standard and loss-aware decoding."""

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from qiskit import transpile
from qiskit_aer import AerSimulator

from .circuit import (
    NUM_DATA_QUBITS,
    NUM_SENSOR_QUBITS,
    build_memory_circuit,
    build_sensor_noise_model,
)
from .decoders import loss_aware_decode, majority_decode


@dataclass(frozen=True)
class ExperimentConfig:
    """Parameters for one balanced logical-memory benchmark."""

    loss_probability: float = 0.2
    false_positive_probability: float = 0.01
    false_negative_probability: float = 0.01
    shots_per_input: int = 5_000
    seed: int = 7

    def __post_init__(self) -> None:
        for name in (
            "loss_probability",
            "false_positive_probability",
            "false_negative_probability",
        ):
            value = getattr(self, name)
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1")
        if self.shots_per_input <= 0:
            raise ValueError("shots_per_input must be positive")


@dataclass(frozen=True)
class DecoderMetrics:
    """Outcome totals for a decoder."""

    correct: int
    incorrect: int
    abstained: int

    @property
    def total(self) -> int:
        return self.correct + self.incorrect + self.abstained

    @property
    def success_rate(self) -> float:
        """Correct trials divided by all trials; abstentions count as failures."""
        return self.correct / self.total

    @property
    def coverage(self) -> float:
        """Fraction of trials on which the decoder returned a value."""
        return (self.correct + self.incorrect) / self.total

    @property
    def conditional_accuracy(self) -> float | None:
        """Accuracy among non-abstained trials."""
        decoded = self.correct + self.incorrect
        return self.correct / decoded if decoded else None


@dataclass(frozen=True)
class ExperimentResult:
    config: ExperimentConfig
    standard: DecoderMetrics
    loss_aware: DecoderMetrics
    counts_by_input: Mapping[int, Mapping[str, int]]


def parse_measurement(outcome: str) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Convert Qiskit's high-to-low classical string into data and flag tuples."""
    compact = outcome.replace(" ", "")
    expected_length = NUM_DATA_QUBITS + NUM_SENSOR_QUBITS
    if len(compact) != expected_length or any(bit not in "01" for bit in compact):
        raise ValueError(f"expected a {expected_length}-bit measurement, got {outcome!r}")

    low_to_high = tuple(int(bit) for bit in reversed(compact))
    return (
        low_to_high[:NUM_DATA_QUBITS],
        low_to_high[NUM_DATA_QUBITS:],
    )


def _score(
    counts_by_input: Mapping[int, Mapping[str, int]], loss_aware: bool
) -> DecoderMetrics:
    correct = incorrect = abstained = 0
    for logical_value, counts in counts_by_input.items():
        for outcome, frequency in counts.items():
            data_bits, loss_flags = parse_measurement(outcome)
            decoded = (
                loss_aware_decode(data_bits, loss_flags)
                if loss_aware
                else majority_decode(data_bits)
            )
            if decoded is None:
                abstained += frequency
            elif decoded == logical_value:
                correct += frequency
            else:
                incorrect += frequency
    return DecoderMetrics(correct, incorrect, abstained)


def run_experiment(config: ExperimentConfig = ExperimentConfig()) -> ExperimentResult:
    """Simulate equally many logical-zero and logical-one memory trials."""
    simulator = AerSimulator(
        noise_model=build_sensor_noise_model(
            config.false_positive_probability,
            config.false_negative_probability,
        )
    )

    counts_by_input: dict[int, Mapping[str, int]] = {}
    for logical_value in (0, 1):
        circuit = build_memory_circuit(logical_value, config.loss_probability)
        compiled = transpile(circuit, simulator, optimization_level=0)
        result = simulator.run(
            compiled,
            shots=config.shots_per_input,
            seed_simulator=config.seed + logical_value,
        ).result()
        counts_by_input[logical_value] = MappingProxyType(
            dict(result.get_counts(compiled))
        )

    readonly_counts = MappingProxyType(counts_by_input)
    return ExperimentResult(
        config=config,
        standard=_score(readonly_counts, loss_aware=False),
        loss_aware=_score(readonly_counts, loss_aware=True),
        counts_by_input=readonly_counts,
    )
