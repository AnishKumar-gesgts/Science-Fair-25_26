import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from qiskit_aer.noise.errors import kraus_error
import random

num_shots = 2000
num_qubits = 3  # your data qubits

# Store the measurement results
results = []

for shot in range(num_shots):
    data_qubits = [1, 1, 1]  # assume |1> initial state, adjust as needed
    erasure_flags = [False]*num_qubits
    
    for i in range(num_qubits):
        # Randomly select Kraus operator based on probability
        if np.random.rand() < p_loss:
            # Apply A1 (decay)
            data_qubits[i] = 0        # qubit decayed
            erasure_flags[i] = True   # mark erasure
        else:
            # Apply A0 (no decay)
            data_qubits[i] = data_qubits[i]  # stays same
            erasure_flags[i] = False
    
    # Apply your majority vote decoder considering erasure flags
    # Example: only include non-erased qubits in majority vote
    non_erased_values = [data_qubits[i] for i in range(num_qubits) if not erasure_flags[i]]
    if len(non_erased_values) > 0:
        majority = 0 if non_erased_values.count(0) > len(non_erased_values)/2 else 1
    else:
        majority = None  # all qubits erased, cannot decode
    
    results.append((data_qubits.copy(), erasure_flags.copy(), majority))
