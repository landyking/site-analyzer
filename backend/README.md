# Site Analyzer Backend

A FastAPI-based backend service for the site analyzer application.

## Prerequisites

- Python 3.11 or higher
- pip (Python package installer)

## Setup and Installation

### 1. Clone the repository and navigate to the backend directory

```bash
cd backend
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

**On macOS/Linux:**
```bash
source .venv/bin/activate
```

**On Windows:**
```bash
.venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

## Running the Application

Start the FastAPI development server:

```bash
fastapi dev app/main.py
# or
uvicorn app.main:app --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive API docs**: http://localhost:8000/docs
- **Alternative API docs**: http://localhost:8000/redoc

## Dependency Management with requirements.txt

### Installing Dependencies

To install all project dependencies:

```bash
pip install -r requirements.txt
```

### Adding New Dependencies

1. Install the new package:
```bash
pip install package-name
```

2. Update requirements.txt:
```bash
pip freeze > requirements.txt
```

### Generating requirements.txt from scratch

If you need to regenerate the requirements.txt file:

```bash
# Make sure your virtual environment is activated
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate     # On Windows

# Generate requirements.txt with all installed packages
pip freeze > requirements.txt
```

### Best Practices

1. **Always use a virtual environment** to avoid conflicts with system packages
2. **Keep requirements.txt updated** whenever you add or remove dependencies
3. **Pin specific versions** for production deployments to ensure reproducibility
4. **Consider creating separate files** for different environments:
   - `requirements.txt` - Production dependencies
   - `requirements-dev.txt` - Development dependencies (testing, linting, etc.)

### Example: Adding a new dependency

```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Install new package
pip install requests

# 3. Update requirements.txt
pip freeze > requirements.txt

# 4. Commit the updated requirements.txt
git add requirements.txt
git commit -m "Add requests dependency"
```

## Development

### Project Structure

```
backend/
├── app/
│   └── main.py          # Main FastAPI application
├── .venv/               # Virtual environment (ignored by git)
├── requirements.txt     # Python dependencies
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

### Environment Variables

Create a `.env` file in the backend directory for environment-specific configuration:

```bash
# Example .env file
DEBUG=True
DATABASE_URL=sqlite:///./test.db
SECRET_KEY=your-secret-key-here
```

## API Documentation

Once the server is running, you can access the interactive API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Troubleshooting

### Common Issues

1. **Import errors**: Make sure your virtual environment is activated and dependencies are installed
2. **Port already in use**: Change the port by running `uvicorn app.main:app --reload --port 8001`
3. **Permission errors**: Ensure you have write permissions in the project directory

### Useful Commands

```bash
# Check installed packages
pip list

# Check if requirements.txt is up to date
pip freeze | diff requirements.txt -

# Install specific version of a package
pip install "fastapi==0.116.1"

# Uninstall a package
pip uninstall package-name

# Then update requirements.txt
pip freeze > requirements.txt
```
