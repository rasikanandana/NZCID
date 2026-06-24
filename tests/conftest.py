import sys
from pathlib import Path

# Make the ``nzcid`` package (at the repo root) importable during tests.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
