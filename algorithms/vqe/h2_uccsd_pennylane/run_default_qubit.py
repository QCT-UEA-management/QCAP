"""VQE for H2 / UCCSD — exact statevector simulation with PennyLane.

Backend  : default.qubit (exact statevector, no shot noise).
Optimizer: COBYLA (gradient-free).
Mapping  : Jordan-Wigner, 4 qubits (via qml.qchem).
Basis    : STO-3G.

For H2 with 2 electrons in a minimal basis, UCCSD is exact (= FCI).
The VQE energy should match the PySCF FCI reference to within optimizer
convergence tolerance.
"""

import sys
import numpy as np
from scipy.optimize import minimize
import pennylane as qml

from molecule import build_hamiltonian, get_reference_energy
from ansatz import build_ansatz

# ── Chemistry setup ────────────────────────────────────────────────────────────
H, n_qubits, hf_state, s_wires, d_wires, nuclear_repulsion = build_hamiltonian()
ansatz = build_ansatz(hf_state, s_wires, d_wires, n_qubits)
n_params = len(s_wires) + len(d_wires)

print("=" * 60)
print("H2 / UCCSD / STO-3G — default.qubit VQE")
print("=" * 60)
print(f"  Qubits       : {n_qubits}")
print(f"  Parameters   : {n_params}")
print(f"  Nuclear rep. : {nuclear_repulsion:.10f} Ha")
print()

# ── VQE ────────────────────────────────────────────────────────────────────────
dev = qml.device("default.qubit", wires=n_qubits)

@qml.qnode(dev)
def circuit(params):
    ansatz(params)
    return qml.expval(H)


iteration = [0]


def cost_fn(params):
    e_total = float(circuit(np.array(params)))
    iteration[0] += 1
    print(f"  iter {iteration[0]:4d}  E_total = {e_total:.10f} Ha", end="\r", flush=True)
    return e_total


x0 = np.zeros(n_params)
result = minimize(
    cost_fn,
    x0,
    method="COBYLA",
    options={"maxiter": 500, "rhobeg": 0.5, "catol": 1e-8},
)

e_vqe_total = result.fun
e_fci = get_reference_energy()

print(" " * 60, end="\r", flush=True)
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
