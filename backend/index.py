from pathlib import Path
import sys

ENGINE_SRC = Path(__file__).resolve().parent.parent / "packages" / "wind-calculation-engine" / "src"
sys.path.insert(0, str(ENGINE_SRC))

from app.main import app  # noqa: E402
