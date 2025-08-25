import os
import app.gis.tools as tools
import app.gis.consts as consts
import logging
from app.gis.engine_models import (
    EmptyTaskMonitor,
    EngineConfigs,
    RestrictedFactor, 
    SuitabilityFactor,
    TaskMonitor,
)
from app.gis.functions import (
    RPL_Select_analysis,
    RPL_Clip_analysis,
    RPL_Buffer_analysis,
    RPL_Union_analysis,
    RPL_ExtractByMask,
    RPL_PolygonToRaster_conversion,
    RPL_DistanceAccumulation,
    RPL_Reclassify,
    RPL_Combine_rasters,
    RPL_Apply_mask,
)

logger = logging.getLogger(__name__)
class SiteSuitabilityEngine:
    def __init__(self, data_dir, output_dir, configs: EngineConfigs):
        """
        Initialize the Site Suitability Engine.
        
        Parameters:
        - data_dir: Directory containing input data
        - output_dir: Directory to store output data
        - configs: Configuration settings for the engine
        """
        self.data_dir = data_dir
        self.output_dir = output_dir
        
        # Ensure output directories exist
        os.makedirs(output_dir, exist_ok=True)
        self.restrict_dir = os.path.join(output_dir, "restrict")
        self.clip_dir = os.path.join(output_dir, "clip")
        self.score_dir = os.path.join(output_dir, "score")
        
        os.makedirs(self.restrict_dir, exist_ok=True)
        os.makedirs(self.clip_dir, exist_ok=True)
        os.makedirs(self.score_dir, exist_ok=True)
        
        # Default input paths
        self.in_territorial_authority = os.path.join(data_dir, "statsnz-territorial-authority-2025-clipped-SHP/territorial-authority-2025-clipped.shp")
        self.in_lake_polygons = os.path.join(data_dir, "lds-nz-lake-polygons-topo-150k-SHP/nz-lake-polygons-topo-150k.shp")
        self.in_river_centerlines = os.path.join(data_dir, "lds-nz-river-centrelines-topo-150k-SHP/nz-river-centrelines-topo-150k.shp")
        self.in_coastline = os.path.join(data_dir, "lds-nz-coastlines-topo-150k-SHP/nz-coastlines-topo-150k.shp")
        self.in_residential_area = os.path.join(data_dir, "lds-nz-residential-area-polygons-topo-150k-SHP/nz-residential-area-polygons-topo-150k.shp")
        self.in_road_centerlines = os.path.join(data_dir, "lds-nz-road-centrelines-topo-150k-SHP/nz-road-centrelines-topo-150k.shp")
        self.in_powerline_centerlines = os.path.join(data_dir, "lds-nz-powerline-centrelines-topo-150k-SHP/nz-powerline-centrelines-topo-150k.shp")
        self.in_solar_radiation = os.path.join(data_dir, "lris-lenz-mean-annual-solar-radiation-GTiff/solar_2193.tif")
        self.in_temperature = os.path.join(data_dir, "lris-lenz-mean-annual-temperature-GTiff/temperature_2193.tif")
        self.in_slope = os.path.join(data_dir, "lris-lenz-slope-GTiff/slope_2193.tif")
        
        # Initialize factors list
        self.factors = []
        self._initialize_factors(configs)

    def _initialize_factors(self, configs: EngineConfigs):
        """Initialize the list of factors for site suitability analysis."""
        all_factors = [
            {
                "name": "rivers",
                "dataset": self.in_river_centerlines,
                "method_prepare": self._clip_data,
                "buffer_distance": 500,
                "method_restricted_zone": self._create_restricted_area,
                "method_evaluate": lambda *args: None,
            },
            {
                "name": "lakes",
                "dataset": self.in_lake_polygons,
                "method_prepare": self._clip_data,
                "buffer_distance": 500,
                "method_restricted_zone": self._create_restricted_area,
                "method_evaluate": lambda *args: None,
            },
            {
                "name": "coastlines",
                "dataset": self.in_coastline,
                "method_prepare": self._clip_data,
                "buffer_distance": 500,
                "method_restricted_zone": self._create_restricted_area,
                "method_evaluate": lambda *args: None,
            },
            {
                "name": "residential",
                "dataset": self.in_residential_area,
                "method_prepare": self._clip_data,
                "buffer_distance": 1000,
                "method_restricted_zone": self._create_restricted_area,
                "method_evaluate": lambda *args: None,
            },
            {
                "name": "slope",
                "dataset": self.in_slope,
                "method_prepare": self._clip_data,
                "method_restricted_zone": lambda *args: None,
                "score_weight": 1.5,
                "evaluate_rules": [
                    (0, 5, 10),
                    (5, 10, 8),
                    (10, 15, 5),
                    (15, 90, 2)
                ],
                "method_evaluate": self._evaluate_slope,
            },
            {
                "name": "roads",
                "dataset": self.in_road_centerlines,
                "method_prepare": self._clip_data,
                "method_restricted_zone": lambda *args: None,
                "score_weight": 1.5,
                "evaluate_rules": [
                    (0, 1000, 10),
                    (1000, 2000, 8),
                    (2000, 3000, 5),
                    (3000, float('inf'), 2)
                ],
                "method_evaluate": self._evaluate_distance_vector,
            },
            {
                "name": "powerlines",
                "dataset": self.in_powerline_centerlines,
                "method_prepare": self._clip_data,
                "method_restricted_zone": lambda *args: None,
                "score_weight": 2.0,
                "evaluate_rules": [
                    (0, 1000, 10),
                    (1000, 2000, 8),
                    (2000, 3000, 5),
                    (3000, float('inf'), 2)
                ],
                "method_evaluate": self._evaluate_distance_vector,
            },
            {
                "name": "solar",
                "dataset": self.in_solar_radiation,
                "method_prepare": self._clip_data,
                "method_restricted_zone": lambda *args: None,
                "score_weight": 4.0,
                "evaluate_rules": [
                    (115, 125, 2),
                    (125, 135, 4),
                    (135, 140, 6),
                    (140, 145, 8),
                    (145, 150, 9),
                    (150, 155, 10)
                ],
                "method_evaluate": self._evaluate_radiation,
            },
            {
                "name": "temperature",
                "dataset": self.in_temperature,
                "method_prepare": self._clip_data,
                "method_restricted_zone": lambda *args: None,
                "score_weight": 1.0,
                "evaluate_rules": [
                    (-70, 0, 2),
                    (0, 50, 5),
                    (50, 120, 10),
                    (120, 140, 7),
                    (140, 165, 3)
                ],
                "method_evaluate": self._evaluate_temperature,
            }
        ]
        apply_factors = []
        
        for rfactor in configs.restricted_factors:
            config = next((f for f in all_factors if f['name'] == rfactor.kind), None)
            if config:
                config['buffer_distance'] = rfactor.buffer_distance
                apply_factors.append(config)

        for sfactor in configs.suitability_factors:
            config = next((f for f in all_factors if f['name'] == sfactor.kind), None)
            if config:
                config['score_weight'] = sfactor.weight
                if sfactor.ranges:
                    config['evaluate_rules'] = sfactor.ranges
                apply_factors.append(config)
        
        self.factors = apply_factors
    
    def _clip_data(self, factor, prepared_data, district_name, district_boundary_shp):
        """
        Clips the data to the district boundary.
        
        Parameters:
        - factor: Factor dictionary containing dataset and name
        - prepared_data: Dictionary of already prepared data
        - district_name: Name of the district
        - district_boundary_shp: Path to the district boundary shapefile
        
        Returns:
        - Path to the clipped data
        """
        key = factor['name']
        dataset = factor['dataset']
        logger.info(f"{district_name} # Clipping {key} data")
        out_path = os.path.join(self.clip_dir, f"clip_{key}_{district_name}")

        if dataset.endswith(".shp"):
            out_path += ".shp"
            RPL_Clip_analysis(out_path, dataset, district_boundary_shp)
        elif dataset.endswith(".tif"):
            out_path += ".tif"
            logger.info(f"range {dataset}: {tools.get_data_range(dataset)}")
            RPL_ExtractByMask(dataset, district_boundary_shp, out_path)
            logger.info(f"range {out_path}: {tools.get_data_range(out_path)}")

        return out_path
    
    def _create_restricted_area(self, factor, prepared_data, district_name, district_boundary_shp):
        """
        Creates a buffer around the feature and clips it to the district boundary.
        
        Parameters:
        - factor: Factor dictionary containing buffer_distance and name
        - prepared_data: Dictionary of already prepared data
        - district_name: Name of the district
        - district_boundary_shp: Path to the district boundary shapefile
        
        Returns:
        - Path to the clipped buffered data
        """
        feature = factor['name']
        distance = factor["buffer_distance"]

        logger.info(f"{district_name} # Creating buffer for {feature}...")
        buffer_output = os.path.join(self.restrict_dir, f"buffer_{feature}_{district_name}.shp")
        RPL_Buffer_analysis(prepared_data[feature], buffer_output, distance)

        buffer_clipped_output = os.path.join(self.restrict_dir, f"buffer_clipped_{feature}_{district_name}.shp")
        RPL_Clip_analysis(buffer_clipped_output, buffer_output, district_boundary_shp)

        return buffer_clipped_output
    
    def _evaluate_distance_vector(self, factor, prepared_data, district_name, district_boundary):
        """
        Evaluates distance to vector features and creates a score raster.
        
        Parameters:
        - factor: Factor dictionary
        - prepared_data: Dictionary of already prepared data
        - district_name: Name of the district
        - district_boundary: Path to the district boundary
        
        Returns:
        - Path to the score raster
        """
        vector_path = prepared_data[factor['name']]
        template_raster = prepared_data["slope"]
        
        # Create a binary raster from the vector
        binary_raster = os.path.join(self.score_dir, f"binary_{factor['name']}_{district_name}.tif")
        RPL_PolygonToRaster_conversion(vector_path, binary_raster, template_raster)
        logger.info(f"range {binary_raster}: {tools.get_data_range(binary_raster)}")
        # Calculate distance
        dist_raster = os.path.join(self.score_dir, f"distance_{factor['name']}_{district_name}.tif")
        RPL_DistanceAccumulation(binary_raster, dist_raster)
        logger.info(f"range {dist_raster}: {tools.get_data_range(dist_raster)}")
        # Reclassify distance to score
        score_raster = os.path.join(self.score_dir, f"score_{factor['name']}_{district_name}.tif")
        RPL_Reclassify(dist_raster, score_raster, factor["evaluate_rules"])
        logger.info(f"range {score_raster}: {tools.get_data_range(score_raster)}")
        return score_raster
    
    def _evaluate_slope(self, factor, prepared_data, district_name, district_boundary):
        """
        Evaluates slope and creates a score raster.
        
        Parameters:
        - factor: Factor dictionary
        - prepared_data: Dictionary of already prepared data
        - district_name: Name of the district
        - district_boundary: Path to the district boundary
        
        Returns:
        - Path to the score raster
        """
        slope_raster = prepared_data[factor['name']]
        score_raster = os.path.join(self.score_dir, f"score_{factor['name']}_{district_name}.tif")
        logger.info(f"range {slope_raster}: {tools.get_data_range(slope_raster)}")
        RPL_Reclassify(slope_raster, score_raster, factor["evaluate_rules"])
        logger.info(f"range {score_raster}: {tools.get_data_range(score_raster)}")
        return score_raster
    
    def _evaluate_radiation(self, factor, prepared_data, district_name, district_boundary):
        """
        Evaluates solar radiation and creates a score raster.
        
        Parameters:
        - factor: Factor dictionary
        - prepared_data: Dictionary of already prepared data
        - district_name: Name of the district
        - district_boundary: Path to the district boundary
        
        Returns:
        - Path to the score raster
        """
        radiation_raster = prepared_data[factor['name']]
        score_raster = os.path.join(self.score_dir, f"score_{factor['name']}_{district_name}.tif")
        logger.info(f"range {radiation_raster}: {tools.get_data_range(radiation_raster)}")
        RPL_Reclassify(radiation_raster, score_raster, factor["evaluate_rules"])
        logger.info(f"range {score_raster}: {tools.get_data_range(score_raster)}")
        return score_raster
    
    def _evaluate_temperature(self, factor, prepared_data, district_name, district_boundary):
        """
        Evaluates temperature and creates a score raster.
        
        Parameters:
        - factor: Factor dictionary
        - prepared_data: Dictionary of already prepared data
        - district_name: Name of the district
        - district_boundary: Path to the district boundary
        
        Returns:
        - Path to the score raster
        """
        temperature_raster = prepared_data[factor['name']]
        score_raster = os.path.join(self.score_dir, f"score_{factor['name']}_{district_name}.tif")
        logger.info(f"range {temperature_raster}: {tools.get_data_range(temperature_raster)}")
        RPL_Reclassify(temperature_raster, score_raster, factor["evaluate_rules"])
        logger.info(f"range {score_raster}: {tools.get_data_range(score_raster)}")
        return score_raster


    def process_district(self, district_code, district_name, monitor: TaskMonitor = EmptyTaskMonitor()):
        """
        Processes a single district for site suitability analysis.
        
        Parameters:
        - district_code: Code for the district
        - district_name: Name of the district
        
        Returns:
        - Path to the final suitability raster
        """
        if monitor.is_cancelled():
            logger.info("Processing cancelled for district %s; aborting.", district_name)
            return None
        logger.info(f"Start processing {district_name}")

        self.template_raster = None
        
        # Select the district boundary
        district_boundary_shp = os.path.join(self.output_dir, f"district_boundary_{district_name}.shp")
        RPL_Select_analysis(
            self.in_territorial_authority, 
            district_boundary_shp, 
            f"TA2025_V1_ == '{district_code}'"
        )
        
        monitor.update_progress(10, "district", f"Boundary prepared: {district_name}")
        # show_shapefile_info(district_boundary_shp)

        
        # Prepare data for each factor
        prepared_data = {}
        for factor in self.factors:
            prepared_data[factor["name"]] = factor["method_prepare"](
                factor, prepared_data, district_name, district_boundary_shp
            )
            if monitor.is_cancelled():
                logger.info("Processing cancelled for district %s during data preparation; aborting.", district_name)
                return None

        self.template_raster = prepared_data["slope"]  # Use slope as template for raster operations

        # print(f"prepared_data: {prepared_data}")
        # for k,v in prepared_data.items():
            # print(f"{k}: {v}")
            # show_file_info(v)
        
        # Create restricted zones for each factor
        restricted_zones = []
        for factor in self.factors:
            zone = factor["method_restricted_zone"](
                factor, prepared_data, district_name, district_boundary_shp
            )
            if zone is not None:
                restricted_zones.append(zone)
            if monitor.is_cancelled():
                logger.info("Processing cancelled for district %s during restricted zone creation; aborting.", district_name)
                return None
        
              # print(f"prepared_data: {prepared_data}")
        # for v in restricted_zones:
        #     print(f"{v}")
        #     show_file_info(v)

        # Union all restricted zones
        if restricted_zones:
            restricted_union = os.path.join(self.restrict_dir, f"restricted_union_{district_name}.shp")
            RPL_Union_analysis(restricted_zones, restricted_union)
            tools.show_file_info(restricted_union)
            # Convert the union to a raster mask
            restricted_mask_raster = os.path.join(self.output_dir, f"zone_restricted_{district_name}.tif")
            RPL_PolygonToRaster_conversion(restricted_union, restricted_mask_raster, self.template_raster)
            tools.show_file_info(restricted_mask_raster)
            monitor.update_progress(50, "restrict", f"Restricted zones prepared: {district_name}")
            monitor.record_file("restricted", restricted_mask_raster)
        else:
            logger.info(f"Warning: No restricted zones for {district_name}")
            # Create an empty mask if no restricted zones
            restricted_mask_raster = None
        
        # Evaluate and score each factor
        score_rasters = {}
        for factor in self.factors:
            if "method_evaluate" in factor and factor["method_evaluate"] is not None:
                logger.info(f"{district_name} # Evaluating {factor['name']}...")
                score_raster = factor["method_evaluate"](
                    factor, prepared_data, district_name, district_boundary_shp
                )
                if score_raster is not None:
                    score_rasters[factor["name"]] = score_raster
                    monitor.record_file(factor["name"], score_raster)
            if monitor.is_cancelled():
                logger.info("Processing cancelled for district %s during factor evaluation; aborting.", district_name)
                return None
        monitor.update_progress(80, "score", f"Factors scored: {district_name}")
        # for k,v in score_rasters.items():
        #     print(f"{k}: {v}")
        #     show_file_info(v)
        # return
        # Combine scores with weights
        if score_rasters:
            weighted_rasters = []
            
            for factor in self.factors:
                if factor["name"] in score_rasters and "score_weight" in factor:
                    weighted_rasters.append((score_rasters[factor["name"]], factor["score_weight"]))

            weighted_sum_raster = os.path.join(self.output_dir, f"zone_weighted_{district_name}.tif")
            if weighted_rasters:
                RPL_Combine_rasters(weighted_rasters, weighted_sum_raster)
                monitor.record_file("weighted", weighted_sum_raster)

                # Apply the restricted mask
                if restricted_mask_raster:
                    final_zone_raster = os.path.join(self.output_dir, f"zone_masked_{district_name}.tif")
                    RPL_Apply_mask(weighted_sum_raster, restricted_mask_raster, final_zone_raster)
                    monitor.update_progress(95, "combine", f"Finalizing: {district_name}")
                    monitor.record_file("final", final_zone_raster)
                    return final_zone_raster
                else:
                    monitor.update_progress(95, "combine", f"Finalizing: {district_name}")
                    return weighted_sum_raster
            else:
                print(f"Warning: No weighted rasters for {district_name}")
                return None
        else:
            print(f"Warning: No score rasters for {district_name}")
            return None
    
    def run(self, selected_districts=None, monitor: TaskMonitor = EmptyTaskMonitor()):
        """
        Run the site suitability analysis for all districts or selected districts.
        
        Parameters:
        - selected_districts: List of district codes to process. If None, process all districts.
        
        Returns:
        - Dictionary mapping district names to their final suitability raster paths
        """
        results = {}
        
        districts_to_process = []
        if selected_districts:
            districts_to_process = [d for d in consts.districts if d[0] in selected_districts]

        if not districts_to_process:
            raise Exception(f"No districts found for the provided codes: {selected_districts}")

        for district_code, district_name in districts_to_process:
            if monitor and monitor.is_cancelled():
                logger.info("Processing cancelled; aborting further districts.")
                return results
            result_path = self.process_district(district_code, district_name, monitor=monitor)
            results[district_name] = result_path
            print(f"Finished processing {district_name}")
            if monitor and not monitor.is_cancelled():
                monitor.update_progress(100, "success", f"Finished processing {district_name}")

        # if monitor and not monitor.is_cancelled():
        #     monitor.update_progress(100, "success", "All districts processed")
        print("All selected districts processed successfully.")
        return results


# Example usage
# Run this script by `cd backend && python -m app.gis.engine`
if __name__ == "__main__":
    # Set your data directory and output directory
    root_dir = os.path.abspath('../')
    data_dir = os.path.join(root_dir, "test-data")
    output_dir = os.path.join(root_dir, "output-data", "engine")

    # Initialize the engine
    engine = SiteSuitabilityEngine(data_dir, output_dir, EngineConfigs(
        restricted_factors=[RestrictedFactor(
            kind="coastlines",
            buffer_distance=500),RestrictedFactor(
            kind="residential",
            buffer_distance=3000)],
        suitability_factors=[SuitabilityFactor(
            kind="slope",
            weight=1.5,
            ranges=None
        )]
    ))

    # Run the analysis for all districts
    # results = engine.run()
    
    # Or run for specific districts
    results = engine.run(selected_districts=["001"])

    # Visualize results
    for district_name, result_path in results.items():
        if result_path:
            tools.show_raster_plot(result_path, title=f"Suitability for {district_name}")
