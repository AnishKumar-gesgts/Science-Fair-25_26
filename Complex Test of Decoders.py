import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from qiskit_aer.noise.errors import kraus_error

# --- Step 1: Build a simple repetition code (encode |ψ> into 3 qubits) ---
def CircuitParameters():
    qc = QuantumCircuit(3, 3)
    qc.h(0)             # Start with |+> = (|0>+|1>)/√2 as logical state
    qc.cx(0, 1)         # Encode
    qc.cx(0, 2)
    qc.barrier()
    qc.measure([0, 1, 2], [0, 1, 2])
    return qc


# --- Step 2: Kraus operator for qubit loss (|1> -> |0>) ---
ploss = 0.2  # loss probability

K0 = np.array([[1, 0], [0, np.sqrt(1 - ploss)]])
K1 = np.array([[0, np.sqrt(ploss)], [0, 0]])
loss_error = kraus_error([K0, K1])  # 1-qubit amplitude damping error

# Create 2-qubit version for CNOT gates by tensoring two single-qubit errors
loss_error_2q = loss_error.tensor(loss_error)

# Build noise model
noise_model = NoiseModel()
noise_model.add_all_qubit_quantum_error(loss_error, ["h"])     # 1-qubit ops
noise_model.add_all_qubit_quantum_error(loss_error_2q, ["cx"]) # 2-qubit ops

# --- Step 3: Simulate with noise ---
simulator = AerSimulator(noise_model=noise_model)

qc = CircuitParameters()
transpiled_qc = transpile(qc, simulator)
result = simulator.run(transpiled_qc, shots=2000).result()
counts = result.get_counts()
print("Raw measurement results with qubit loss:", counts)


# --- Step 4: Define decoders ---
def normal_decoder(counts):
    """Majority vote, assumes no loss"""
    logical_counts = {"0": 0, "1": 0}
    for outcome, freq in counts.items():
        if outcome.count("0") > 1:
            majority = "0"
        else:
            majority = "1"
        logical_counts[majority] += freq
    return logical_counts


def loss_aware_decoder(counts):
    """Ignore lost qubits: if tie, keep coherence"""
    logical_counts = {"0": 0, "1": 0}
    for outcome, freq in counts.items():
        zeros = outcome.count("0")
        ones = outcome.count("1")
        if zeros > ones:
            logical_counts["0"] += freq
        elif ones > zeros:
            logical_counts["1"] += freq
        else:
            # Tie — ambiguous, preserve coherence half-half
            logical_counts["0"] += freq / 2
            logical_counts["1"] += freq / 2
    return logical_counts


print("Standard decode:", normal_decoder(counts))
print("Loss-aware decode:", loss_aware_decoder(counts))
