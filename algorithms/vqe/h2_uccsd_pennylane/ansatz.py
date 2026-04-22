import pennylane as qml


def build_ansatz(hf_state, s_wires, d_wires, n_qubits):
    """Return a callable that applies the UCCSD ansatz to the active circuit.

    Parameters
    ----------
    hf_state : array
        Hartree-Fock occupation bitstring from qml.qchem.hf_state.
    s_wires : list
        Wire pairs for single excitations.
    d_wires : list
        Wire quadruples for double excitations.
    n_qubits : int

    Returns
    -------
    ansatz : callable
        ansatz(params) applies qml.UCCSD; len(params) == len(s_wires) + len(d_wires).
    """
    def ansatz(params):
        qml.UCCSD(
            weights=params,
            wires=range(n_qubits),
            s_wires=s_wires,
            d_wires=d_wires,
            init_state=hf_state,
        )

    return ansatz
