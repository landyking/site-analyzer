import geopandas as gpd

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