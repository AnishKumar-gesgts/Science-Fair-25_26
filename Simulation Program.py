import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from qiskit_aer.noise.errors import kraus_error
from qiskit.circuit import Delay
import random



# --- Step 1: Build a simple repetition code (encode |ψ> into 3 qubits) ---
def CircuitParameters():
    qc = QuantumCircuit(9,9)

    #have loss
    qc.h(0)
    qc.cx(0, 1)
    qc.cx(0, 2)

    # Logical block B (clean/reference block) - prepare same logical state independently
    qc.cx(0, 3)
    qc.cx(1, 4)
    qc.cx(2, 5)
    
    qc.append(Delay(100), [0])
    qc.append(Delay(100), [1])
    qc.append(Delay(100), [2])


    # Ancilla flags (ancilla i = XOR(dataA_i, dataB_i) )
    # ancilla = 1 if data bits differ (i.e., disagreement / possible error)
    qc.cx(0, 6)
    qc.cx(3, 6)

    qc.cx(1, 7)
    qc.cx(4, 7)

    qc.cx(2, 8)
    qc.cx(5, 8)

    qc.append(Delay(100), [6])
    qc.append(Delay(100), [7])
    qc.append(Delay(100), [8])
    
    #no loss

    qc.measure([0,1,2,3,4,5,6,7,8], [0,1,2,3,4,5,6,7,8])
    return qc

# look at ancillas & syndrome extraction if time

ploss = 0.1  # loss probability
pdeterror = 0.01 #detection error

A0 = np.array([[1, 0],[0, np.sqrt(1 - ploss)]])
A1 = np.array([[0, np.sqrt(ploss)], [0, 0]])
krausDataError = kraus_error([A0, A1])

DetectionError0 = np.array([[1, 0],[0, np.sqrt(1 - pdeterror)]])
DetectionError1 = np.array([[0, np.sqrt(pdeterror)], [0, 0]])
krausAncillaError = kraus_error([DetectionError0, DetectionError1])

#qutrit (3by3 matrix, lol) WHICH DONT WORK NOOOOOOOO

#think of complex numbers, preserving probabilities through identitiy matrices 
#100% probability satisfied array [1,0], [0,1] is identity

NoiseModel = NoiseModel()

# Apply independent amplitude damping to each qubit at each single-qubit gate

for q in (0,1,2):
    NoiseModel.add_quantum_error(krausDataError, ["delay"], [q])
for q in (6,7,8):
    NoiseModel.add_quantum_error(krausAncillaError, ["delay"], [q])







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
        
        storeval = []
        for i in range(3):
            if ancillaval[i] == 0:
                storeval.append(qubitval[i])
        
        if len(storeval) == 0:
            continue
        else:
            majorityvote = sum(storeval)/len(storeval)
            if len(storeval) != 0:
                if majorityvote > 0.5:
                    finalval = "1"
                    Tie = False
                elif majorityvote < 0.5:
                    finalval = "0"
                    Tie = False
                elif majorityvote == 0.5:
                    Tie = True

                if Tie:
                    finalcounts["0"] += freq/2
                    finalcounts["1"] += freq/2
                elif Tie == False:
                    finalcounts[finalval] += freq


    return finalcounts

#NEED TO REVISE BY IMPLEMENTING PER QUBIT ANCILLA CORRECTION, 
#CAN REMOVE THOSE QUBITS AND THEN MAKE MAJORITY 1,0, OR 0.5
        


print("Normal decoder:", normal_decoder(First3Qubits))
print("Ancilla decoder:", loss_aware_decoder(counts))
print("No-error decoder: ", noerror_decoder(Middle3Qubits))
print("Raw measurement results with qubit loss:", counts)

