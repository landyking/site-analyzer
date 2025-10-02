# Site Analyzer Platform
[![CI/CD Pipeline](https://github.com/landyking/site-analyzer/actions/workflows/site-analyzer-pipeline.yml/badge.svg?branch=main)](https://github.com/landyking/site-analyzer/actions/workflows/site-analyzer-pipeline.yml)

A comprehensive platform for Solar Power Site Suitability Analysis, featuring both a backend API service and a web-based frontend. The system enables users to analyze geographical areas for solar power installation suitability, manage analysis tasks, and visualize results.

## 📋 Overview

Site Analyzer empowers users to assess map regions for solar power site suitability by considering various constraint and suitability factors. Users can create analysis tasks for specific districts, review detailed suitability assessments, and interact with results through an intuitive web interface.

## 🏗️ Architecture

The platform consists of two main components:

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

## 🚀 Getting Started

1. **Clone the repository**  
     `git clone <repo-url>`

2. **Backend Setup**  
     - See [`/backend/README.md`](/backend/README.md) for API installation and configuration.

3. **Frontend Setup**  
     - See [`/webfront/README.md`](/webfront/README.md) for web app installation and usage.

## 📦 Project Structure

```
site-analyzer/
├── backend/      # API service and core logic
├── frontend/     # Web application
├── docs/         # Documentation
├── test-data/    # Test datasets
├── output-data/  # Analysis outputs
└── README.md     # Project overview
```

## 🔄 Continuous Integration & Deployment

The project uses GitHub Actions for automated CI/CD. For detailed information about the pipeline configuration, deployment process, and local testing, see [**CI/CD Documentation**](docs/CICD.md).

## 🧰 Data Preparation

When working with geospatial data, it is often necessary to ensure that the coordinate reference systems (CRS) of different datasets are consistent. This is particularly important when performing operations like rasterization or distance calculations.

If the raster data's coordinate reference system (CRS) is not consistent with the shapefile, we can reproject the raster data using GDAL's `gdalwarp` command. This command allows us to specify the target CRS and apply compression options to optimize the output file size.

```bash
# rio info xxx.tif
gdalwarp -t_srs EPSG:2193 -co COMPRESS=DEFLATE -co PREDICTOR=2 -co ZLEVEL=9 -tr 25 25 input.tif output_compressed.tif
# gdalwarp -t_srs EPSG:2193 -co COMPRESS=LZW input.tif output_compressed.tif
```

## 📄 License

Distributed under the MIT License. See `LICENSE` for details.