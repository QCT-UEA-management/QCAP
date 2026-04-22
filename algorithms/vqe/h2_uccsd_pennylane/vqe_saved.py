import math
import pennylane as qml
from pennylane import numpy as np
from pennylane.transforms import decompose
from scipy.optimize import minimize
from mqss.pennylane_adapter.device import MQSSPennylaneDevice
from pennylane.transforms import decompose
from functools import partial

def build_h2_problem():
    # H2 at 0.735 Angstrom, STO-3G basis
    symbols = ["H", "H"]
    geometry = np.array(
        [
            [0.0, 0.0, 0.0],
            [0.0, 0.0, 0.735],
        ],
        requires_grad=False,
    )

    mol = qml.qchem.Molecule(
        symbols,
        geometry,
        charge=0,
        mult=1,
        basis_name="sto-3g",
        unit="Angstrom",
    )

    H, n_qubits = qml.qchem.molecular_hamiltonian(mol, method="dhf")
    n_electrons = 2
    hf_state = qml.qchem.hf_state(n_electrons, n_qubits)
    singles, doubles = qml.qchem.excitations(n_electrons, n_qubits)
    s_wires, d_wires = qml.qchem.excitations_to_wires(singles, doubles)
    n_params = len(singles) + len(doubles)
    return H, n_qubits, hf_state, s_wires, d_wires, n_params


def exact_ground_energy(H, n_qubits):
    mat = qml.matrix(H, wire_order=range(n_qubits))
    evals = np.linalg.eigvalsh(mat)
    return float(evals[0])


def make_ansatz(hf_state, s_wires, d_wires, n_qubits):
    def ansatz(theta):
        qml.UCCSD(
            weights=theta,
            wires=range(n_qubits),
            s_wires=s_wires,
            d_wires=d_wires,
            init_state=hf_state,
        )
    return ansatz


def main():
    # ---- Build chemistry problem with PennyLane only ----
    H, n_qubits, hf_state, s_wires, d_wires, n_params = build_h2_problem()

    e_exact = exact_ground_energy(H, n_qubits)
    print(f"Exact electronic ground energy (diag) = {e_exact:.12f} Ha\n")
    print(f"Number of qubits = {n_qubits}")
    print(f"Number of VQE parameters = {n_params}\n")

    # ---- Devices ----
    dev_backend = MQSSPennylaneDevice(
        wires=n_qubits,
        token="token",
        backends="EQE1"
        #shots=num_shots  
    )

    dev_ideal = qml.device("default.qubit", wires=n_qubits)

    ansatz = make_ansatz(hf_state, s_wires, d_wires, n_qubits) 

    #NATIVE_GATES = [qml.RX, qml.RZ, qml.CZ]

    # IQM-native gate set (approximation using PennyLane gates)
    #@partial(qml.transforms.decompose, gate_set=NATIVE_GATES)
    @qml.qnode(dev_backend)
    def energy_backend(theta):
        ansatz(theta)
        return qml.expval(H)

    #@partial(qml.transforms.decompose, gate_set=NATIVE_GATES)
    @qml.qnode(dev_ideal)
    def energy_ideal(theta):
        ansatz(theta)
        return qml.expval(H)

    def objective(theta):
        theta = np.array(theta, dtype=float, requires_grad=False)
        e_b = float(energy_backend(theta))
        e_i = float(energy_ideal(theta))

        print(
            f"params = {theta}  | "
            f"E_backend = {e_b:.8f} Ha | "
            f"E_ideal(sv) = {e_i:.8f} Ha | "
            f"|Δ| = {abs(e_b - e_i):.6f}"
        )

        return e_b

    # Random initialization of parameters
    theta0 = np.random.uniform(0, 2 * np.pi, size=(n_params,), requires_grad=False)
    theta_test = np.zeros(n_params)
    print(qml.draw(energy_ideal)(theta_test))
    theta_test = np.zeros(n_params)
    print("backend energy:", energy_backend(theta_test))
    print("ideal energy:", energy_ideal(theta_test))

    
    '''
    result = minimize(
        objective,
        x0=np.array(theta0, dtype=float),
        method="COBYLA",
        options={"maxiter": 2},
    )

    print("\n=== FINAL VQE RESULT ===")
    print("Optimized parameters:", result.x)
    print(f"Energy (backend): {result.fun} Ha")
    print(f"Energy (exact  ): {e_exact:.12f} Ha")
    '''


if __name__ == "__main__":
    main()