import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from qiskit_aer.noise.errors import kraus_error
import random



# --- Step 1: Build a simple repetition code (encode |ψ> into 3 qubits) ---
def CircuitParameters():
    qc = QuantumCircuit(3, 3)
    qc.h(0)             # Start with |+> = (|0>+|1>)/√2 as logical state
    qc.cx(0, 1)         # Encode
    qc.cx(0, 2)
    qc.barrier()
    qc.measure([0, 1, 2], [0, 1, 2])
    return qc

# look at ancillas & syndrome extraction if time

ploss = 0.2  # loss probability


#qutrit (3by3 matrix, lol)
KrausError0 = np.zeros(3,3)
KrausError1 = np.zeros(3,3)
KrausError0[0,0] = 1
KrausError0[1,1] = np.sqrt(1 - ploss)
KrausError0[2,2] = 1
KrausError1[2,3] = np.sqrt(ploss)


krausError = kraus_error([KrausError0, KrausError1])

'''⚙️ 2. What makes a Kraus error “erasure-compatible”?

A noise process is erasure-compatible if:

The environment state corresponding to the error is orthogonal and distinguishable,
i.e., we can know which qubit was affected.

The process can be represented as a mapping into an extended Hilbert space,
e.g., from 
∣0⟩,∣1⟩ → ∣0⟩,∣1⟩,∣𝑒⟩, where |e⟩ is a “flagged erasure” state.

The hardware can produce a classical signal (“no click”, “no fluorescence”, “leaked energy level”) corresponding to that event.'''

#Quantum Error Object


#think of complex numbers, preserving probabilities through identitiy matrices 
#100% probability satisfied array [1,0], [0,1] is identity

noiseModel = NoiseModel()
RandomErrorChoose = random.randint(1,3)
if RandomErrorChoose == 1:
    noiseModel.add_all_qubit_quantum_error(krausError, ["cx", "h"])
elif RandomErrorChoose == 2:
    noiseModel.add_all_qubit_quantum_error(krausError, ["cx", "h"])


#id  means that the circuit will automatically apply the error to all processes, like idle instead of identity


simulator = AerSimulator(noise_model = noiseModel)

qc = CircuitParameters()

TranspiledQuantumCircuit = transpile(qc, simulator)
result = simulator.run(TranspiledQuantumCircuit, shots=2000).result()
counts = result.get_counts()
print("Raw measurement results with qubit loss:", counts)


def normal_decoder(counts):
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
    logical_counts = {"0":0, "1":0}
    for outcome, freq in counts.items():
        zeros = outcome.count("0")
        ones = outcome.count("1")
        if zeros > ones:
            logical_counts["0"] += freq
        elif ones > zeros:
            logical_counts["1"] += freq
        else:
            logical_counts["0"] += freq/2
            logical_counts["1"] += freq/2
    return logical_counts

print("Standard decode:", normal_decoder(counts))
print("Loss-aware decode:", loss_aware_decoder(counts))
