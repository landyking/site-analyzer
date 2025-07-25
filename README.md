# Site Analyzer Backend

A backend API service for the Solar Power Site Suitability Analysis Platform, designed to analyze geographical areas for solar power installation suitability.

## 📋 Overview

This platform enables users to analyze map regions for solar power site suitability by considering various constraint and suitability factors. Users can create analysis tasks for specific districts and receive detailed suitability assessments.

## 🏗️ Architecture

The system follows a RESTful API design with the following core domains:

- **User Management**: Authentication and authorization with OIDC support
- **Map Task Management**: Analysis task creation, processing, and result management
- **File Management**: Handling of analysis result files and reports