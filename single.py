import sys
from pathlib import Path


def integrate_file(path: str):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    rows = []
    with p.open("r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            parts = line.split()
            if len(parts) < 5:
                continue

            try:
                vals = tuple(float(x) for x in parts[:5])
                rows.append(vals)
            except ValueError:
                continue

    if not rows:
        raise ValueError(f"No valid data row with >=5 numeric columns in: {path}")

    return rows


def main():
    if len(sys.argv) < 8:
        raise ValueError("Usage: python single.py N t1 t2 j1 j2 hz order")

    # args
    N = str(int(sys.argv[1]))
    t1 = str(int(sys.argv[2]))
    t2 = str(int(sys.argv[3]))
    j1 = str(int(sys.argv[4]))
    j2 = str(int(sys.argv[5]))
    hz = str(int(sys.argv[6]))
    order = int(sys.argv[7])

    if order not in (0, 1):
        raise ValueError("order must be 0 or 1")

    ff_sp = f"sp/results1_{t1}_{t2}_{j1}_{j2}_{N}_{hz}.txt"
    ff_sm = f"sm/results1_{t1}_{t2}_{j1}_{j2}_{N}_{hz}.txt"

    rows_sp = integrate_file(ff_sp)
    rows_sm = integrate_file(ff_sm)

    if len(rows_sp) != len(rows_sm):
        raise ValueError("sp and sm files have different numbers of valid data rows")

    with open(f"eta1_{t1}_{t2}_{j1}_{j2}_{N}_{hz}.txt", "a") as f:
        for (h, eta_val, I_real_sp, I_imag_sp, Sum_sp), (
            h1,
            eta_val1,
            I_real_sm,
            I_imag_sm,
            Sum_sm,
        ) in zip(rows_sp, rows_sm):
            # Optional consistency checks
            if h != h1 or eta_val != eta_val1:
                pass  # keep existing behavior; change to raise if strict matching is required

            f.write(
                f"{h} {eta_val} "
                f"{I_real_sp + I_real_sm} {I_imag_sp + I_imag_sm} {-Sum_sp + Sum_sm}\n"
            )


if __name__ == "__main__":
    main()

