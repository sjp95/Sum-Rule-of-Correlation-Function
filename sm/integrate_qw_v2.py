"""
integrate_qw_v2.py
==================
Reads 4-column data files produced by the C++ simulation:
    col 0 : q
    col 1 : w
    col 2 : Re / sqrt(dim)
    col 3 : Im / sqrt(dim)

Computes:
    I_real = Σ_q  ∫ Re(d)/sqrt(dim)  dw        (sum over q, Simpson integral over w)
    I_imag = Σ_q  ∫ Im(d)/sqrt(dim)  dw        (sum over q, Simpson integral over w)

Usage
-----
    python integrate_qw_v2.py                              # built-in demo
    python integrate_qw_v2.py N t1 t2 j1 j2 hz order
"""

import sys
import numpy as np
from scipy.integrate import simpson


# ── helpers ──────────────────────────────────────────────────────────────────

def load_file(path: str):
    """Load a whitespace-delimited 4-column file and return a structured dict."""
    data = np.loadtxt(path)
    return {
        "q"    : data[:, 0],
        "w"    : data[:, 1],
        "real" : data[:, 2],
        "imag" : data[:, 3],
        "path" : path,
    }


def reshape_to_grid(d: dict):
    """
    Reshape flat (q, w, f) arrays into 2-D grids.

    Returns
    -------
    q_vals  : 1-D array of unique q values  (length Nq)
    w_vals  : 1-D array of unique w values  (length Nw)
    Re_grid : 2-D array shape (Nq, Nw)
    Im_grid : 2-D array shape (Nq, Nw)
    """
    q_unique = np.unique(d["q"])
    w_unique = np.unique(d["w"])
    Nq, Nw   = len(q_unique), len(w_unique)

    q_idx = np.searchsorted(q_unique, d["q"])
    w_idx = np.searchsorted(w_unique, d["w"])

    Re_grid = np.zeros((Nq, Nw))
    Im_grid = np.zeros((Nq, Nw))

    Re_grid[q_idx, w_idx] = d["real"]
    Im_grid[q_idx, w_idx] = d["imag"]

    return q_unique, w_unique, Re_grid, Im_grid


def sum_q_simpson_w(q_vals, w_vals, grid):
    """
    Step 1 : Simpson's rule integral over w for each q row → 1-D array (Nq,)
    Step 2 : Discrete sum over all q values                → scalar

        result = Σ_q [ ∫ f(q, w) dw ]
    """
    # Step 1 – Simpson integral over w axis for every q row
    integral_over_w = simpson(grid, x=w_vals, axis=1)   # shape (Nq,)

    # Step 2 – plain discrete sum over q (no dq weighting)
    total = np.sum(integral_over_w)

    return total, integral_over_w   # return both for diagnostics


def integrate_file(path: str):
    d                          = load_file(path)
    q_vals, w_vals, Re, Im     = reshape_to_grid(d)

    Nq, Nw = Re.shape
    dq     = q_vals[1] - q_vals[0] if Nq > 1 else float("nan")
    dw     = w_vals[1] - w_vals[0] if Nw > 1 else float("nan")

    I_real, intw_Re = sum_q_simpson_w(q_vals, w_vals, Re)
    I_imag, intw_Im = sum_q_simpson_w(q_vals, w_vals, Im)

    # legacy quantity kept for comparison
    Sum_Im = np.sum(Im)

    print(f"\n{'='*60}")
    print(f"  File  : {path}")
    print(f"  Grid  : {Nq} q-points × {Nw} w-points")
    print(f"  dq    = {dq:.6g}    dw = {dw:.6g}")
    print(f"  Σ_q ∫ Re/√dim dw  = {I_real: .16g}")
    print(f"  Σ_q ∫ Im/√dim dw  = {-I_imag: .16g}")
    print(f"  Sum Im (raw)       = {Sum_Im:.16g}")
    print(f"{'='*60}")

    return I_real, -I_imag, Sum_Im


# ── main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        # ── demo ──────────────────────────────────────────────────────────────
        print("No file supplied – running built-in demo with synthetic data.\n")

        q_demo = np.linspace(0, np.pi, 50)
        w_demo = np.linspace(-10, 10, 80)
        QQ, WW = np.meshgrid(q_demo, w_demo, indexing="ij")   # (Nq, Nw)

        Re_demo = np.sin(QQ) * np.exp(-WW**2 / 2.0)
        Im_demo = np.cos(QQ) * np.exp(-WW**2 / 2.0)

        demo_file = "/tmp/demo_SZ.dat"
        with open(demo_file, "w") as f:
            for i, q in enumerate(q_demo):
                for j, w in enumerate(w_demo):
                    f.write(f"{q:.16f}     {w:.16f}     "
                            f"{Re_demo[i,j]:.16f}     {Im_demo[i,j]:.16f}\n")

        print(f"Demo file written to {demo_file}")

        # Analytic reference:
        #   Σ_q ∫ sin(q) e^{-w²/2} dw  =  [Σ_q sin(q_i)] × sqrt(2π)
        analytic_sum_sinq  = np.sum(np.sin(q_demo))
        analytic_real      = analytic_sum_sinq * np.sqrt(2 * np.pi)
        analytic_sum_cosq  = np.sum(np.cos(q_demo))
        analytic_imag      = analytic_sum_cosq * np.sqrt(2 * np.pi)

        I_real, I_imag, Sum = integrate_file(demo_file)

        print(f"\n  Analytic reference:")
        print(f"  Σ_q ∫ Re dw  = {analytic_real:.16g}")
        print(f"  Σ_q ∫ Im dw  = {analytic_imag:.16g}")
        print(f"  Error Re     = {abs(I_real  - analytic_real):.3e}")
        print(f"  Error Im     = {abs(-I_imag - analytic_imag):.3e}")

    else:
        N     = str(int(sys.argv[1]))
        t1    = str(int(sys.argv[2]))
        t2    = str(int(sys.argv[3]))
        j1    = str(int(sys.argv[4]))
        j2    = str(int(sys.argv[5]))
        hz    = str(int(sys.argv[6]))
        order = int(sys.argv[7])
        eta = str(int(sys.argv[8]))

        if order == 0:
            prename = "Data/NSC/SZ/SZQW/SZ"
        elif order == 1:
            prename = "Data/NSC/SZiSZj/SiSjQW/SZiSiSj"

        ff = f"{prename}_{t1}_{t2}_{j1}_{j2}_{N}_{hz}_{eta}.dat"

        I_real, I_imag, Sum = integrate_file(ff)

        h = float(hz) / 100.0
        eta_val = (float(eta)/10)*2*np.pi/50
        with open(f"results1_{t1}_{t2}_{j1}_{j2}_{N}_{hz}.txt", "a") as f:
            f.write(f"{h} {eta_val} {I_real} {I_imag} {-Sum}\n")
