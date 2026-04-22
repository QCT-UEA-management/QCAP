
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
if not backends:
    raise RuntimeError(f"No backend named '{backend_name}' found via MQSS.")
[backend] = backends

# Construct two circuits

circuit_1 = QuantumCircuit(2)
circuit_1.h(0)
circuit_1.cx(0, 1)
circuit_1.measure_all()

circuit_2 = QuantumCircuit(2)
circuit_2.h(0)
circuit_2.x(1)
circuit_2.cx(0, 1)
circuit_2.measure_all()

transpiled_qcs = transpile([circuit_1, circuit_2], backend=backend, initial_layout=[0, 2])
job = backend.run(transpiled_qcs, shots=10)
print(job.result().get_counts())
