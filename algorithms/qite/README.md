# QITE: Quantum Imaginary Time Evolution

A quantum algorithm for determining ground states, excited states, and thermal
states on a quantum computer, based on the quantum analogue of classical
imaginary time evolution.

## Overview

QITE provides a quantum implementation of imaginary time evolution, which
classically converges to the ground state via:

$$\ket{\Psi} = \lim_{\beta \to \infty} \frac{\ket{\Phi(\beta)}}{\|\ket{\Phi(\beta)}\|}$$

where the imaginary time evolution is:

$$\ket{\Phi(\beta)} = e^{-\beta \hat{H}} \ket{\Phi(0)}$$

Unlike variational algorithms (e.g. VQE), QITE does not require high-dimensional
classical optimization and has no local minima in its construction. Unlike phase
estimation, it does not require deep circuits or ancillae.




## References

[1]  Motta, Mario, Sun, Chong, Tan, Adrian T. K., O'Rourke, Matthew J., Ye, Erika,
Minnich, Austin J., Brandão, Fernando G. S. L., & Chan, Garnet Kin-Lic (2020).
Determining eigenstates and thermal states on a quantum computer using quantum
imaginary time evolution. *Nature Physics*, 16, 205–210.
[https://doi.org/10.1038/s41567-019-0704-4](https://doi.org/10.1038/s41567-019-0704-4)