"""Circuit construction for a flagged amplitude-damping channel."""

from math import asin, sqrt

from qiskit import QuantumCircuit
from qiskit_aer.noise import NoiseModel, ReadoutError


NUM_DATA_QUBITS = 3
NUM_SENSOR_QUBITS = 3


def _validate_probability(value: float, name: str) -> None:
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be between 0 and 1")


def build_memory_circuit(logical_value: int, loss_probability: float) -> QuantumCircuit:
    """Build a repetition memory coupled to one loss sensor per data qubit.

    The two-gate sensor interaction is a Stinespring dilation of amplitude
    damping. For one data qubit and a sensor initialized in |0>, it implements

        |0,0> -> |0,0>
        |1,0> -> sqrt(1-p)|1,0> + sqrt(p)|0,1>.

    Measuring the sensor therefore reveals which amplitude-damping jump
    occurred without inventing an extra copy of the data.
    """
    if logical_value not in (0, 1):
        raise ValueError("logical_value must be 0 or 1")
    _validate_probability(loss_probability, "loss_probability")

    circuit = QuantumCircuit(
        NUM_DATA_QUBITS + NUM_SENSOR_QUBITS,
        NUM_DATA_QUBITS + NUM_SENSOR_QUBITS,
        name=f"logical_{logical_value}",
    )

    if logical_value == 1:
        circuit.x(0)
    circuit.cx(0, 1)
    circuit.cx(0, 2)
    circuit.barrier()

    theta = 2.0 * asin(sqrt(loss_probability))
    for data_qubit in range(NUM_DATA_QUBITS):
        sensor_qubit = NUM_DATA_QUBITS + data_qubit
        circuit.cry(theta, data_qubit, sensor_qubit)
        circuit.cx(sensor_qubit, data_qubit)

    circuit.barrier()
    circuit.measure(
        range(NUM_DATA_QUBITS + NUM_SENSOR_QUBITS),
        range(NUM_DATA_QUBITS + NUM_SENSOR_QUBITS),
    )
    return circuit


def build_sensor_noise_model(
    false_positive_probability: float,
    false_negative_probability: float,
) -> NoiseModel:
    """Create asymmetric classical readout noise for the loss sensors."""
    _validate_probability(false_positive_probability, "false_positive_probability")
    _validate_probability(false_negative_probability, "false_negative_probability")

    # Rows are the actual sensor value; columns are the reported value.
    sensor_error = ReadoutError(
        [
            [1.0 - false_positive_probability, false_positive_probability],
            [false_negative_probability, 1.0 - false_negative_probability],
        ]
    )
    noise_model = NoiseModel()
    for sensor_qubit in range(NUM_DATA_QUBITS, NUM_DATA_QUBITS + NUM_SENSOR_QUBITS):
        noise_model.add_readout_error(sensor_error, [sensor_qubit])
    return noise_model
