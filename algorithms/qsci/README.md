# QSCI — Quantum-Selected Configuration Interaction

A quantum-classical hybrid algorithm for ground- and excited-state energy
calculations in quantum chemistry, using quantum computers to select the
most important electron configurations for a classical diagonalization.

---

## Overview

**QSCI** addresses a core challenge in electronic structure theory: identifying
which electron configurations matter most for representing the ground state.
Classical Selected CI (SCI) methods struggle to find these configurations
efficiently for strongly correlated systems. Quantum computers, by contrast,
naturally produce measurement distributions concentrated on the important
configurations.

The key insight is that a quantum device is used *only* to define a subspace
$\mathcal{S}$. All energy computation happens classically inside that subspace,
making the method robust to quantum noise: errors in the quantum state shift
which configurations are selected, but cannot violate the variational principle
within the chosen subspace.

## Algorithm

1. Prepare an approximate ground state $|\psi\rangle$ on a quantum device
   (e.g. via VQE, adiabatic state preparation, or Hamiltonian time evolution).
2. Sample $|\psi\rangle$ in the computational basis for $n_\text{shots}$
   measurements.
3. Select the $R$ most frequently observed bitstrings
   $\mu_1, \ldots, \mu_R$ — each represents a Slater determinant.
4. Define the CI subspace:
$$\mathcal{S} = \mathrm{span}\{|\mu_1\rangle, \ldots, |\mu_R\rangle\}$$
5. Build and diagonalize the projected Hamiltonian classically:
$$(H_\mathcal{S})_{kl} = \langle\mu_k|\hat{H}|\mu_l\rangle \quad
\rightarrow \quad E_0, \, |\Psi_0\rangle$$

Excited states are obtained analogously by targeting higher eigenvectors.

## Key Properties

- **Noise robustness:** the quantum device only defines the subspace;
  the energy is computed by exact classical diagonalization and satisfies
  the variational principle.
- **Flexible state preparation:** works with any method that produces a
  reasonable approximate ground state — VQE, UCCSD, time evolution, LUCJ
  ansatz, etc.
- **Scalable classical post-processing:** subspace diagonalization cost
  scales with $R$, not with the full Hilbert space dimension.
- **Ground and excited states:** the subspace Hamiltonian yields the full
  low-energy spectrum within $\mathcal{S}$.

## References

[1] Kanno *et al.*, *"Quantum-Selected Configuration Interaction: classical
diagonalization of Hamiltonians in subspaces selected by quantum computers"*,
arXiv:2302.11320 (2023).
<https://arxiv.org/abs/2302.11320>