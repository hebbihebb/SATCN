"""
Quick launcher for GRMR-V3 Test GUI with GPU detection.
"""
import sys
from pathlib import Path

# Must be before imports
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from satcn.gui.grmr_v3_test_gui import GRMRV3TestGUI  # noqa: E402

if __name__ == "__main__":
    app = GRMRV3TestGUI()
    app.run()
