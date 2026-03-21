import sys
from pathlib import Path

# Add repo root to sys.path so tests can import modules with their current flat structure.
# This will be removed once all sources are moved to src/maccabipediabot/.
sys.path.insert(0, str(Path(__file__).parent.parent))
