#!/usr/bin/env python3

import sys
import glob
from pathlib import Path
from collections import defaultdict
import matplotlib.pyplot as plt


def read_eta_file(path):
    rows = []

    with open(path, "r") as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            parts = line.split()

            if len(parts) < 5:
                continue

            try:
                h = float(parts[0])
                eta_val = float(parts[1])
                ireal = float(parts[2])
                iimag = float(parts[3])
                summ = float(parts[4])

                rows.append((h, eta_val, ireal, iimag, summ))

            except ValueError:
                continue

    return rows


def main():
    if len(sys.argv) != 6:
        raise ValueError(
            "Usage: python single_eta.py t1 t2 j1 j2 hz"
        )

    t1 = str(int(sys.argv[1]))
    t2 = str(int(sys.argv[2]))
    j1 = str(int(sys.argv[3]))
    j2 = str(int(sys.argv[4]))
    hz = str(int(sys.argv[5]))

    eta_dir = Path("eta")
    plot_dir = Path("plots")

    eta_dir.mkdir(exist_ok=True)
    plot_dir.mkdir(exist_ok=True)

    pattern = f"eta1_{t1}_{t2}_{j1}_{j2}_*_{hz}.txt"
    files = sorted(glob.glob(pattern))

    if not files:
        raise FileNotFoundError(f"No files found matching: {pattern}")

    eta_data = defaultdict(list)

    # ---------------------------------------------------------
    # Read all matching files
    # ---------------------------------------------------------
    for fname in files:
        base = Path(fname).stem
        parts = base.split("_")

        # eta1_t1_t2_j1_j2_N_hz
        N = int(parts[5])

        rows = read_eta_file(fname)

        for h, eta_val, ireal, iimag, summ in rows:
            norm = summ / (N / 2.0)

            eta_data[eta_val].append(
                (N, h, eta_val, ireal, iimag, summ, norm)
            )

    # ---------------------------------------------------------
    # Write eta grouped files
    # ---------------------------------------------------------
    for eta_val, data in eta_data.items():
        data.sort(key=lambda x: x[0])

        eta_tag = int(round(eta_val * 100))
        outfile = eta_dir / f"eta_{t1}_{t2}_{j1}_{j2}_{eta_tag}_{hz}.txt"

        with open(outfile, "w") as f:
            f.write("# N h eta I_real I_imag Sum normalized_sum\n")

            for row in data:
                f.write(
                    f"{row[0]} {row[1]} {row[2]} {row[3]} "
                    f"{row[4]} {row[5]} {row[6]}\n"
                )

        print(f"Wrote {outfile}")

    # ---------------------------------------------------------
    # Combined plot: all eta in same graph
    # ---------------------------------------------------------
    plt.figure(figsize=(8, 6))

    for eta_val in sorted(eta_data.keys()):
        data = sorted(eta_data[eta_val], key=lambda x: x[0])

        Nvals = [x[0] for x in data]
        Yvals = [x[6] for x in data]

        plt.plot(
            Nvals,
            Yvals,
            "o-",
            linewidth=2,
            label=f"eta={eta_val}"
        )

    plt.xlabel("N", fontsize=14)
    plt.ylabel("Sum", fontsize=14)
    plt.title(f"t1={t1}, t2={t2}, j1={j1}, j2={j2}, hz={hz}")
    plt.legend()
    plt.grid(False)
    plt.tight_layout()

    plotfile = plot_dir / f"combined_eta_{t1}_{t2}_{j1}_{j2}_{hz}.png"
    plt.savefig(plotfile, dpi=300)
    plt.close()

    print(f"Saved combined plot: {plotfile}")


if __name__ == "__main__":
    main()