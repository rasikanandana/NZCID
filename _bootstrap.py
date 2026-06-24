"""Ensure the ``src`` directory is importable.

Streamlit Cloud runs ``app.py`` from the repo root and does not pip-install
the local package, so we add ``src`` to ``sys.path`` once, here. Every page
imports this module before importing ``nzcid``.
"""

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
