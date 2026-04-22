import numpy as np
import pennylane as qml
from pyscf import gto, scf, fci as pyscf_fci

SYMBOLS = ["H", "H"]
GEOMETRY = np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 0.735]])  # Angstrom
BASIS = "sto-3g"
CHARGE = 0
MULT = 1
N_ELECTRONS = 2


def build_hamiltonian():
    """Return the PennyLane electronic Hamiltonian and all VQE building blocks.

    qml.qchem.molecular_hamiltonian includes nuclear repulsion as a constant
    term, so qml.expval(H) gives the total energy directly.  nuclear_repulsion
    is returned separately for display purposes only.

    Returns
    -------
    H : qml.Hamiltonian
        Electronic Hamiltonian in the Jordan-Wigner basis.
    n_qubits : int
    hf_state : array
        Hartree-Fock occupation bitstring.
    s_wires : list
        Wire pairs for single excitations.
    d_wires : list
        Wire quadruples for double excitations.
    nuclear_repulsion : float
        Nuclear repulsion energy in Hartree.
    """
    mol = qml.qchem.Molecule(
        SYMBOLS,
        GEOMETRY,
        charge=CHARGE,
        mult=MULT,
        basis_name=BASIS,
        unit="Angstrom",
    )
    H, n_qubits = qml.qchem.molecular_hamiltonian(mol, method="dhf")

    hf_state = qml.qchem.hf_state(N_ELECTRONS, n_qubits)
    singles, doubles = qml.qchem.excitations(N_ELECTRONS, n_qubits)
    s_wires, d_wires = qml.qchem.excitations_to_wires(singles, doubles)

    nuclear_repulsion = _nuclear_repulsion()
    return H, n_qubits, hf_state, s_wires, d_wires, nuclear_repulsion


def _nuclear_repulsion():
    mol = gto.Mole()
    mol.atom = "H 0 0 0; H 0 0 0.735"
    mol.basis = BASIS
    mol.charge = CHARGE
    mol.spin = 0
    mol.unit = "Angstrom"
    mol.verbose = 0
    mol.build()
    return mol.energy_nuc()


def get_reference_energy():
    """Return the PySCF FCI total energy (electronic + nuclear repulsion) in Hartree."""
    mol = gto.Mole()
    mol.atom = "H 0 0 0; H 0 0 0.735"
    mol.basis = BASIS
    mol.charge = CHARGE
    mol.spin = 0
    mol.unit = "Angstrom"
    mol.verbose = 0
    mol.build()

    mf = scf.RHF(mol)
    mf.verbose = 0
    mf.run()

    solver = pyscf_fci.FCI(mf)
    solver.verbose = 0
    e_fci, _ = solver.kernel()
    return e_fci
