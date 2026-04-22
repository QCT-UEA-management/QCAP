import os
from dotenv import load_dotenv, find_dotenv
from qiskit import QuantumCircuit, compiler
from mqss.qiskit_adapter import MQSSQiskitAdapter

from job_wait import wait_for_job

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

# --- Circuit 1: Bell state ---
c1 = QuantumCircuit(2, 2, name="bell")
c1.h(0)
c1.cx(0, 1)
c1.measure([0, 1], [0, 1])

# --- Circuit 2: Simple different circuit ---
c2 = QuantumCircuit(2, 2, name="only_h")
c2.h(0)
c2.measure([0, 1], [0, 1])

# Transpile both at once
tc1, tc2 = compiler.transpile([c1, c2], backend, optimization_level=3)

job = None
try:
    job = backend.run([tc1, tc2], shots=1000, no_modify=True)
    result = wait_for_job(job, backend=backend)
    counts1 = result.get_counts(0)
    counts2 = result.get_counts(1)
    print("Counts for circuit 1 (bell):", counts1)
    print("Counts for circuit 2 (only_h):", counts2)
except KeyboardInterrupt:
    print("Interrupted by user.")
    if job is not None:
        try:
            job.cancel()
            print("Remote job cancelled.")
        except Exception as exc:
            print(f"Failed to cancel remote job: {exc}")
    raise
