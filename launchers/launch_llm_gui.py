"""
Quick launcher for SATCN LLM GUI.
"""
import sys
from pathlib import Path

# Must be before imports
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from satcn.gui.llm_gui import SATCNLLMGui  # noqa: E402

if __name__ == "__main__":
    app = SATCNLLMGui()
    app.run()
