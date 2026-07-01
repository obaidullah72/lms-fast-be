import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent

if sys.platform == "win32":
    VENV_PYTHON = ROOT_DIR / "venv" / "Scripts" / "python.exe"
else:
    VENV_PYTHON = ROOT_DIR / "venv" / "bin" / "python"


def ensure_venv() -> None:
    """Re-run this script with the project venv if it is not already active."""
    in_venv = sys.prefix != sys.base_prefix or os.environ.get("VIRTUAL_ENV")

    if in_venv:
        print("Virtual environment: active")
        return

    if not VENV_PYTHON.exists():
        print("Error: venv not found. Create it first:")
        print("  python3 -m venv venv")
        print("  source venv/bin/activate")
        print("  pip install -r requirements.txt")
        sys.exit(1)

    print("Activating virtual environment...")
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__, *sys.argv[1:]])


def run_migrations() -> None:
    """Create database tables if they do not exist yet."""
    from app.database import Base, engine
    from app.models.user import User  # noqa: F401 — register model with SQLAlchemy

    Base.metadata.create_all(bind=engine)
    print("Database migrations verified — tables are ready.")


def start_server() -> None:
    import uvicorn

    print("Starting server at http://localhost:8000")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    ensure_venv()
    run_migrations()
    start_server()
