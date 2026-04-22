
# TE-QSCI — Time-Evolved Quantum-Selected Configuration Interaction

A quantum-classical hybrid algorithm for ground-state energy calculations in quantum chemistry, using time-evolved quantum states as input to Selected Configuration Interaction (SCI) on classical computers.


## Overview

**TE-QSCI** eliminates the need for variational circuit optimization (as in VQE or ADAPT-QSCI) by preparing the QSCI input state via Hamiltonian time evolution. The time-evolution operator naturally generates electron excitations of increasing order over an initial reference state:

$$ \ket{\psi(t)} = e^{-i\hat{H}t} \ket{\psi_I} = \ket{\psi_I} - i\hat{H}t\ket{\psi_I} + \frac{(-i\hat{H}t)^2}{2}\ket{\psi_I} + \cdots $$

Since $\hat{H}$ contains up to second-order excitation operators, the $k$-th order term generates excitations up to order $2k$ over $\ket{\psi_I}$, producing a measurement distribution that captures the important configurations for the CI subspace.



## Algorithm

1. Prepare the initial state $\ket{\psi_I}$ on a quantum device (e.g. Hartree-Fock or UCCSD).
2. Apply the time-evolution operator to obtain $\ket{\psi(t)} = e^{-i\hat{H}t}\ket{\psi_I}$.
3. Sample $\ket{\psi(t)}$ in the computational basis for $n_\text{shots}$ measurements.
4. Select the $R$ most frequent bitstrings $\mu_1, \ldots, \mu_R$ $\rightarrow$ defines subspace $\mathcal{S} = \mathrm{span}{\ket{\mu_1}, \ldots, \ket{\mu_R}}$.
5. Diagonalize the projected Hamiltonian $(H_\mathcal{S})_{kl} = \bra{\mu_k}\hat{H}\ket{\mu_l}$ classically $\rightarrow$ ground-state energy.




## References

[1] Mathias Mikkelsen and Yuya O. Nakagawa, _"Quantum-selected configuration interaction with time-evolved state"_, **Physical Review Research 7**, 043043 (2025). [https://doi.org/10.1103/75pv-hbrx](https://doi.org/10.1103/75pv-hbrx)