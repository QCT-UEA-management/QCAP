"""VQE for H2 / UCCSD — LRZ QPU via Qiskit MQSS adapter.

Backend  : LRZ IQM QPU accessed through the Munich Quantum Software Stack (MQSS).
Optimizer: COBYLA (gradient-free).
Mapping  : Jordan-Wigner, 4 qubits.
Basis    : STO-3G.

Credentials
-----------
Copy .env.example at the repo root to .env and fill in MQSS_TOKEN.
The script loads it automatically via python-dotenv.

Set MQSS_BACKEND in .env (e.g. EQE1).
See backends/qiskit_lrz_mqss.md for full setup instructions.

Error mitigation
----------------
This runner targets real hardware. When error mitigation demonstrably improves
accuracy for this workflow, add it here. Currently none is applied.
"""

import os
import sys
import warnings
import numpy as np
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# qiskit_nature triggers scipy sparse efficiency hints that are not actionable here
warnings.filterwarnings("ignore", module=r"scipy\.sparse")
from scipy.optimize import minimize
from qiskit import transpile
from qiskit.primitives import BackendEstimatorV2

from molecule import build_hamiltonian, get_reference_energy
from ansatz import build_ansatz

# ── Credentials and backend ────────────────────────────────────────────────────
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

from mqss.qiskit_adapter import MQSSQiskitAdapter
adapter = MQSSQiskitAdapter(token=token)
backends = adapter.backends(name=backend_name)
if not backends:
    raise RuntimeError(f"No backend named '{backend_name}' found via MQSS.")
backend = backends[0]

# ── Chemistry setup ────────────────────────────────────────────────────────────
SHOTS_PRECISION = 0.005  # ~40 000 shots per expectation value

problem, qubit_op = build_hamiltonian()
nuclear_repulsion = problem.nuclear_repulsion_energy
ansatz = build_ansatz(problem)

print("=" * 60)
print(f"H2 / UCCSD / STO-3G — LRZ QPU VQE  [{backend_name}]")
print("=" * 60)
print(f"  Qubits       : {qubit_op.num_qubits}")
print(f"  Parameters   : {ansatz.num_parameters}")
print(f"  Nuclear rep. : {nuclear_repulsion:.10f} Ha")
print(f"  Precision    : {SHOTS_PRECISION} Ha (target std-dev per expectation)")

# ── Classical reference ────────────────────────────────────────────────────────
e_fci = get_reference_energy()
print(f"  PySCF FCI    : {e_fci:.10f} Ha")
print()

# ── Transpile once to the backend native gate set ──────────────────────────────
# Transpile the parametric ansatz (parameters left unbound) so the layout is
# fixed for every iteration.  Binding happens on the already-transpiled circuit,
# avoiding a per-iteration re-transpile that can shift qubit indices and break
# BackendEstimatorV2's internal expval map.
x0 = np.zeros(ansatz.num_parameters)
transpiled = transpile(ansatz, backend=backend, optimization_level=3)
qubit_op_isa = qubit_op.apply_layout(transpiled.layout)

estimator = BackendEstimatorV2(backend=backend)
iteration = [0]


def cost_fn(params):
    bound = transpiled.assign_parameters(dict(zip(transpiled.parameters, params)))

    job = estimator.run([(bound, qubit_op_isa)], precision=SHOTS_PRECISION)
    e_total = float(job.result()[0].data.evs)
    
    iteration[0] += 1
    print(f"  iter {iteration[0]:4d}  E_total = {e_total:.8f} Ha", end="\r", flush=True)
    return e_total


result = minimize(
    cost_fn,
    x0,
    method="COBYLA",
    options={"maxiter": 3, "rhobeg": 0.3},
)

e_vqe_total = result.fun

print()
print()
print("=" * 60)
print("RESULTS")
print("=" * 60)
print(f"  VQE energy   : {e_vqe_total:.8f} Ha")
print(f"  PySCF FCI    : {e_fci:.10f} Ha")
print(f"  Error        : {abs(e_vqe_total - e_fci):.4f} Ha")
print(f"  Iterations   : {result.nfev}")
print("=" * 60)
