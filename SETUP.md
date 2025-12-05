# Python Environment Setup

## Requirements

- **Python Version:** 3.9 or higher
- **Operating System:** Windows 10/11 (64-bit)
- **Package Manager:** pip

## Installation Steps

### 1. Check Python Version

```bash
python --version
```

Ensure you have Python 3.9 or higher installed.

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# On Linux/Mac (if needed for development)
source venv/bin/activate
```

### 3. Upgrade pip

```bash
python -m pip install --upgrade pip
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

```bash
# Copy the example environment file
copy .env.example .env

# Edit .env and add your configuration:
# - GEMINI_API_KEY: Your Google Gemini API key
# - DATABASE_PATH: Path to SQLite database (default: ./data/maas.db)
# - ACSOFT_PATH: Path to ACSoft executable
# - etc.
```

### 6. Initialize Database

```bash
python scripts/init_db.py
```

### 7. Verify Installation

```bash
# Run tests
pytest

# Check code style
flake8 app/

# Format code
black app/
```

## Development Environment

### Recommended IDE Setup

- **VS Code** with extensions:
  - Python
  - Pylance
  - Black Formatter
  - Flake8
  - pytest

### Code Quality Tools

- **Black:** Code formatter (configured in pyproject.toml)
- **Flake8:** Linter (configured in .flake8)
- **pytest:** Testing framework (configured in pytest.ini)
- **mypy:** Type checker (configured in pyproject.toml)

### Running the Application

```bash
# Start the server
uvicorn app.main:app --reload

# Or use the run script (to be created in Phase 1)
python run.py
```

## Troubleshooting

### Virtual Environment Issues

If you have issues activating the virtual environment:

```bash
# Windows PowerShell may require execution policy change
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Package Installation Issues

If you encounter package installation errors:

```bash
# Upgrade pip and setuptools
python -m pip install --upgrade pip setuptools wheel

# Install packages one by one to identify issues
pip install fastapi
pip install uvicorn
# etc.
```

### Import Errors

Ensure your PYTHONPATH includes the project root:

```bash
# Windows
set PYTHONPATH=%PYTHONPATH%;C:\path\to\mom_project

# Linux/Mac
export PYTHONPATH="${PYTHONPATH}:/path/to/mom_project"
```

## Next Steps

After setting up the environment:

1. Read `TECHNICAL_SPECS.md` for system architecture
2. Read `spec/Requirements.md` for functional requirements
3. Read `spec/Design.md` for design decisions
4. Check `spec/Tasks.md` for implementation tasks
5. Review `CONTRIBUTING.md` for development guidelines

## Support

For issues or questions:
- Check `docs/user/troubleshooting.md`
- Review logs in `logs/maas.log`
- Create an issue on GitHub
