# GHZ State generation and measurement

import os
import matplotlib.pyplot as plt
from dotenv import load_dotenv, find_dotenv
from mqss.qiskit_adapter import MQSSQiskitAdapter
from qiskit import QuantumCircuit, transpile
from qiskit.visualization import plot_histogram

load_dotenv(find_dotenv())

token = os.environ.get("MQSS_TOKEN")
if not token:
    raise RuntimeError(
        "MQSS_TOKEN environment variable is not set.\n"
        "See README.md for setup instructions."
    )

backend_name = os.environ.get("MQSS_BACKEND")
if not backend_name:
    raise RuntimeError(
        "MQSS_BACKEND environment variable is not set.\n"
        "See README.md for setup instructions."
    )

adapter = MQSSQiskitAdapter(token=token)
backends = adapter.backends(name=backend_name)
if not backends:
    raise RuntimeError(f"No backend named '{backend_name}' found via MQSS.")
backend = backends[0]

# Parameters
qubits = 3
shots = 10

# Build GHZ circuit
qc = QuantumCircuit(qubits, qubits)
qc.h(0)
for i in range(1, qubits):
    qc.cx(0, i)
qc.measure_all(add_bits=False)

# Transpile if needed
trans_qc = transpile(qc, backend, optimization_level=3)

# Run job
job = backend.run(trans_qc, no_modify=True, shots=shots, queued=True)
counts = job.result().get_counts()
print("Result:", counts)
