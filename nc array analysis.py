import xarray as xr
import os
import rasterio
import numpy as np


# print(os.getcwd())
# print(os.listdir())

ds = xr.open_dataset("YOUR_NC_FILE_HERE")

# Elevation/bathymetry array
height = ds["elevation"].values
print(height)

def extract_height_from_tif(tif_path, x=None, y=None):
    """
    If x and y are provided → returns height at that coordinate.
    If not → returns the full height matrix.
    """

    with rasterio.open(tif_path) as dataset:
        if x is not None and y is not None:
            # Convert geographic coordinate → pixel coordinate
            print(dataset.crs)
            print(dataset.bounds)
            row, col = dataset.index(x, y)
            height = dataset.read(1)[row, col]
            return float(height)

        # Return full elevation array
        height_map = dataset.read(1)
        return height_map
    
tif_file = "/Users/macmanley/terrain.tif"

# Get height at a specific coordinate
height_value = extract_height_from_tif(tif_file, x=-9.7, y=52.8)
print("Height:", height_value)