# One-Dimensional Kitaev Magnet Sum Rules

This repository contains C++ and Python implementations for calculating one- and two-spin-flip dynamical correlation functions and their corresponding sum rules in 1D Kitaev magnets. The code supports exact analytical benchmarks and numerical simulations using Density Matrix Renormalization Group (DMRG) via the iTensor library.

## Theoretical Background

In 1D Kitaev chains, the Hamiltonian is

$$
H_{\text{Kitaev}} = \sum_{i\,\in\,\mathrm{even}} \left( S_i^x S_{i+1}^x    \right)
$$

Unlike the Heisenberg model, total $S^z$ does not commute with $H_{\text{Kitaev}}$, so the ground state contains contributions from all $S_{\text{Tot}}^z$ sectors.

### One-Spin Sum Rules

The single-spin dynamical correlation function is

$$\mathcal{S}_1^\beta(q,\omega) = \frac{1}{N} \sum_{i,j} e^{-iq(r_i-r_j)} \int_{-\infty}^{\infty} \frac{dt}{2\pi} e^{i\omega t} \langle \lambda_0 | S_i^{\bar{\beta}}(t) S_j^\beta(0) | \lambda_0 \rangle$$

The corresponding sum rules $\Xi_1^\beta$ are the integrals over all momentum $q$ and frequency $\omega$:

- **Z-component**: $\Xi_1^z = \frac{N}{4}$
- **Transverse components**: $\Xi_1^+ = \frac{1}{4} \sum_{\alpha} \sum_{I_\alpha} |d_{I_\alpha}|^2 C_{\uparrow, n_\downarrow}^{I_\alpha}$ and $\Xi_1^- = \frac{1}{4} \sum_{\alpha} \sum_{I_\alpha} |d_{I_\alpha}|^2 C_{\downarrow, N-n_\uparrow}^{I_\alpha}$

### Two-Spin Sum Rules

For double spin-flip excitations, relevant to RIXS and 2DCS, the dynamical correlation function is

$$\mathcal{S}_2^{\alpha\beta}(q,\omega) = \frac{1}{N} \sum_{i,j} e^{-iq(r_i-r_j)} \int_{-\infty}^{\infty} \frac{dt}{2\pi} e^{i\omega t} \langle \lambda_0 | S_i^{\bar{\alpha}}(t) S_{i+a}^{\bar{\beta}}(t) S_j^\alpha(0) S_{j+a}^\beta(0) | \lambda_0 \rangle$$

A key result is the combinatoric-factor-free sum rule, valid for any magnetic field value:

$$\sum_{\alpha,\beta \in \{+,-\}} \Xi_2^{\alpha,\beta} = N$$

## Code Implementation

The project is split into high-performance numerical computation in C++ and analytical benchmarking/visualization in Python.

### C++: Numerical Simulations

The C++ code uses the iTensor library for DMRG and time evolution.

- Computes $\mathcal{S}_1$ and $\mathcal{S}_2$ correlation functions for chains up to $N=180$
- Supports bond dimensions up to 2000 for convergence in the Kitaev and Heisenberg models
- Uses a time step $\Delta t$ and total time $t_{\max}$ to determine the frequency window $\omega \in [0, 2\pi/\Delta t]$
- Includes a Lorentzian broadening factor $\eta$ for spectral functions

### Python: Analytics and Plotting

The Python scripts provide exact solutions used to benchmark DMRG results.

- Exact diagonalization for smaller system sizes to verify sum rule coefficients $d_{I_\alpha}$
- Analytical field-dependent BdG spectrum:

	$$\epsilon_{\pm,\pm}^k = \pm \sqrt{\left(h^2 + 2|m_k|^2\right) \pm 2\sqrt{|m_k|^2\left(h^2 + 2|m_k|^2\right)}}$$

	where $m_k = \frac{1}{4}(J_x + J_y e^{i2ka})$
- Generates spectral weight plots and sum rule normalization curves

## Usage Summary

1. Run the C++ DMRG binary to generate raw time-domain correlation data.
2. Use the Python scripts to perform Fourier transforms and apply broadening $\eta$.
3. Compare the numerical sum rule $\sum \Xi_2^{\alpha,\beta}$ against the analytical value $N$ to verify accuracy.
