# main.py — Akun 15 NI25 (THE SOUTHERN WIRE, Varian C).
# Stdlib-only, copy-only: render via compose_c into output/entry.png,
# then copy the finished page to entry.png at the repo root.
import os, shutil, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import compose_c


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    outdir = os.path.join(here, "output")
    os.makedirs(outdir, exist_ok=True)
    tmp = os.path.join(outdir, "entry.png")
    with open(tmp, "wb") as fh:
        fh.write(compose_c.render_png())
    shutil.copyfile(tmp, os.path.join(here, "entry.png"))


if __name__ == "__main__":
    main()
