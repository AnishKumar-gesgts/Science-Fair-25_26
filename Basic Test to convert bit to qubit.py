from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer

# Binary string input
binary_input = "101"

# Create quantum circuit with one qubit per bit
qc = QuantumCircuit(len(binary_input), len(binary_input))

# Set qubits according to binary input
for i, bit in enumerate(binary_input):
    if bit == '1':
        qc.x(i)  # Flip |0> to |1> for bit 1

# Measure all qubits
qc.measure(range(len(binary_input)), range(len(binary_input)))

# Use Aer simulator
simulator = Aer.get_backend('qasm_simulator')

# Transpile the circuit for the backend
tqc = transpile(qc, simulator)

# Run the circuit with 1024 shots
job = simulator.run(tqc, shots=1024)
result = job.result()

# Get counts
counts = result.get_counts()
print(counts)
