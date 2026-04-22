
import os
import time
from dotenv import load_dotenv, find_dotenv
from qiskit import QuantumCircuit, compiler
from qiskit.providers.jobstatus import JobStatus
from mqss.qiskit_adapter import MQSSQiskitAdapter
from qiskit import QuantumCircuit, transpile

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
[backend] = backends

# Construct two circuits

circuit = QuantumCircuit(2, 2)
circuit.h(0)
circuit.cx(0, 1)
circuit.measure([0, 1], [0, 1])

job = backend.run(circuit, shots=10)
result = job.result()
counts = result.get_counts()
print("Measurement counts:", counts)
