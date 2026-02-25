from pyproj import Transformer
import rasterio

def extract_substrate_from_tif(tif_path, lon, lat):

    with rasterio.open(tif_path) as dataset:

        # Transform WGS84 → raster CRS
        transformer = Transformer.from_crs(
            "EPSG:4326",
            dataset.crs,
            always_xy=True
        )

        x_proj, y_proj = transformer.transform(lon, lat)

        if not (dataset.bounds.left <= x_proj <= dataset.bounds.right and
                dataset.bounds.bottom <= y_proj <= dataset.bounds.top):
            return None

        row, col = dataset.index(x_proj, y_proj)

        return int(dataset.read(1)[row, col])

# Example (Ireland coast)
print(extract_substrate_from_tif(
    "YOUR_FILE_HERE",
    -9.7,
    55
))