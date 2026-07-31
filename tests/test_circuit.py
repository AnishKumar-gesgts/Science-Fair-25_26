from qiskit.quantum_info import Operator

from loss_aware_qec.circuit import build_memory_circuit


def test_circuit_has_three_data_qubits_and_three_sensors():
    circuit = build_memory_circuit(logical_value=1, loss_probability=0.2)
    assert circuit.num_qubits == 6
    assert circuit.num_clbits == 6


def test_amplitude_damping_interaction_is_unitary_before_measurement():
    circuit = build_memory_circuit(logical_value=1, loss_probability=0.2)
    interaction = circuit.remove_final_measurements(inplace=False)
    assert Operator(interaction).is_unitary()
