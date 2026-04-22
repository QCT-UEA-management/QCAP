"""VQE for H2 / UCCSD — exact statevector simulation.

Backend  : StatevectorEstimator (qiskit.primitives) — exact, no shot noise.
Optimizer: COBYLA (gradient-free).
Mapping  : Jordan-Wigner, 4 qubits.
Basis    : STO-3G.

For H2 with 2 electrons in a minimal basis, UCCSD is exact (= FCI).
The VQE energy should therefore match the PySCF FCI reference to within
optimizer convergence tolerance.
"""

import sys
import warnings
import numpy as np

# qiskit_nature triggers scipy sparse efficiency hints that are not actionable here
warnings.filterwarnings("ignore", module=r"scipy\.sparse")
from scipy.optimize import minimize
from qiskit.primitives import StatevectorEstimator

from molecule import build_hamiltonian, get_reference_energy
from ansatz import build_ansatz

# ── Chemistry setup ────────────────────────────────────────────────────────────
problem, qubit_op = build_hamiltonian()
nuclear_repulsion = problem.nuclear_repulsion_energy
ansatz = build_ansatz(problem)

print("=" * 60)
print("H2 / UCCSD / STO-3G — Statevector VQE")
print("=" * 60)
print(f"  Qubits       : {qubit_op.num_qubits}")
print(f"  Parameters   : {ansatz.num_parameters}")
print(f"  Nuclear rep. : {nuclear_repulsion:.10f} Ha")
print()

# ── VQE ────────────────────────────────────────────────────────────────────────
estimator = StatevectorEstimator()
iteration = [0]


def cost_fn(params):
    job = estimator.run([(ansatz, qubit_op, params)])
    e_elec = float(job.result()[0].data.evs)
    e_total = e_elec + nuclear_repulsion
    iteration[0] += 1
    print(f"  iter {iteration[0]:4d}  E_total = {e_total:.10f} Ha", end="\r", flush=True)
    return e_elec


x0 = np.zeros(ansatz.num_parameters)
result = minimize(
    cost_fn,
    x0,
    method="COBYLA",
    options={"maxiter": 500, "rhobeg": 0.5, "catol": 1e-8},
)

e_vqe_total = result.fun + nuclear_repulsion
e_fci = get_reference_energy()

print(" " * 60, end="\r", flush=True)  # clear the progress line
print()
print("=" * 60)
print("RESULTS")
print("=" * 60)
print(f"  VQE energy   : {e_vqe_total:.10f} Ha")
print(f"  PySCF FCI    : {e_fci:.10f} Ha")
print(f"  Error        : {abs(e_vqe_total - e_fci):.2e} Ha")
print(f"  Converged    : {result.success}")
print(f"  Iterations   : {result.nfev}")
print("=" * 60)

if abs(e_vqe_total - e_fci) > 1e-4:
    print("WARNING: VQE did not converge to chemical accuracy (1 mHa).", file=sys.stderr)
