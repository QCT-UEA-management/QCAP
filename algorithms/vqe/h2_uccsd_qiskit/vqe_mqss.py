import math
import numpy as np
from qiskit import transpile
from qiskit.primitives import BackendEstimatorV2
from qiskit.quantum_info import Statevector
from qiskit_nature.units import DistanceUnit
from qiskit_nature.second_q.drivers import PySCFDriver
from qiskit_nature.second_q.circuit.library import HartreeFock, UCCSD
from qiskit_nature.second_q.mappers import JordanWignerMapper
from mqss.qiskit_adapter import MQSSQiskitAdapter


def estimate_required_shots(precision, variance=1.0):
    if precision <= 0:
        raise ValueError("precision must be > 0")
    return math.ceil(variance / (precision ** 2))


def build_h2_problem():
    driver = PySCFDriver(
        atom="H 0 0 0; H 0 0 0.735",
        basis="sto3g",
        charge=0,
        spin=0,
        unit=DistanceUnit.ANGSTROM,
    )
    es_problem = driver.run()

    mapper = JordanWignerMapper()
    second_q_op = es_problem.hamiltonian.second_q_op()
    qubit_op = mapper.map(second_q_op)  # typically a SparsePauliOp

    ansatz = UCCSD(
        es_problem.num_spatial_orbitals,
        es_problem.num_particles,
        mapper,
        initial_state=HartreeFock(
            es_problem.num_spatial_orbitals,
            es_problem.num_particles,
            mapper,
        ),
    )
    return es_problem, qubit_op, ansatz


def ideal_expectation(bound_circuit, qubit_op):
    sv = Statevector.from_instruction(bound_circuit)
    ev = sv.expectation_value(qubit_op)
    return float(ev.real)


def backend_expectation(bound_circuit, qubit_op, backend, precision=0.01, opt_level=3):
    # 1) Transpile circuit for backend
    tqc = transpile(bound_circuit, backend=backend, optimization_level=opt_level)

    # 2) Map operator to transpiled layout (same idea as your first script)
    H_isa = qubit_op.apply_layout(tqc.layout)

    # 3) Estimator run
    estimator = BackendEstimatorV2(backend=backend)
    job = estimator.run([(tqc, H_isa)], precision=precision)
    pub = job.result()[0]
    return float(pub.data.evs), pub.metadata


def exact_ground_energy(qubit_op):
    # Works for small qubit Hamiltonians (H2 sto-3g is small)
    H = qubit_op.to_matrix(sparse=False)
    evals = np.linalg.eigvalsh(H)
    return float(evals[0].real)


def main():
    # ---- MQSS backend ----
    adapter = MQSSQiskitAdapter(token="<api-token>")
    [backend] = adapter.backends(name="<resource-name>")

    # ---- Build chemistry problem ----
    es_problem, qubit_op, ansatz = build_h2_problem()

    print("\n--- Qubit Hamiltonian ---")
    print(qubit_op)
    print()

    # Optional: exact reference energy (electronic, in Hartree)
    e_exact = exact_ground_energy(qubit_op)
    print(f"Exact electronic ground energy (diag) = {e_exact:.12f} Ha\n")

    # ---- Simple VQE loop (COBYLA) using Estimator expectations ----
    ansatz_params = list(ansatz.parameters)
    n = len(ansatz_params)
    print(f"Number of VQE parameters = {n}\n")

    precision = 0.01
    shots_est = estimate_required_shots(precision=precision, variance=1.0)
    print(f"Requested precision = {precision}")
    print(f"Estimated shots (worst-case) ≈ {shots_est}\n")

    from scipy.optimize import minimize

    def energy(theta):
        theta = np.asarray(theta, dtype=float)
        bound = ansatz.assign_parameters({p: v for p, v in zip(ansatz_params, theta)})

        e_ideal = ideal_expectation(bound, qubit_op)
        e_backend, meta = backend_expectation(bound, qubit_op, backend, precision=precision)

        print(f"E_backend = {e_backend:.12f} Ha | E_ideal(sv) = {e_ideal:.12f} Ha | |Δ| = {abs(e_backend-e_ideal):.6f}")
        # If you want to see estimator metadata each call, uncomment:
        # print("  metadata:", meta)

        return e_backend

    #theta0 = np.zeros(n)
    theta0 = np.random.uniform(0, 2 * np.pi, size=n)
    result = minimize(energy, theta0, method="COBYLA", options={"maxiter": 5})

    print("\n=== FINAL VQE RESULT ===")
    print("Optimized parameters:", result.x)
    print("Minimum energy (backend):", result.fun)
    print(f"Exact electronic ground energy (diag): {e_exact:.12f} Ha")


if __name__ == "__main__":
    main()