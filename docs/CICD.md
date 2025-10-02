# 🔄 Continuous Integration & Deployment

The project utilizes GitHub Actions for automated building and deployment, configured in [.github/workflows/site-analyzer-pipeline.yml](../.github/workflows/site-analyzer-pipeline.yml).

## Pipeline Overview

The workflow consists of three build jobs and their corresponding deployment jobs:

- **Webfront Build & Deploy**: Builds the frontend application and deploys it to the server.
- **Backend Build & Deploy**: Runs unit tests with coverage reporting, compiles the Python backend, and deploys it to the server.
- **Titiler Build & Deploy**: Builds and deploys the titiler component.

## Testing Integration

The backend build job includes comprehensive testing:

- **Test Dependencies**: Uses `uv sync --group test` to install test dependencies
- **Unit Tests**: Runs pytest with the complete test suite (84 tests)
- **Coverage Reporting**: Generates coverage reports in XML and terminal formats
- **Coverage Reports**: Generates local coverage reports in XML and terminal formats
- **Quality Gates**: Tests must pass before the build proceeds
- **Build Dependencies**: Uses `uv sync` to install all production dependencies for building
- **Package Build**: Creates distributable package using `uv build`

### Local Testing Commands

To run tests locally (same as CI):

```bash
# Install test dependencies
uv sync --group test

# Run tests with coverage
uv run pytest tests/unit/ --cov=app --cov-report=xml --cov-report=term-missing --tb=short
```

For more testing options, see the [Backend Testing Guide](../backend/TESTING.md).

## Required Secrets

To run the CI/CD pipeline, the following secrets must be configured in your GitHub repository:

### SSH and Deployment Secrets

| Secret Name | Description |
|-------------|-------------|
| `SSH_HOST` | Target server hostname or IP address |
| `SSH_USER` | Username for SSH connection |
| `SSH_PASS` | Password for SSH authentication |
| `SSH_TARGET_PATH` | Path where artifacts should be deployed on the server |



### Frontend Environment Variables

| Secret Name | Description |
|-------------|-------------|
| `VITE_API_URL` | API URL for the frontend application |
| `VITE_TITILER_URL` | Titiler service URL for the frontend |
| `VITE_GOOGLE_CLIENT_ID` | Google OAuth client ID (for authentication) |
| `VITE_RELEASE_READ_ONLY` | Enable/disable read-only mode for the application |
| `VITE_RELEASE_DEMO` | Enable/disable demo mode features |
| `VITE_RELEASE_DEMO_USERNAME` | Demo username for demonstration purposes |
| `VITE_RELEASE_DEMO_PASSWORD` | Demo password for demonstration purposes |

## Local Testing with Act

You can test the GitHub Actions workflows locally using [act](https://github.com/nektos/act), a tool that runs GitHub Actions locally in Docker containers.

### 1. Install act

```bash
# For macOS
brew install act
```

### 2. Configure local secrets

Create a `.secrets` file in your repository root (ensure it's in .gitignore):

```bash
# SSH and Deployment
SSH_HOST=your-server-hostname
SSH_USER=your-username
SSH_PASS=your-password
SSH_TARGET_PATH=/path/on/server

# Frontend Environment Variables
VITE_API_URL=http://localhost:8000
VITE_TITILER_URL=http://localhost:8001
VITE_GOOGLE_CLIENT_ID=your-client-id
VITE_RELEASE_READ_ONLY=false
VITE_RELEASE_DEMO=true
VITE_RELEASE_DEMO_USERNAME=demo-user
VITE_RELEASE_DEMO_PASSWORD=demo-pass
```

### 3. Run a specific job

```bash
# Run a specific job with artifacts path
act -j webfront --artifact-server-path /tmp/act-artifacts --secret-file .secrets

# Run backend build job
act -j backend --artifact-server-path /tmp/act-artifacts --secret-file .secrets

# Test deployment job
act -j webfront-deploy --artifact-server-path /tmp/act-artifacts --secret-file .secrets
```

### 4. Important notes for local testing

- Deployment jobs depend on build jobs, so you may need to run build jobs first
- The `--artifact-server-path` parameter is required to share artifacts between jobs
- Use `-P ubuntu-latest=catthehacker/ubuntu:act-latest` for a more compatible Ubuntu image

## Troubleshooting

### Common Issues

- **Authentication failures**: Ensure all required secrets are properly configured
- **Build failures**: Check that all dependencies are correctly specified in the respective configuration files
- **Deployment issues**: Verify that the target server is accessible and the deployment path exists

### Monitoring

Monitor the CI/CD pipeline status through:
- GitHub Actions tab in the repository
- Badge status in the main README
- Server logs for deployment verification