from pyscf import gto, scf, fci as pyscf_fci
from qiskit_nature.units import DistanceUnit
from qiskit_nature.second_q.drivers import PySCFDriver
from qiskit_nature.second_q.mappers import JordanWignerMapper

# H2 at equilibrium bond length, STO-3G minimal basis, singlet ground state
GEOMETRY = "H 0 0 0; H 0 0 0.735"
BASIS = "sto-3g"
CHARGE = 0
SPIN = 0  # 2S


def build_hamiltonian():
    """Return the qiskit_nature ElectronicStructureProblem and the JW qubit Hamiltonian.

    The qubit_op eigenvalues are electronic energies only.
    Add problem.nuclear_repulsion_energy to obtain total energies.
    """
    driver = PySCFDriver(
        atom=GEOMETRY,
        basis=BASIS,
        charge=CHARGE,
        spin=SPIN,
        unit=DistanceUnit.ANGSTROM,
    )
    problem = driver.run()
    mapper = JordanWignerMapper()
    qubit_op = mapper.map(problem.hamiltonian.second_q_op())
    return problem, qubit_op


def get_reference_energy():
    """Return the PySCF FCI total energy (electronic + nuclear repulsion) in Hartree."""
    mol = gto.Mole()
    mol.atom = GEOMETRY
    mol.basis = BASIS
    mol.charge = CHARGE
    mol.spin = SPIN
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
