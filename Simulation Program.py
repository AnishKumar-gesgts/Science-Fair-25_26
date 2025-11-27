import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from qiskit_aer.noise.errors import kraus_error
import random



# --- Step 1: Build a simple repetition code (encode |ψ> into 3 qubits) ---
def CircuitParameters():
    qc = QuantumCircuit(9,9)

    #have loss
    qc.h(0)             # Start with |+> = (|0>+|1>)/√2 as logical state
    qc.cx(0,1)         # Encode
    qc.cx(0,2)

    qc.cx(0, 6)
    qc.id(0)
    qc.cx(0, 6)
    
    qc.cx(1, 7)
    qc.id(1) 
    qc.cx(1, 7)

    qc.cx(2, 8)
    qc.id(2)
    qc.cx(2, 8)
    
    
    #no loss
    qc.h(3)
    qc.cx(3,4)
    qc.cx(3,5)


    
    
    qc.measure([0,1,2,3,4,5,6,7,8], [0,1,2,3,4,5,6,7,8])
    return qc




# look at ancillas & syndrome extraction if time

ploss = 0.003  # loss probability
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
nyqubit = random.randint(0,2)
NoiseModel.add_quantum_error(krausDataError, ["id"], [nyqubit])
'''NoiseModel.add_quantum_error(krausDataError, ["id"], [1])
NoiseModel.add_quantum_error(krausDataError, ["id"], [2])'''






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

Middle3Qubits = {}
for value, frequency2 in counts.items():
    middle3value = value[3:-3]  # Get the first 3 bits (data qubits)
    Middle3Qubits[middle3value] = Middle3Qubits.get(middle3value, 0) + frequency2

Last3Qubits = {}
for value, frequency3 in counts.items():
    last3value = value[:3]  # Get the first 3 bits (data qubits)
    Last3Qubits[last3value] = Last3Qubits.get(last3value, 0) + frequency3
        


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

def noerror_decoder(Middle3Qubits):
    finalcountsnoerror = {"0":0, "1":0}
    for value, freq in Middle3Qubits.items():
        if value.count("0") > 1:
            majority = "0"  
        else:
            majority = "1"
        finalcountsnoerror[majority] += freq
    return finalcountsnoerror

#need to write

def loss_aware_decoder(counts):
    finalcounts = {"0": 0, "1": 0}
    for value,freq in counts.items():
    # map qubits to positions in the bitstring
    # value string: [cbit8, cbit7, cbit6, cbit5, cbit4, cbit3, cbit2, cbit1, cbit0]
        qubit_map = {
            0: int(value[8]),  # qubit 0
            1: int(value[7]),  # qubit 1
            2: int(value[6]),  # qubit 2
            3: int(value[5]),  # qubit 3
            4: int(value[4]),  # qubit 4
            5: int(value[3]),  # qubit 5
            6: int(value[2]),  # qubit 6
            7: int(value[1]),  # qubit 7
            8: int(value[0]),  # qubit 8
        }

        # ancilla = qubits 6,7,8
        ancillaval = [qubit_map[6], qubit_map[7], qubit_map[8]]
        # data qubits = 0,1,2
        qubitval = [qubit_map[0], qubit_map[1], qubit_map[2]]

        if ancillaval[0] == 0:
            finalcounts[str(qubitval[0])] += freq
        if ancillaval[1] == 0:
            finalcounts[str(qubitval[1])] += freq
        if ancillaval[2] == 0:
            finalcounts[str(qubitval[2])] += freq

        

        '''
        if ancillaval.count(0) == 3:
            majority = "0" if qubitval.count(0) > 1 else "1"
            finalcounts[majority] += freq
        elif ancillaval.count(0) == 2:
            majority = "0" if qubitval.count(0) > 1 else "1"
            finalcounts[majority] += freq*(1-(1*ploss))
        elif ancillaval.count(0) == 1:
            majority = "0" if qubitval.count(0) > 1 else "1"
            finalcounts[majority] += freq*(1-(2*ploss))
        else:
            if qubitval.count("0") > 1:
                majority = "0"  
            else:
                majority = "1"
            finalcounts[majority] += freq*(1-(3*ploss))
        '''

    return finalcounts

#NEED TO REVISE BY IMPLEMENTING PER QUBIT ANCILLA CORRECTION, 
#CAN REMOVE THOSE QUBITS AND THEN MAKE MAJORITY 1,0, OR 0.5
        


print("Normal decoder:", normal_decoder(First3Qubits))
print("Ancilla decoder:", loss_aware_decoder(counts))
print("No-error decoder: ", noerror_decoder(Middle3Qubits))
print("Raw measurement results with qubit loss:", counts)

