"""
Quick launcher for Pipeline Test GUI with GPU detection.
"""
import sys
from pathlib import Path

# Must be before imports
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from satcn.gui.pipeline_test_gui import PipelineTestGUI  # noqa: E402

if __name__ == "__main__":
    app = PipelineTestGUI()
    app.run()
