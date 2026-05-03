"""
integrate_qw.py
===============
Reads 4-column data files produced by the C++ simulation:
    col 0 : q
    col 1 : w
    col 2 : Re / sqrt(dim)
    col 3 : Im / sqrt(dim)

Computes the double integral over w and q using composite Simpson's rule:

    I_real = ∫∫ Re(d)/sqrt(dim)  dw dq
    I_imag = ∫∫ Im(d)/sqrt(dim)  dw dq

Usage
-----
    python integrate_qw.py path/to/file.dat
    python integrate_qw.py path/to/file1.dat path/to/file2.dat
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

    Assumes the file is written with q as the outer loop and w as the inner
    loop (standard row-major C++ output).  Falls back to sorting if needed.

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
    
    # Map values to indices via a sort-based approach
    q_idx = np.searchsorted(q_unique, d["q"])
    w_idx = np.searchsorted(w_unique, d["w"])

    Re_grid = np.zeros((Nq, Nw))
    Im_grid = np.zeros((Nq, Nw))

    Re_grid[q_idx, w_idx] = d["real"]
    Im_grid[q_idx, w_idx] = d["imag"]

    return q_unique, w_unique, Re_grid, Im_grid


def double_simpson(q_vals, w_vals, grid):
    """
    2-D composite Simpson's rule on a uniform rectangular grid.

    Step 1 : integrate over w for every q row  →  1-D array (length Nq)
    Step 2 : integrate that result over q       →  scalar

    scipy.integrate.simpson automatically uses Simpson's rule on uniform
    grids and falls back gracefully if the number of points is even
    (it uses the 3/8 rule for the last panel).
    """
    # Step 1 – integrate each row over w
    integral_over_w = simpson(grid, x=w_vals, axis=1)   # shape (Nq,)

    # Step 2 – integrate the result over q
    total = simpson(integral_over_w, x=q_vals)           # scalar

    return total


def integrate_file(path: str):
    d                          = load_file(path)
    q_vals, w_vals, Re, Im     = reshape_to_grid(d)

    Nq, Nw = Re.shape
    dq     = q_vals[1] - q_vals[0] if Nq > 1 else float("nan")
    dw     = w_vals[1] - w_vals[0] if Nw > 1 else float("nan")

    I_real = double_simpson(q_vals, w_vals, Re)
    I_imag = double_simpson(q_vals, w_vals, Im)

    Sum = np.sum(Im)

    print(f"\n{'='*60}")
    print(f"  File : {path}")
    print(f"  Grid : {Nq} q-points × {Nw} w-points")
    print(f"  dq   = {dq:.6g}    dw = {dw:.6g}")
    print(f"  ∫∫ Re/√dim  dw dq = {I_real: .16g}")
    print(f"  ∫∫ Im/√dim  dw dq = {-I_imag: .16g}")
    #print(f"  |I|               = {np.hypot(I_real, I_imag):.16g}")
    print(f"  Sum Im            = {Sum:.16g}")
    print(f"{'='*60}")

    return I_real, -I_imag , Sum


# ── main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        # ── demo: generate a synthetic file matching your C++ format ──────────
        print("No file supplied – running built-in demo with synthetic data.\n")

        rng    = np.random.default_rng(42)
        q_demo = np.linspace(0, np.pi, 50)
        w_demo = np.linspace(-10, 10, 80)
        QQ, WW = np.meshgrid(q_demo, w_demo, indexing="ij")  # (Nq, Nw)

        # Gaussian in w, sinusoidal in q  – analytic result is known
        Re_demo = np.sin(QQ) * np.exp(-WW**2 / 2.0)
        Im_demo = np.cos(QQ) * np.exp(-WW**2 / 2.0)

        demo_file = "/tmp/demo_SZ.dat"
        with open(demo_file, "w") as f:
            for i, q in enumerate(q_demo):
                for j, w in enumerate(w_demo):
                    f.write(f"{q:.16f}     {w:.16f}     "
                            f"{Re_demo[i,j]:.16f}     {Im_demo[i,j]:.16f}\n")

        print(f"Demo file written to {demo_file}")

        # Analytic reference: ∫₀^π sin(q)dq × ∫_{-∞}^{∞} e^{-w²/2}dw
        # = 2 × sqrt(2π) ≈ 5.01326
        analytic_real = 2.0 * np.sqrt(2 * np.pi)
        analytic_imag = 0.0   # ∫₀^π cos(q)dq = 0

        I_real, I_imag, Sum = integrate_file(demo_file)

        print(f"\n  Analytic reference:")
        print(f"  ∫∫ Re  dw dq = {analytic_real:.16g}")
        print(f"  ∫∫ Im  dw dq = {analytic_imag:.16g}")
        print(f"  Error Re     = {abs(I_real - analytic_real):.3e}")
        print(f"  Error Im     = {abs(I_imag - analytic_imag):.3e}")

    else:
        N=str(int(sys.argv[1]))
        t1=str(int(sys.argv[2]))
        t2=str(int(sys.argv[3]))
        j1=str(int(sys.argv[4]))
        j2=str(int(sys.argv[5]))
        hz=str(int(sys.argv[6]))
        order=int(sys.argv[7])
        eta=str(int(sys.argv[8]))

        prename=str("SZ")
        if(order==0):
            prename=str("Data/NSC/SZ/SZQW/SZ")
        if(order==1):
            prename=str("Data/NSC/SZiSZj/SiSjQW/SZiSiSj")

        ff =str(prename+"_"+t1+"_"+t2+"_"+j1+"_"+j2+"_"+N+"_"+hz+"_"+eta+".dat") #"+s+" 
        I_real, I_imag, Sum = integrate_file(ff)
        h=float(hz)/100.0
        eta_val = (float(eta)/10)*2*np.pi/50
        with open("results_"+t1+"_"+t2+"_"+j1+"_"+j2+"_"+N+"_"+hz+".txt", "a") as f:
            f.write(f"{h} {eta_val} {I_real} {I_imag} {-Sum}\n")

