
# VQE — Variational Quantum Eigensolver

A quantum-classical hybrid algorithm for ground-state energy calculations in quantum chemistry, using a parameterized quantum circuit optimized via classical minimization.


## Overview

**VQE** estimates the ground-state energy of a molecular Hamiltonian $\hat{H}$ by exploiting the **variational principle**: for any normalized trial state $\ket{\psi(\boldsymbol{\theta})}$, the expectation value of the Hamiltonian provides an upper bound on the true ground-state energy $E_0$:

$$ E(\boldsymbol{\theta}) = \bra{\psi(\boldsymbol{\theta})} \hat{H} \ket{\psi(\boldsymbol{\theta})} \geq E_0 $$

A parameterized quantum circuit (ansatz) prepares $\ket{\psi(\boldsymbol{\theta})}$ on a quantum device. A classical optimizer iteratively updates the parameters $\boldsymbol{\theta}$ to minimize $E(\boldsymbol{\theta})$, driving the trial state toward the true ground state.

## Algorithm

1. Choose an **ansatz** $U(\boldsymbol{\theta})$ — a parameterized quantum circuit suited to the target molecule (e.g., hardware-efficient, UCCSD).
2. Prepare the trial state $\ket{\psi(\boldsymbol{\theta})} = U(\boldsymbol{\theta})\ket{\psi_I}$ on a quantum device, starting from a reference state $\ket{\psi_I}$ (e.g., Hartree-Fock).
3. Measure the energy $E(\boldsymbol{\theta}) = \bra{\psi(\boldsymbol{\theta})}\hat{H}\ket{\psi(\boldsymbol{\theta})}$ by decomposing $\hat{H}$ into a sum of Pauli operators and estimating each term via repeated circuit executions.
4. Pass $E(\boldsymbol{\theta})$ to a classical optimizer (e.g., COBYLA, gradient descent, SPSA), which proposes an updated parameter vector $\boldsymbol{\theta}' \leftarrow \boldsymbol{\theta}$.
5. Repeat steps 2–4 until convergence: $\min_{\boldsymbol{\theta}} E(\boldsymbol{\theta}) \approx E_0$.

## Hamiltonian Decomposition

The molecular Hamiltonian is expressed in second quantization and mapped to qubit operators via a fermion-to-qubit transformation (e.g., Jordan-Wigner, Bravyi-Kitaev):

$$ \hat{H} = \sum_j c_j \hat{P}_j, \quad \hat{P}_j \in {I, X, Y, Z}^{\otimes n} $$

Each Pauli term $\hat{P}_j$ is measured independently, and the energy is reconstructed as:

$$ E(\boldsymbol{\theta}) = \sum_j c_j \langle \hat{P}_j \rangle_{\boldsymbol{\theta}} $$


## References

[1] Alberto Peruzzo et al., _"A variational eigenvalue solver on a photonic chip"_, **Nature Communications 5**, 4213 (2014). [https://doi.org/10.1038/ncomms5213](https://doi.org/10.1038/ncomms5213)

[2] Jarrod R. McClean et al., _"The theory of variational hybrid quantum-classical algorithms"_, **New Journal of Physics 18**, 023023 (2016). [https://doi.org/10.1088/1367-2630/18/2/023023](https://doi.org/10.1088/1367-2630/18/2/023023)

[3] Jules Tilly et al., _"The Variational Quantum Eigensolver: A review of methods and best practices"_, **Physics Reports 986**, 1–128 (2022). [https://doi.org/10.1016/j.physrep.2022.08.003](https://doi.org/10.1016/j.physrep.2022.08.003)