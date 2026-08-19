from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "data" / "sentinel"

# Centro aproximado de Sinop-MT.
SINOP_CENTER = (-55.5091, -11.8604)

# Recorte pequeno em torno da area urbana/rural de Sinop.
# Ordem: oeste, sul, leste, norte.
SINOP_BBOX = (-55.75, -12.05, -55.25, -11.65)

DEFAULT_START_DATE = "2025-11-01"
DEFAULT_END_DATE = "2026-03-31"
DEFAULT_MAX_CLOUD_PERCENT = 20
DEFAULT_SCALE_METERS = 10


def build_output_path(product: str) -> Path:
    return OUTPUT_DIR / f"sentinel2_sinop_{product}.tif"
