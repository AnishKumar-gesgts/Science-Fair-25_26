from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
from qiskit_aer.noise import NoiseModel
from qiskit_aer.noise.errors import kraus_error
import numpy as np


qc = QuantumCircuit(1, 1)
qc.h(0)
qc.measure(0, 0)


p_loss = 0.1
K0 = np.array([[1, 0],
               [0, np.sqrt(1 - p_loss)]])
K1 = np.array([[0, np.sqrt(p_loss)],
               [0, 0]])
loss_error = kraus_error([K0, K1])

noise_model = NoiseModel()
noise_model.add_all_qubit_quantum_error(loss_error, ["h", "id"])

backend = Aer.get_backend("qasm_simulator")
tqc = transpile(qc, backend)
shots = 1000
job = backend.run(tqc, shots=shots, noise_model=noise_model)
result = job.result()

counts = result.get_counts()
print("Measurement results:", counts)


ideal_probs = {'0': 0.5, '1': 0.5}

measured_probs = {k: v/shots for k, v in counts.items()}

approx_fidelity = sum(np.sqrt(ideal_probs[k] * measured_probs.get(k, 0)) for k in ideal_probs)

print("Approximate fidelity (from counts):", approx_fidelity)
