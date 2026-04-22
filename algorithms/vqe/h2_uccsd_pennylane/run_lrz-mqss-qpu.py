"""VQE for H2 / UCCSD — LRZ QPU via PennyLane MQSS adapter.

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

Note
----
qml.qchem.molecular_hamiltonian includes nuclear repulsion as a constant term,
so qml.expval(H) returns the total energy directly. nuclear_repulsion is used
for display purposes only.

Error mitigation
----------------
This runner targets real hardware. When error mitigation demonstrably improves
accuracy for this workflow, add it here. Currently none is applied.
"""

import os
import numpy as np
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

from scipy.optimize import minimize
import pennylane as qml
from mqss.pennylane_adapter.device import MQSSPennylaneDevice

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

# ── Chemistry setup ────────────────────────────────────────────────────────────
SHOTS = 40000  # ~equivalent to precision=0.005 Ha in the Qiskit runner

H, n_qubits, hf_state, s_wires, d_wires, nuclear_repulsion = build_hamiltonian()
n_params = len(s_wires) + len(d_wires)
ansatz = build_ansatz(hf_state, s_wires, d_wires, n_qubits)

print("=" * 60)
print(f"H2 / UCCSD / STO-3G — LRZ QPU VQE  [{backend_name}]")
print("=" * 60)
print(f"  Qubits       : {n_qubits}")
print(f"  Parameters   : {n_params}")
print(f"  Nuclear rep. : {nuclear_repulsion:.10f} Ha")
print(f"  Shots        : {SHOTS}")

# ── Classical reference ────────────────────────────────────────────────────────
e_fci = get_reference_energy()
print(f"  PySCF FCI    : {e_fci:.10f} Ha")
print()

# ── Device and QNode ──────────────────────────────────────────────────────────
dev = MQSSPennylaneDevice(
    wires=n_qubits,
    token=token,
    backends=backend_name,
    shots=SHOTS,
)


@qml.qnode(dev)
def energy_circuit(params):
    ansatz(params)
    return qml.expval(H)


# ── Optimization ───────────────────────────────────────────────────────────────
x0 = np.zeros(n_params)
iteration = [0]


def cost_fn(params):
    # qml.expval(H) includes nuclear repulsion, so this is already total energy
    e_total = float(energy_circuit(np.array(params, dtype=float)))

    iteration[0] += 1
    print(f"  iter {iteration[0]:4d}  E_total = {e_total:.8f} Ha", end="\r", flush=True)
    return e_total


result = minimize(
    cost_fn,
    x0,
    method="COBYLA",
    options={"maxiter": 5, "rhobeg": 0.3},
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
