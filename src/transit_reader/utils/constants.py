from datetime import datetime
from pathlib import Path

NOW_DT: datetime = datetime.now()
NOW: str = NOW_DT.strftime("%Y-%m-%d %H-%M")
TIMESTAMP: str = NOW_DT.strftime("%Y-%m-%d_%H-%M-%S")
DATE_TODAY: str = NOW_DT.strftime("%Y-%m-%d")
TODAY: str = NOW_DT.strftime("%A, %d %B %Y")

# Project directories
REPO_ROOT = Path(__file__).resolve().parents[3]
UTILS_DIR = Path(__file__).resolve().parent

OUTPUT_DIR = REPO_ROOT / "outputs" / DATE_TODAY
CREW_OUTPUTS_DIR = REPO_ROOT / "crew_outputs" / TIMESTAMP
CHARTS_DIR = OUTPUT_DIR / "charts"
DOCS_DIR = REPO_ROOT / "astro_docs"
SUBJECT_DIR = UTILS_DIR.parent / "subjects"

CSS_FILE = UTILS_DIR / "astro_styling.css"


def ensure_output_dirs() -> None:
    """Create the output/crew-output/chart directories used by a flow run."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    CREW_OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)


