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

A0 = np.array([[1, 0],[0, np.sqrt(1 - ploss)]])
A1 = np.array([[0, np.sqrt(ploss)], [0, 0]])
krausNormalError = kraus_error([A0, A1])


#qutrit (3by3 matrix, lol) WHICH DONT WORK NOOOOOOOO
KrausError0 = np.array([[1,0,0],[0,np.sqrt(1-ploss),0],[0,0,1]])
KrausError1 = np.array([[0,0,0],[0,0,0],[0,np.sqrt(ploss),0]])


krausErasureAwareError = kraus_error([KrausError0, KrausError1])

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

noiseErasureModel = NoiseModel()
noiseErasureModel.add_all_qubit_quantum_error(krausErasureAwareError, ["cx", "h"])
noiseNormalModel = NoiseModel()
noiseErasureModel.add_all_qubit_quantum_error(krausNormalError, ["cx", "h"])


#id  means that the circuit will automatically apply the error to all processes, like idle instead of identity

simulation = AerSimulator()

qc = CircuitParameters()

TranspiledQC = transpile(qc, simulation)

resultN = simulation.run(qc, noise_model=noiseNormalModel, shots=2000).result()
resultE = simulation.run(qc, noise_model=noiseErasureModel, shots=2000).result()
countsN = resultN.get_counts()
countsE = resultE.get_counts()
print("Measurement with loss: ", countsN)
print("Measurements with loss + erasure flags: ", countsE)

#counts is a dictionary of unique combinations and the number of times it occured (outcome, freq)

def normal_decoder(countsN):
    """Majority vote, assumes no loss"""
    logical_counts = {"0":0, "1":0}
    for outcome, freq in countsN.items():
        if outcome.count("0") > 1:
            majority = "0"  
        else:
            majority = "1"
        logical_counts[majority] += freq
    return logical_counts

#need to write

def loss_aware_decoder(countsE):
    logical_counts = {"0":0, "1":0}
    erasureflags = 0
    postErasure = []
    for outcome, freq in countsE.items():
        erasureflags = outcome.count("e")
        for element in outcome:
            if element != "e":
                postErasure.append(element)
                erasureflags += 1

        zeros = postErasure.count("0")
        ones = postErasure.count("1")
        
        if zeros > ones:
            logical_counts["0"] += freq
        elif ones > zeros:
            logical_counts["1"] += freq
    return logical_counts

print("Normal decoder:", normal_decoder(countsN))
print("Erasrue decoder:", loss_aware_decoder(countsE))
