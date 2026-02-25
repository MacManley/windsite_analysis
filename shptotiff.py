import geopandas as gpd
import rasterio
from rasterio.features import rasterize
from rasterio.transform import from_origin

# -----------------------------
# Configuration
# -----------------------------

INPUT_SHP = "YOUR_INPUT_SHP_HERE"
OUTPUT_TIF = "YOUR_OUTPUT_DIRECTORY_HERE"

SD_COLUMN = "SUBSTRATE"

# Sediment class mapping
sediment_mapping = {
    "Rock": 1,
    "Rock or other hard substrata": 1,

    "Coarse sediment": 2,
    "Till": 2,

    "Sand": 3,
    "muddy Sand": 4,
    "sandy Mud": 4,
    "Mud": 4,
    "Mud to muddy Sand": 4,
    "sandy Mud/muddy Sand": 4,

    "Mixed sediment": 5,

    "Seabed": 0,
    "Unclassified substrate": 0
}
# Grid resolution (metres)
RESOLUTION = 300

# -----------------------------
# Load shapefile
# -----------------------------

print("Loading shapefile...")

gdf = gpd.read_file(INPUT_SHP)

gdf = gdf.cx[-11:-5, 51:56]

print(gdf.columns)
print(gdf.head())
print(gdf["SUBSTRATE"].unique())

# -----------------------------
# Reproject to metre-based CRS (Ireland offshore friendly)
# -----------------------------

if gdf.crs != "EPSG:32629":
    print("Reprojecting to EPSG:32629...")
    gdf = gdf.to_crs("EPSG:32629")

# -----------------------------
# Convert seabed categories → numeric IDs
# -----------------------------

gdf["class_id"] = gdf[SD_COLUMN].map(sediment_mapping)

# Handle unmapped categories
gdf["class_id"] = gdf["class_id"].fillna(0)

# -----------------------------
# Compute raster grid
# -----------------------------

minx, miny, maxx, maxy = gdf.total_bounds

width = int((maxx - minx) / RESOLUTION)
height = int((maxy - miny) / RESOLUTION)

print("Raster dimensions:")
print("Width:", width)
print("Height:", height)
print("Total pixels:", width * height)

transform = from_origin(minx, maxy, RESOLUTION, RESOLUTION)

# -----------------------------
# Rasterize polygons
# -----------------------------

print("Rasterizing...")

raster = rasterize(
    [(geom, value) for geom, value in zip(gdf.geometry, gdf["class_id"])],
    out_shape=(height, width),
    transform=transform,
    fill=0,
    dtype="int16"
)

# -----------------------------
# Save GeoTIFF
# -----------------------------

print("Saving GeoTIFF...")

with rasterio.open(
    OUTPUT_TIF,
    "w",
    driver="GTiff",
    height=height,
    width=width,
    count=1,
    dtype=raster.dtype,
    crs=gdf.crs,
    transform=transform,
) as dst:
    dst.write(raster, 1)

print("Done →", OUTPUT_TIF)