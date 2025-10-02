# Site Analyzer Platform

[![CI/CD Pipeline](https://github.com/landyking/site-analyzer/actions/workflows/site-analyzer-pipeline.yml/badge.svg?branch=main)](https://github.com/landyking/site-analyzer/actions/workflows/site-analyzer-pipeline.yml)

A comprehensive platform for Solar Power Site Suitability Analysis, featuring a backend API service, a web-based frontend, and a raster tile service (TiTiler). The system enables users to analyze geographical areas for solar power installation suitability, manage analysis tasks, and visualize results.

## 📋 Overview

Site Analyzer empowers users to assess map regions for solar power site suitability by considering various constraint and suitability factors. Users can create analysis tasks for specific districts, review detailed suitability assessments, and interact with results through an intuitive web interface.

## 🏗️ Architecture

The platform consists of three main components:

- **Backend API Service**:

  - RESTful API design
  - User Management: Authentication and authorization with OIDC support
  - Map Task Management: Analysis task creation, processing, and result management
  - File Management: Handling of analysis result files and reports

- **Web Frontend**:
  - Interactive map visualization
  - Task creation and management UI
  - Display of suitability analysis results
  - User authentication

- **TiTiler Tile Service**:

  - Dynamic raster tiling for Cloud-Optimized GeoTIFFs (COGs)
  - On-the-fly rendering and XYZ/WMTS tile endpoints
  - Serves analysis outputs and base layers to the web frontend

## 🚀 Getting Started

1. **Clone the repository**  
    `git clone <repo-url>`

2. **Backend Setup**

   - See [`/backend/README.md`](/backend/README.md) for API installation and configuration.

3. **Frontend Setup**
   - See [`/webfront/README.md`](/webfront/README.md) for web app installation and usage.

4. **TiTiler Setup**
   - See [`/titiler/README.md`](/titiler/README.md) for running the tile server used by the frontend.

## 🌐 Live Demo

Try the hosted demo at https://solar.y2ki.com/

- Access: Use the Demo account shown on the sign-in page to log in.
- Limitations: The demo environment runs under a read-only mode due to resource constraints and security considerations.
- Explore: Browse the built-in example map data to see typical analysis outputs and interactions.
- Full experience: For all features and best performance, run the platform locally following the Backend, Webfront, and TiTiler setup guides above.

## 📦 Project Structure

```
site-analyzer/
├── backend/      # API service and core logic
├── webfront/     # Web application (frontend)
├── titiler/      # Raster tiling service (COG tiles)
├── docs/         # Documentation
├── test-data/    # Test datasets
├── output-data/  # Analysis outputs
└── README.md     # Project overview
```

## 🔄 Continuous Integration & Deployment

The project uses GitHub Actions for automated CI/CD. For detailed information about the pipeline configuration, deployment process, and local testing, see [**CI/CD Documentation**](docs/CICD.md).

## 🗺️ Default Datasets

These default geospatial layers are provided as baseline inputs for constraint and suitability scoring; they can be customized or extended per analysis.

The platform ships with a curated set of publicly available New Zealand geospatial datasets used as defaults for constraint and suitability scoring. These layers are sourced from LRIS, LINZ, and Stats NZ.

| **Dataset Name**                           | **Purpose**                                                             | **Source**                                                                                    |
| ------------------------------------------ | ----------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| LENZ - Mean Annual Solar Radiation         | Identify areas with high solar exposure                                 | [LRIS](https://lris.scinfo.org.nz/layer/48095-lenz-mean-annual-solar-radiation/)              |
| LENZ - Mean Annual Temperature             | Ensure temperature is within operational range                          | [LRIS](https://lris.scinfo.org.nz/layer/48094-lenz-mean-annual-temperature/)                  |
| LENZ - Slope                               | Exclude areas with steep slopes unsuitable for solar panel installation | [LRIS](https://lris.scinfo.org.nz/layer/48081-lenz-slope/)                                    |
| NZ Residential Area Polygons (Topo, 1:50k) | Ensure safe distance from residential zones                             | [LINZ](https://data.linz.govt.nz/layer/50325-nz-residential-area-polygons-topo-150k/)         |
| NZ River Centrelines (Topo, 1:50k)         | Maintain buffer distance from rivers                                    | [LINZ](https://data.linz.govt.nz/layer/50327-nz-river-centrelines-topo-150k/)                 |
| NZ Lake Polygons (Topo, 1:50k)             | Maintain buffer distance from lakes                                     | [LINZ](https://data.linz.govt.nz/layer/50293-nz-lake-polygons-topo-150k/)                     |
| NZ Powerline Centrelines (Topo, 1:50k)     | Prioritize areas near powerlines for grid connection                    | [LINZ](https://data.linz.govt.nz/layer/50311-nz-powerline-centrelines-topo-150k/)             |
| NZ Roads: Road Section Geometry            | Prioritize areas near roads for construction accessibility              | [LINZ](https://data.linz.govt.nz/layer/53378-nz-roads-road-section-geometry/)                 |
| Territorial Authority 2025 Clipped         | Define district boundaries for spatial filtering                        | [Stats NZ](https://datafinder.stats.govt.nz/layer/120962-territorial-authority-2025-clipped/) |

These defaults are intended to provide a robust baseline for analysis across New Zealand. Depending on your study area and objectives, you may incorporate additional layers (e.g., protected areas, flood zones) or update the sources to more recent releases.

## 🧰 Data Preparation

When working with geospatial data, it is often necessary to ensure that the coordinate reference systems (CRS) of different datasets are consistent. This is particularly important when performing operations like rasterization or distance calculations.

If the raster data's coordinate reference system (CRS) is not consistent with the shapefile, we can reproject the raster data using GDAL's `gdalwarp` command. This command allows us to specify the target CRS and apply compression options to optimize the output file size.

```bash
# rio info xxx.tif
gdalwarp -t_srs EPSG:2193 -co COMPRESS=DEFLATE -co PREDICTOR=2 -co ZLEVEL=9 -tr 25 25 input.tif output_compressed.tif
# gdalwarp -t_srs EPSG:2193 -co COMPRESS=LZW input.tif output_compressed.tif
```

## 📝 License
Distributed under the MIT License.
