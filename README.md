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

The project utilizes GitHub Actions for automated building and deployment, configured in [.github/workflows/site-analyzer-pipeline.yml](.github/workflows/site-analyzer-pipeline.yml).

### Pipeline Overview

The workflow consists of three build jobs and their corresponding deployment jobs:

- **Webfront Build & Deploy**: Builds the frontend application and deploys it to the server.
- **Backend Build & Deploy**: Compiles the Python backend and deploys it to the server.
- **Titiler Build & Deploy**: Builds and deploys the titiler component.

### Required Secrets

To run the CI/CD pipeline, the following secrets must be configured in your GitHub repository:

| Secret Name | Description |
|-------------|-------------|
| `SSH_HOST` | Target server hostname or IP address |
| `SSH_USER` | Username for SSH connection |
| `SSH_PASS` | Password for SSH authentication |
| `SSH_TARGET_PATH` | Path where artifacts should be deployed on the server |
| `VITE_API_URL` | API URL for the frontend application |
| `VITE_TITILER_URL` | Titiler service URL for the frontend |
| `VITE_GOOGLE_CLIENT_ID` | Google OAuth client ID (for authentication) |

### Local Testing with Act

You can test the GitHub Actions workflows locally using [act](https://github.com/nektos/act), a tool that runs GitHub Actions locally in Docker containers.

1. **Install act**
   ```bash
   # For macOS
   brew install act
   ```

2. **Configure local secrets**
   Create a `.secrets` file in your repository root (ensure it's in .gitignore):
   ```bash
   SSH_HOST=your-server-hostname
   SSH_USER=your-username
   SSH_PASS=your-password
   SSH_TARGET_PATH=/path/on/server
   VITE_API_URL=http://localhost:8000
   VITE_TITILER_URL=http://localhost:8001
   VITE_GOOGLE_CLIENT_ID=your-client-id
   ```

3. **Run a specific job**
   ```bash
   # Run a specific job with artifacts path
   act -j webfront --artifact-server-path /tmp/act-artifacts --secret-file .secrets
   
   # Run backend build job
   act -j backend --artifact-server-path /tmp/act-artifacts --secret-file .secrets
   
   # Test deployment job
   act -j webfront-deploy --artifact-server-path /tmp/act-artifacts --secret-file .secrets
   ```

4. **Important notes for local testing**
   - Deployment jobs depend on build jobs, so you may need to run build jobs first
   - The `--artifact-server-path` parameter is required to share artifacts between jobs
   - Use `-P ubuntu-latest=catthehacker/ubuntu:act-latest` for a more compatible Ubuntu image

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