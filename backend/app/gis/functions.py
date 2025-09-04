import geopandas as gpd
import rasterio
from rasterio.mask import mask
from scipy.ndimage import distance_transform_edt
import pandas as pd
import numpy as np
from shapely import box

DISTANCE_NODATA = -9999

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

def gen_bounding_box(input_shp, output_shp):
    """
    Generates a bounding box for the features in the input shapefile and saves it to the output shapefile.
    """
    gdf = gpd.read_file(input_shp)
    minx, miny, maxx, maxy = gdf.total_bounds
    bbox = box(minx, miny, maxx, maxy)
    bbox_gdf = gpd.GeoDataFrame({'geometry': [bbox]}, crs=gdf.crs)
    bbox_gdf.to_file(output_shp)

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

    unioned = gpd.GeoSeries([gs_all.union_all()], crs=gds_list[0].crs)
    unioned.to_file(output)

def RPL_ExtractByMask(input_raster, mask_shapefile, output_raster):
    """
    Extract the cells of a raster that fall within the area defined by a shapefile mask, setting other cells to nodata.
    
    Parameters:
    - input_raster: Path to the input raster file.
    - mask_shapefile: Path to the shapefile defining the mask.
    
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
            # "driver": "GTiff",
            "driver": "COG",
            "height": out_image.shape[1],
            "width": out_image.shape[2],
            "transform": out_transform,
            "compress": "lzw",
            "nodata": src.nodata,  # Ensure nodata is preserved
        })

    # Save the masked raster to file
    with rasterio.open(output_raster, "w", **out_meta) as dest:
        dest.write(out_image)

def RPL_PolygonToRaster_conversion(input_shp, output_raster, template_raster, fill_nodata = False):
    """
    Convert a polygon shapefile to a raster format according to a template raster. 
    Cells in polygons will be set to 1, others to 0.

    Parameters:
    - input_shp: Path to the input polygon shapefile.
    - output_raster: Path to save the output raster file.
    - template_raster: Path to the template raster file for alignment.

    Returns:
    - None
    """
    transform = None
    out_shape = None
    crs = None
    template_data = None
    with rasterio.open(template_raster) as src:
        transform = src.transform
        out_shape = (src.height, src.width)
        crs = src.crs
        template_data = src.read(1)
    
    gdf = gpd.read_file(input_shp)
    shapes = [(geom, 1) for geom in gdf.geometry]
    fill = src.nodata if fill_nodata else 0
    rasterized = rasterio.features.rasterize(
            shapes=shapes,
            out_shape=out_shape,
            transform=transform,
            fill=fill,
            nodata=src.nodata,
            dtype='uint8',
            all_touched=True,
        )
    
    # Set nodata in the output raster where the template raster has nodata values
    rasterized[template_data == src.nodata] = src.nodata

    with rasterio.open(
        output_raster,
        'w',
        driver='COG',
        height=out_shape[0],
        width=out_shape[1],
        count=1,
        dtype='uint8',
        crs=crs,
        transform=transform,
        nodata=src.nodata,
        compress='lzw',
    ) as dst:
        dst.write(rasterized, 1)

def RPL_DistanceAccumulation(input_raster,output_raster):
    """
    Perform euclidean distance accumulation on a binary raster, where 1 represents target areas and 0 represents other areas.
    The output raster will contain the distance from each cell to the nearest target area.

    Parameters:
    - input_raster: Path to the input binary raster file.
    - output_raster: Path to save the output raster file with distance accumulation.
    
    Returns:
    - None
    """
    with rasterio.open(input_raster) as src:
        raster_data = src.read(1)
        raster_nodata = src.nodata

        if raster_nodata is not None:
            nodata_mask = (raster_data == raster_nodata)
        else:
            nodata_mask = np.zeros_like(raster_data, dtype=bool)

        inverse_mask = (raster_data != 1)

        # Calculate the distance transform
        distance = distance_transform_edt(inverse_mask)

        # Convert distance to meters if the pixel size is known
        pixel_size = src.transform.a
        distance_in_meters = distance * pixel_size

        # Set the nodata values in the distance raster
        distance_in_meters[nodata_mask] = DISTANCE_NODATA

        # Save the result to a new raster file
        with rasterio.open(output_raster, 'w', driver='COG', height=src.height, width=src.width,
                           count=1, dtype='float32', crs=src.crs, transform=src.transform,
                            nodata=DISTANCE_NODATA,compress='lzw',
                           ) as dst:
            dst.write(distance_in_meters.astype('float32'), 1)

def RPL_Reclassify(input_raster, output_raster, remap_range):
    """
    Reclassify a raster based on a given range mapping.

    Parameters:
    - input_raster: Path to the input raster file.
    - output_raster: Path to save the reclassified raster file.
    - remap_range: List of [min, max, new_value] for reclassification.
      Example: [
          (0, 5, 10),
          (5, 10, 8),
          (10, 15, 5),
          (15, 90, 2)
      ] means: values from 0 (inclusive) to 5 (exclusive) become 10, etc.

    Returns:
    - None
    """
    with rasterio.open(input_raster) as src:
        data = src.read(1)
        nodata_value = src.nodata

        # find min and max values in remap_range
        remap_min = min([r[0] for r in remap_range])
        remap_max = max([r[1] for r in remap_range])

        nodata_mask =  None
        if nodata_value is not None:
            # Ensure remap ranges do not include the nodata value (if nodata is not NaN)
            if not np.isnan(nodata_value) and (nodata_value >= remap_min and nodata_value <= remap_max):
                raise ValueError(f"Nodata value {nodata_value} is outside the remap range [{remap_min}, {remap_max}]")
            nodata_mask = (data == nodata_value)
        else:
            nodata_mask = np.zeros_like(data, dtype=bool)
        
        without_nodata = data[~nodata_mask]
        min_value = np.nanmin(without_nodata)
        max_value = np.nanmax(without_nodata)

        # Ensure the remap range covers the data range
        if remap_min > min_value or remap_max < max_value:
            raise ValueError("Remap range does not cover the data range. "
                             f"Data range: [{min_value}, {max_value}], "
                             f"Remap range: [{remap_min}, {remap_max}]")

        # Create a copy of the data to reclassify
        reclassified_data = np.copy(data)
        # Apply the reclassification
        for min_val, max_val, new_val in remap_range:
            mask = (data >= min_val) & (data < max_val)
            reclassified_data[mask] = new_val
            
        reclassified_data[nodata_mask] = nodata_value
        # Save the reclassified raster
        with rasterio.open(output_raster, 'w', driver='COG', height=src.height, width=src.width,
                           nodata=src.nodata,
                           compress='lzw',
                           count=1, dtype=reclassified_data.dtype, crs=src.crs, transform=src.transform) as dst:
            dst.write(reclassified_data, 1)

def RPL_Combine_rasters(inputs, output_raster):
    """
    Combine multiple raster files into a single raster by computing the weighted sum of their values.

    Parameters:
    - inputs: List of tuples (raster file path, weight).
    - output_raster: Path to save the combined raster.

    Returns:
    - None
    """
    all_weights = [weight for _, weight in inputs]
    total_weight = sum(all_weights)
    normalized_weights = [weight / total_weight for weight in all_weights]
    data_and_weight = list(zip([file for file, _ in inputs], normalized_weights))
    first_file, first_weight = data_and_weight[0]
    with rasterio.open(first_file) as src:
        out_meta = src.meta.copy()
        out_meta.update({
            "driver": "COG",
            "count": 1,
            "dtype": "float32",
            "compress": "lzw"
        })
        first_data = src.read(1)
        raster_nodata = src.nodata
        nodata_mask = None
        if raster_nodata is not None:
            nodata_mask = (first_data == src.nodata)
        weighted_sum = first_data.astype(np.float32) * first_weight
        for file, weight in data_and_weight[1:]:
            with rasterio.open(file) as src:
                data = src.read(1)
                weighted_sum += data.astype(np.float32) * weight
        
        if nodata_mask is not None:
            weighted_sum[nodata_mask] = DISTANCE_NODATA
            out_meta['nodata'] = DISTANCE_NODATA
        
        with rasterio.open(output_raster, 'w', **out_meta) as dest:
            dest.write(weighted_sum, 1)

def RPL_Apply_mask(value_raster, mask_raster, output_path):
    """
    Applies a binary mask to a raster file, setting values to zero where the mask is 1, and writes the result to an output file.
    Parameters:
        value_raster (str): Path to the input raster file containing the values to be masked.
        mask_raster (str): Path to the binary mask raster file. Pixels with value 1 will be masked (set to zero in the output).
        output_path (str): Path where the masked raster will be saved.
    Returns:
        None
    Raises:
        ValueError: If the input rasters do not have the same shape or CRS.
    """
    with rasterio.open(value_raster) as src_value, rasterio.open(mask_raster) as src_mask:
        if src_value.shape != src_mask.shape:
            raise ValueError("Input rasters must have the same shape.")
        if src_value.crs != src_mask.crs:
            raise ValueError("Input rasters must have the same CRS.")
        value_data = src_value.read(1)
        mask_data = src_mask.read(1)
        
        masked_data = value_data.copy()
        masked_data[mask_data == 1] = src_value.nodata
    
        out_meta = src_value.meta.copy()
        out_meta.update({
            "driver": "COG",
            "compress": "lzw",
        })
        with rasterio.open(output_path, 'w', **out_meta) as dst:
            dst.write(masked_data, 1)
