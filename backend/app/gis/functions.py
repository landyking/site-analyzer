import geopandas as gpd
import rasterio
from rasterio.mask import mask
import pandas as pd

def RPL_Select_analysis(input_shp, output_shp, conditions_expression):
    """
    Selects features from the input shapefile based on a given expression and saves them to an output shapefile.
    
    Parameters:
    - input_shp: Path to the input shapefile.
    - output_shp: Path to save the output shapefile.
    - conditions_expression: Expression to filter features. Example: "TA2025_V1_ == '001'".
    
    Returns:
    - None
    """
    gdf = gpd.read_file(input_shp)
    selected_gdf = gdf.query(conditions_expression)
    selected_gdf.to_file(output_shp)

def RPL_Clip_analysis(output, whole_area, boundary):
    """
    Clips a whole area shapefile to a specified boundary and saves the result.
    
    Parameters:
    - output: Path to save the clipped shapefile.
    - whole_area: Path to the whole area shapefile.
    - boundary: Path to the boundary shapefile.
    
    Returns:
    - None
    """
    whole_area_gdf = gpd.read_file(whole_area)
    boundary_gdf = gpd.read_file(boundary)
    
    clipped_gdf = gpd.clip(whole_area_gdf, boundary_gdf)
    clipped_gdf.to_file(output)

def RPL_Buffer_analysis(input, output, buffer_distance):
    """
    Creates a buffer around features in a shapefile and saves the result.
    Users can use `[axis.unit_name for axis in gdf.crs.axis_info]` to get the unit of a shapefile.
    
    Parameters:
    - input: Path to the input shapefile.
    - output: Path to save the buffered shapefile.
    - buffer_distance: Distance for the buffer (float, same unit as input shapefile).

    Returns:
    - None
    """
    gdf = gpd.read_file(input)
    buffered_gdf = gdf.buffer(distance=buffer_distance)
    buffered_gdf.to_file(output)

def RPL_Union_analysis(inputs, output):
    """
    Unions multiple shapefiles into a single shapefile, merging geometries and discarding attributes.
    
    Parameters:
    - inputs: List of paths to input shapefiles.
    - output: Path to save the unioned shapefile.
    
    Returns:
    - None
    """
    gds_list = [gpd.read_file(input).geometry for input in inputs]
    gs_all = gpd.GeoSeries(pd.concat(gds_list, ignore_index=True), crs=gds_list[0].crs)
    unioned =  gs_all.union_all()
    unioned.to_file(output)

def RPL_ExtractByMask(input_raster, mask_shapefile, output_raster):
    """
    Extract the cells of a raster that fall within the area defined by a shapefile mask, setting other cells to nodata.
    
    Parameters:
    - input_raster: Path to the input raster file.
    - mask_shapefile: Path to the shapefile defining the mask.
    - output_raster: Path to save the masked raster file.
    Returns:
    - None
    """
    mask_gdf = gpd.read_file(mask_shapefile)
    mask_geoms = mask_gdf.geometry.values

    # Open the raster file
    with rasterio.open(input_raster) as src:
        # Mask the raster with the shapefile geometry
        out_image, out_transform = mask(src, mask_geoms, crop=True)

        # Copy the metadata
        out_meta = src.meta.copy()
        out_meta.update({
            "driver": "GTiff",
            "height": out_image.shape[1],
            "width": out_image.shape[2],
            "transform": out_transform,
            "nodata": src.nodata  # Ensure nodata is preserved
        })

    # Save the masked raster to file
    with rasterio.open(output_raster, "w", **out_meta) as dest:
        dest.write(out_image)