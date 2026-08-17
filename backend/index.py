from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parent
REPOSITORY_ROOT = BACKEND_DIR.parent
ENGINE_SRC = REPOSITORY_ROOT / "packages" / "wind-calculation-engine" / "src"

sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(ENGINE_SRC))

from app.main import app  # noqa: E402
