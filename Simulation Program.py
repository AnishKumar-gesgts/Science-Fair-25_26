import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from qiskit_aer.noise.errors import kraus_error
import random



# --- Step 1: Build a simple repetition code (encode |ψ> into 3 qubits) ---
def CircuitParameters():
    qc = QuantumCircuit(6,6)
    qc.h(0)             # Start with |+> = (|0>+|1>)/√2 as logical state
    qc.cx(0,1)         # Encode
    qc.id(0)
    qc.id(1) 
    qc.cx(0,2)
    qc.id(0)
    qc.id(2) 

    qc.measure([0,1,2], [0,1,2])
    qc.barrier()

    qc.cx(0,3)
    qc.x(3)
    qc.cx(1,4)
    qc.x(4)
    qc.cx(2,5)
    qc.x(5)
    

    qc.measure([3,4,5], [3,4,5])
    return qc




# look at ancillas & syndrome extraction if time

ploss = 0.2  # loss probability
pdeterror = 0.01 #detection error

A0 = np.array([[1, 0],[0, np.sqrt(1 - ploss)]])
A1 = np.array([[0, np.sqrt(ploss)], [0, 0]])
krausDataError = kraus_error([A0, A1])

DetectionError0 = np.array([[1, 0],[0, np.sqrt(1 - pdeterror)]])
DetectionError1 = np.array([[0, np.sqrt(pdeterror)], [0, 0]])
krausAncillaError = kraus_error([DetectionError0, DetectionError1])

#qutrit (3by3 matrix, lol) WHICH DONT WORK NOOOOOOOO





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

NoiseModel = NoiseModel()
'''
NoiseModel.add_quantum_error(krausAncillaError, ["id"], [3])
NoiseModel.add_quantum_error(krausAncillaError, ["id"], [4])
NoiseModel.add_quantum_error(krausAncillaError, ["id"], [5])
'''
# Apply independent amplitude damping to each qubit at each single-qubit gate
NoiseModel.add_quantum_error(krausDataError, ["h"], [0])  # qubit 0 H
NoiseModel.add_quantum_error(krausDataError, ["id"], [0]) # qubit 0 idle
NoiseModel.add_quantum_error(krausDataError, ["id"], [1]) # qubit 1 idle
NoiseModel.add_quantum_error(krausDataError, ["id"], [2]) # qubit 2 idle



#id  means that the circuit will automatically apply the error to all processes, like idle instead of identity

simulation = AerSimulator()

qc = CircuitParameters()

TranspiledQC = transpile(qc, simulation)

result = simulation.run(qc, noise_model=NoiseModel, shots=2000).result()
counts = result.get_counts()

First3Qubits = {}
for value, frequency1 in counts.items():
    first3value = value[-3:]  # Get the first 3 bits (data qubits)
    First3Qubits[first3value] = First3Qubits.get(first3value, 0) + frequency1

Last3Qubits = {}
for value, frequency2 in counts.items():
    last3value = value[:3]  # Get the first 3 bits (data qubits)
    Last3Qubits[last3value] = Last3Qubits.get(last3value, 0) + frequency2
        


#counts is a dictionary of unique combinations and the number of times it occured (outcome, freq)

def normal_decoder(First3Qubits):
    finalcountsnormal = {"0":0, "1":0}
    for value, freq in First3Qubits.items():
        if value.count("0") > 1:
            majority = "0"  
        else:
            majority = "1"
        finalcountsnormal[majority] += freq
    return finalcountsnormal

#need to write

def loss_aware_decoder(First3Qubits):
    finalcountsnormal = {"0":0, "1":0}
    for value, freq in counts.items():
        error = value[:3].count("1") > 1
        if error == False:
            first3value = value[-3:]
            if first3value.count("0") > 1:
                majority = "0"  
            else:
                majority = "1"
            finalcountsnormal[majority] += freq
    return finalcountsnormal

def loss_aware_decoder(counts):
    
    finalcountsnormal = {"0": 0, "1": 0}

    for value, freq in counts.items():
        # Slice bits
        ancillaval = value[:3]  # first 3 bits = ancillas 3,4,5
        qubitval = value[-3:]    # last 3 bits = data 0,1,2

        # Only count if ancilla indicates no erasure
        # Adjust this depending on your convention; here we assume "0" = no error
        if (ancillaval.count("1") >1):
            # Majority vote on data qubits
            if qubitval.count("0") > 1:
                majority = "0"
            else:
                majority = "1"
            finalcountsnormal[majority] += freq
    return finalcountsnormal
        


print("Normal decoder:", normal_decoder(First3Qubits))
print("Erasrue decoder:", loss_aware_decoder(First3Qubits))
print("Raw measurement results with qubit loss:", counts)
