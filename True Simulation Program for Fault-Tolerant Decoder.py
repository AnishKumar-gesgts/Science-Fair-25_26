import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from qiskit_aer.noise.errors import kraus_error


# --- Step 1: Build a simple repetition code (encode |ψ> into 3 qubits) ---
def CircuitParameters():
    qc = QuantumCircuit(3, 3)
    qc.h(0)             # Start with |+> = (|0>+|1>)/√2 as logical state
    qc.cx(0, 1)         # Encode
    qc.cx(0, 2)
    return qc


# look at ancillas & syndrome extraction if time


# --- Step 2: Kraus operator for qubit loss (|1> -> |0>) ---
# Kraus operators are a set of quantum mechanical operators 
# that describe the evolution of an open quantum system, 
# such as a quantum state interacting with an environment

ploss = 0.2  # loss probability


K0 = np.array([[1, 0], [0, np.sqrt(1 - ploss)]])
K1 = np.array([[0, np.sqrt(ploss)], [0, 0]])
loss_error = kraus_error([K0, K1])
#Quantum Error Object


#think of complex numbers, preserving probabilities through identitiy matrices 
#100% probability satisfied array [1,0], [0,1] is identity

noise_model = NoiseModel()
noise_model.add_all_qubit_quantum_error(loss_error, ["cx", "h"])

#id  means that the circuit will automatically apply the error to all processes, like idle instead of identity
# --- Step 3: Simulate with noise ---
simulator = AerSimulator(noise_model = noise_model)

qc = CircuitParameters()
#check what this is
qc.barrier()
qc.measure([0, 1, 2], [0, 1, 2])  # measure all
#end check

TranspiledQuantumCircuit = transpile(qc, simulator)
result = simulator.run(TranspiledQuantumCircuit, shots=2000).result()
counts = result.get_counts()
print("Raw measurement results with qubit loss:", counts)



# --- Step 4: Define decoders ---
def standard_decoder(counts):
    """Majority vote, assumes no loss"""
    logical_counts = {"0":0, "1":0}
    for outcome, freq in counts.items():
        if outcome.count("0") > 1:
            majority = "0"  
        else:
            majority = "1"
        logical_counts[majority] += freq
    return logical_counts

def loss_aware_decoder(counts):
    """Ignore lost qubits: if tie, keep coherence"""
    logical_counts = {"0":0, "1":0}
    for outcome, freq in counts.items():
        # treat 'loss' as erasure (we simulate loss by bias in results)
        zeros = outcome.count("0")
        ones = outcome.count("1")
        if zeros > ones:
            logical_counts["0"] += freq
        elif ones > zeros:
            logical_counts["1"] += freq
        else:
            # If tie (e.g., 01?), keep superposition (count half-half)
            logical_counts["0"] += freq/2
            logical_counts["1"] += freq/2
    return logical_counts

print("Standard decode:", standard_decoder(counts))
print("Loss-aware decode:", loss_aware_decoder(counts))
