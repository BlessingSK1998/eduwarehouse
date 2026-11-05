"""Orchestrator:  python -m pipeline.run [extract|load|all]"""
from __future__ import annotations

import logging
import sys

from . import extract, load


def main(argv: list[str]) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    step = argv[1] if len(argv) > 1 else "all"
    if step not in {"extract", "load", "all"}:
        print(__doc__)
        return 2
    if step in {"extract", "all"}:
        extract.extract_all()
    if step in {"load", "all"}:
        load.load_all()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
