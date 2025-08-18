from datetime import datetime
import rasterio
import numpy as np
import geopandas as gpd
import os

version = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_data_range(input_raster):
    """
    Returns the minimum, maximum (excluding nodata), and nodata value of a raster.

    Parameters:
    - input_raster: Path to the raster file.

    Returns:
    - (min_value, max_value, nodata_value): Tuple of min, max, and nodata.
    """
    with rasterio.open(input_raster) as src:
        data = src.read(1)
        nodata_value = src.nodata

        if nodata_value is not None:
            data = data[data != nodata_value]

        min_value = np.nanmin(data)
        max_value = np.nanmax(data)

    return min_value, max_value, nodata_value
def get_data_range(input_raster):
    """
    Returns the minimum, maximum (excluding nodata), and nodata value of a raster.

    Parameters:
    - input_raster: Path to the raster file.

    Returns:
    - (min_value, max_value, nodata_value): Tuple of min, max, and nodata.
    """
    with rasterio.open(input_raster) as src:
        data = src.read(1)
        nodata_value = src.nodata

        if nodata_value is not None:
            data = data[data != nodata_value]

        min_value = np.nanmin(data)
        max_value = np.nanmax(data)

    return min_value, max_value, nodata_value
def show_shapefile_plot(shapefile_path):
    """
    Visualizes a shapefile on a plot using GeoPandas.
    
    Parameters:
    - shapefile_path: Path to the shapefile to visualize
    
    Returns:
    - None
    """
    import matplotlib.pyplot as plt
    gdf = gpd.read_file(shapefile_path)
    fig, ax = plt.subplots(figsize=(5, 10))
    gdf.plot(ax=ax, color='blue')
    ax.set_xticks([])
    ax.set_yticks([])
    plt.show()
def show_raster_plot(raster_path, cmap='viridis', title=None):
    """
    Visualizes a raster using Rasterio and Matplotlib, displaying nodata values as transparent.

    Parameters:
    - raster_path: Path to the raster file.
    - cmap: Colormap for visualization.
    - title: Optional plot title.

    Returns:
    - None
    """
    import matplotlib.pyplot as plt
    with rasterio.open(raster_path) as src:
        data = src.read(1)
        nodata = src.nodata

    # Mask nodata values for transparency
    if nodata is not None:
        data = np.ma.masked_equal(data, nodata)
    else:
        data = np.ma.masked_invalid(data)

    plt.figure(figsize=(8, 6))
    im = plt.imshow(data, cmap=cmap)
    plt.colorbar(im, fraction=0.046, pad=0.04)
    if title:
        plt.title(title)
    plt.axis('off')
    plt.show()

def show_shapefile_plot(shapefile_path):
    """
    Visualizes a shapefile on a plot using GeoPandas.
    
    Parameters:
    - shapefile_path: Path to the shapefile to visualize
    
    Returns:
    - None
    """
    import matplotlib.pyplot as plt
    gdf = gpd.read_file(shapefile_path)
    fig, ax = plt.subplots(figsize=(5, 10))
    gdf.plot(ax=ax, color='blue')
    ax.set_xticks([])
    ax.set_yticks([])
    plt.show()

def show_file_info(file_path):
    """
    Displays basic information about a file. Determines if the file is a shapefile or raster based on its extension,
    and prints relevant metadata.

    Parameters:
    - file_path: Path to the file.

    Returns:
    - None
    """
    file_size = os.path.getsize(file_path)
    ext = os.path.splitext(file_path)[1].lower()
    print(f"File: {file_path}")
    print(f"Size: {file_size} bytes")
    print(f"Type: {ext}")

    if ext in [".shp"]:
        try:
            gdf = gpd.read_file(file_path)
            print(f"Shapefile CRS: {gdf.crs}")
            print(f"Number of features: {len(gdf)}")
        except Exception as e:
            print(f"Error reading shapefile: {e}")
    elif ext in [".tif", ".tiff"]:
        try:
            with rasterio.open(file_path) as src:
                print(f"metadata: {src.meta}")
                # print(f"Raster CRS: {src.crs}")
                # print(f"Raster size: {src.width} x {src.height}")
                # print(f"Number of bands: {src.count}")
                # print(f"Data type: {src.dtypes[0]}")
        except Exception as e:
            print(f"Error reading raster: {e}")