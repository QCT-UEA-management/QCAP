import os
from dotenv import load_dotenv, find_dotenv
from qiskit import QuantumCircuit, transpile
from mqss.qiskit_adapter import MQSSQiskitAdapter

from job_wait import wait_for_job

load_dotenv(find_dotenv())


def main():
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

    circuit = QuantumCircuit(2, 2)
    circuit.h(0)
    circuit.cx(0, 1)
    circuit.measure([0, 1], [0, 1])

    transpiled_circuit = transpile(circuit, backend, optimization_level=3)

    job = None
    try:
        job = backend.run(transpiled_circuit, shots=1000, no_modify=True)
        result = wait_for_job(job, backend=backend, poll_interval=5.0, verbose=True)
        counts = result.get_counts(0)
        print("Measurement counts:", counts)
    except KeyboardInterrupt:
        print("Interrupted by user.")
        if job is not None:
            try:
                job.cancel()
                print("Remote job cancelled.")
            except Exception as exc:
                print(f"Failed to cancel remote job: {exc}")
        raise


if __name__ == "__main__":
    main()
