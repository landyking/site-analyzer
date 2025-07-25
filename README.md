# Site Analyzer Platform

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
     - See `/backend/README.md` for API installation and configuration.

3. **Frontend Setup**  
     - See `/frontend/README.md` for web app installation and usage.

## 📦 Project Structure

```
site-analyzer/
├── backend/      # API service and core logic
├── frontend/     # Web application
├── docs/         # Documentation
└── README.md     # Project overview
```

## 📄 License

Distributed under the MIT License. See `LICENSE` for details.