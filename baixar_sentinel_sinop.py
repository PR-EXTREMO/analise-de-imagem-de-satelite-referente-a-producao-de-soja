import argparse
from pathlib import Path

import ee
import geemap

from src.sinop_config import (
    DEFAULT_END_DATE,
    DEFAULT_MAX_CLOUD_PERCENT,
    DEFAULT_SCALE_METERS,
    DEFAULT_START_DATE,
    SINOP_BBOX,
    build_output_path,
)

SENTINEL_2_SR = "COPERNICUS/S2_SR_HARMONIZED"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Baixa imagens Sentinel-2 para Sinop-MT usando Google Earth Engine."
    )
    parser.add_argument("--start-date", default=DEFAULT_START_DATE)
    parser.add_argument("--end-date", default=DEFAULT_END_DATE)
    parser.add_argument("--max-cloud", type=float, default=DEFAULT_MAX_CLOUD_PERCENT)
    parser.add_argument("--scale", type=int, default=DEFAULT_SCALE_METERS)
    parser.add_argument("--project", help="ID do projeto Google Cloud/Earth Engine.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Pasta de saida. Padrao: data/sentinel dentro do projeto.",
    )
    return parser.parse_args()


def initialize_earth_engine(project: str | None) -> None:
    try:
        ee.Initialize(project=project)
    except Exception:
        ee.Authenticate()
        ee.Initialize(project=project)


def make_sinop_geometry() -> ee.Geometry:
    return ee.Geometry.Rectangle(SINOP_BBOX)


def mask_sentinel_clouds(image: ee.Image) -> ee.Image:
    qa = image.select("QA60")
    cloud_bit_mask = 1 << 10
    cirrus_bit_mask = 1 << 11
    mask = qa.bitwiseAnd(cloud_bit_mask).eq(0).And(
        qa.bitwiseAnd(cirrus_bit_mask).eq(0)
    )
    return image.updateMask(mask).divide(10000)


def build_sentinel_mosaic(
    geometry: ee.Geometry,
    start_date: str,
    end_date: str,
    max_cloud: float,
) -> ee.Image:
    collection = (
        ee.ImageCollection(SENTINEL_2_SR)
        .filterBounds(geometry)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", max_cloud))
        .map(mask_sentinel_clouds)
    )

    count = collection.size().getInfo()
    if count == 0:
        raise RuntimeError(
            "Nenhuma imagem Sentinel-2 encontrada para esse periodo/filtro de nuvens."
        )

    print(f"Imagens encontradas: {count}")
    return collection.median().clip(geometry)


def export_geotiff(image: ee.Image, bands: list[str], output_path: Path, scale: int) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    geemap.ee_export_image(
        image.select(bands),
        filename=str(output_path),
        scale=scale,
        region=make_sinop_geometry(),
        file_per_band=False,
    )


def main() -> None:
    args = parse_args()
    initialize_earth_engine(args.project)

    output_dir = args.output_dir
    geometry = make_sinop_geometry()
    mosaic = build_sentinel_mosaic(
        geometry=geometry,
        start_date=args.start_date,
        end_date=args.end_date,
        max_cloud=args.max_cloud,
    )

    rgb_path = (output_dir / "sentinel2_sinop_rgb.tif") if output_dir else build_output_path("rgb")
    ndvi_path = (output_dir / "sentinel2_sinop_ndvi.tif") if output_dir else build_output_path("ndvi")

    ndvi = mosaic.normalizedDifference(["B8", "B4"]).rename("NDVI")

    export_geotiff(mosaic, ["B4", "B3", "B2"], rgb_path, args.scale)
    export_geotiff(ndvi, ["NDVI"], ndvi_path, args.scale)

    print(f"RGB salvo em: {rgb_path}")
    print(f"NDVI salvo em: {ndvi_path}")


if __name__ == "__main__":
    main()
