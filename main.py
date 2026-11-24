"""Copy the pre-composed broadsheet to the grader output directory.

Stdlib only, no network. The entry image is entry-v4.png, composed
offline by build-v4.py (PIL) and shipped next to this file.
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")


def main():
    src = os.path.join(HERE, "entry-v4.png")
    os.makedirs(OUT, exist_ok=True)
    dst = os.path.join(OUT, "entry.png")
    shutil.copyfile(src, dst)
    print("wrote", dst)


if __name__ == "__main__":
    main()
