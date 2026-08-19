from pathlib import Path

from src.sinop_config import (
    DEFAULT_END_DATE,
    DEFAULT_START_DATE,
    OUTPUT_DIR,
    SINOP_BBOX,
    SINOP_CENTER,
    build_output_path,
)


def test_sinop_bbox_contains_sinop_center():
    west, south, east, north = SINOP_BBOX
    lon, lat = SINOP_CENTER

    assert west < lon < east
    assert south < lat < north


def test_default_period_is_ordered():
    assert DEFAULT_START_DATE < DEFAULT_END_DATE


def test_build_output_path_creates_descriptive_tif_path():
    path = build_output_path("ndvi")

    assert path == OUTPUT_DIR / "sentinel2_sinop_ndvi.tif"
    assert isinstance(path, Path)
