from qiskit_nature.second_q.circuit.library import HartreeFock, UCCSD
from qiskit_nature.second_q.mappers import JordanWignerMapper


def build_ansatz(problem):
    """Return UCCSD ansatz initialised from the Hartree-Fock state.

    Parameters
    ----------
    problem : ElectronicStructureProblem
        Returned by molecule.build_hamiltonian().

    Returns
    -------
    QuantumCircuit
        Parametrised UCCSD circuit. Parameters are accessible via ansatz.parameters.
    """
    mapper = JordanWignerMapper()
    hf_state = HartreeFock(
        problem.num_spatial_orbitals,
        problem.num_particles,
        mapper,
    )
    ansatz = UCCSD(
        problem.num_spatial_orbitals,
        problem.num_particles,
        mapper,
        initial_state=hf_state,
    )
    return ansatz
