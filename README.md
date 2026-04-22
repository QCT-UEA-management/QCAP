# QCAP — Reference Catalog

A catalog of foundational quantum computational chemistry algorithms running on simulators and real quantum hardware.

Each entry is a self-contained, readable Python script for one **algorithm × molecule × backend**. Chemistry definitions (`molecule.py`, `ansatz.py`) are shared across backends; each backend gets its own runner (`run_aer.py`, `run_lrz-mqss-qpu.py`, etc.).

Please note that QCAP is not a framework. It introduces no abstraction layers, no base classes, and no hidden dependencies—just readable, runnable code implemented in popular quantum SDKs.


## Algorithm Catalog

### 🟢 Done · 🟡 In progress · 🔴 Planned


### Variational Quantum Eigensolver (VQE) 🟡  
- Ansätze: UCCSD
- SDKs: Qiskit, PennyLane, CUDA-Q
- Runners: Statevector, IQM QPU @ LRZ


###  Quantum Imaginary Time Evolution (QITE) 🔴
- SDKs: Qiskit, PennyLane, CUDA-Q


###  Quantum-Selected Configuration Interaction (QSCI) 🔴
- SDKs: Qiskit, PennyLane, CUDA-Q


###  Time-Evolved QSCI (TE-QSCI) 🔴
- SDKs: Qiskit, PennyLane, CUDA-Q


### Quantum-Classical Auxiliary-Field Quantum Monte Carlo (QC-AFQMC) 🔴
- SDKs: Qiskit, PennyLane, CUDA-Q



## Environment Setup

Dependencies are managed from the root `pyproject.toml` using [uv](https://github.com/astral-sh/uv). Install base dependencies plus your chosen SDK:

```bash
uv sync --extra qiskit
# or
uv sync --extra pennylane
# or both
uv sync --extra qiskit --extra pennylane
```

Run any entry:

```bash
uv run python algorithms/vqe/h2_uccsd_qiskit/run_aer.py
```


### Credentials

Copy `.env.example` at the repo root to `.env` and fill in MQSS_TOKEN.
The script loads it automatically via `python-dotenv`.



## Typical Setup for a New Entry

1. Create the directory
   `algorithms/<algorithm>/<molecule>_<ansatz>_<sdk>/`

2. Add the required modules:

   * `molecule.py` — defines geometry, basis set, spin, charge, and active space
   * `ansatz.py` — defines the parametrized circuit or operator pool
   * At least one simulator runner (e.g., `run_aer.py`)

3. Optionally add real-hardware runners (e.g., `run_lrz.py`) if access is available.

4. Verify the implementation: `uv run python run_aer.py`. 
   Ensure it runs without errors and prints the quantum result alongside the PySCF classical reference energy.

5. Add the new algorithm entry to the catalog table above.




## SDK Priority

1. **Qiskit** — best for broad real-hardware access  
2. **PennyLane** — well suited for research and educational use cases  
3. **CUDA-Q** — ideal for GPU-accelerated simulation and emerging QPU targets




## Contributing

Contributions are welcome. The workflow is fork → branch → pull request.

### 1. Fork and clone

```bash
# Fork the repo on GitHub, then:
git clone https://github.com/<your-username>/chem-workflow.git
cd chem-workflow
git remote add upstream https://github.com/<org>/chem-workflow.git
```

### 2. Create a branch

Use a descriptive branch name tied to what you are adding or fixing:

```bash
git checkout -b add/vqe-h2-uccsd-cudaqx
# or
git checkout -b fix/lrz-job-polling
```

### 3. Make your changes

Follow the conventions in **Typical Setup for a New Entry** above. In particular:

- Keep each algorithm folder fully self-contained — no cross-folder imports.
- Every runner must print a PySCF classical reference energy alongside the quantum result.
- Real hardware runners must never silently fall back to a simulator.
- All choices must be explicit in the code: basis set, active space, optimizer, shot count, backend name.
- Do not commit `.env` or any file containing credentials. Use `.env.example` as the template.
- Currently we are only working with 3 SDKs: Qiskit, Pennylane and QUDA-Q.

### 4. Test locally

```bash
uv run python algorithms/<your-entry>/run_aer.py
```

The script must run without errors before you open a pull request.

### 5. Open a pull request

Push your branch to your fork and open a PR against `main` on the upstream repo:

```bash
git push origin <your-branch>
```

Then on GitHub, click **Compare & pull request**. In the PR description, include:

- What algorithm / molecule / backend the entry covers.
- The classical reference energy your runner prints and how it compares to a known value.
- Any hardware access requirements or limitations reviewers should know about.

A maintainer will review the PR, request changes if needed, and merge once it is ready.



## Contributors

| Name | Email |
|------|-------|
| Mario Hernandez Vera | mario.hernandezvera@lrz.de |



## Useful Links

- [MQSS Qiskit Adapter](https://github.com/Munich-Quantum-Software-Stack/MQSS-Qiskit-Adapter)
- [MQSS PennyLane Adapter](https://github.com/Munich-Quantum-Software-Stack/MQSS-Pennylane-Adapter)
- [MQSS Documentation](https://munich-quantum-software-stack.github.io/MQSS-Interfaces/)

