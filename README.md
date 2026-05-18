# CoderrBE - Backend API

A Django REST Framework application providing a complete backend API for the Coderr platform. The project includes multiple apps for managing authentication, offers, orders, reviews, user profiles, and base information.

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Windows](#windows-installation)
  - [Linux](#linux-installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Troubleshooting](#troubleshooting)

## Features

- User authentication and registration
- User profile management
- Offer management (create, read, update, delete)
- Order processing and tracking
- Review system
- Role-based access control
- CORS support for frontend integration
- Comprehensive test coverage with pytest
- RESTful API endpoints

## Technology Stack

- **Python**: 3.14
- **Django**: 6.0.4
- **Django REST Framework**: 3.17.1
- **Database**: SQLite (default)
- **Testing**: pytest, pytest-django, pytest-cov
- **Additional**: django-cors-headers, python-dotenv, Pillow

## Prerequisites

### Windows

- Python 3.10+ (download from [python.org](https://www.python.org))
- Git (optional, for version control)
- pip (included with Python)

### Linux

- Python 3.10+
- pip
- venv (usually included with Python)

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv

# Fedora/RHEL/CentOS
sudo dnf install python3 python3-pip

# Arch Linux
sudo pacman -S python python-pip
```

## Installation

### Windows Installation

1. **Clone or navigate to the project directory:**

```powershell
cd path\to\CoderrBE
```

2. **Create a virtual environment:**

```powershell
python -m venv env
```

3. **Activate the virtual environment:**

```powershell
.\env\Scripts\Activate.ps1
```

> **Note:** If you encounter an execution policy error, run:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

4. **Install dependencies:**

```powershell
pip install -r requirements.txt
```

5. **Set up environment variables:**

Copy the `env.template` file to `.env` and update the configuration:

```powershell
Copy-Item env.template .env
```

Edit the `.env` file and set your `SECRET_KEY` and other configuration options:

```
SECRET_KEY=your-secret-key-here
DEBUG=True
```

6. **Run database migrations:**

```powershell
python manage.py migrate
```

7. **Create a superuser (admin):**

```powershell
python manage.py createsuperuser
```

### Linux Installation

1. **Clone or navigate to the project directory:**

```bash
cd /path/to/CoderrBE
```

2. **Create a virtual environment:**

```bash
python3 -m venv env
```

3. **Activate the virtual environment:**

```bash
source env/bin/activate
```

4. **Install dependencies:**

```bash
pip install -r requirements.txt
```

5. **Set up environment variables:**

Copy the `env.template` file to `.env`:

```bash
cp env.template .env
```

Edit the `.env` file and set your configuration:

```
SECRET_KEY=your-secret-key-here
DEBUG=True
```

6. **Run database migrations:**

```bash
python manage.py migrate
```

7. **Create a superuser (admin):**

```bash
python manage.py createsuperuser
```

## Configuration

### Environment Variables

The project uses a `.env` file for configuration. Copy `env.template` to `.env` and configure:

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key for security | (required) |
| `DEBUG` | Debug mode (True/False) | `True` |

### CORS Configuration

CORS is pre-configured for local development. Edit `core/settings.py` to update:

```python
CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:5500',
    'http://localhost:5500',
]

CORS_ALLOWED_ORIGINS = [
    'http://127.0.0.1:5500',
    'http://localhost:5500',
]
```

## Running the Application

### Start the Development Server

#### Windows

```powershell
# Make sure virtual environment is activated
.\env\Scripts\Activate.ps1

# Run the development server
python manage.py runserver
```

#### Linux

```bash
# Activate virtual environment
source env/bin/activate

# Run the development server
python manage.py runserver
```

The server will start at `http://127.0.0.1:8000/`

### Access the Admin Panel

1. Start the development server (see above)
2. Navigate to `http://127.0.0.1:8000/admin/`
3. Log in with the superuser credentials you created

## Testing

The project uses pytest for testing with comprehensive test coverage.

### Run All Tests

#### Windows

```powershell
pytest
```

#### Linux

```bash
pytest
```

### Run Tests for Specific App

#### Windows

```powershell
pytest auth_app/tests/
pytest offers_app/tests/
pytest orders_app/tests/
```

#### Linux

```bash
pytest auth_app/tests/
pytest offers_app/tests/
pytest orders_app/tests/
```

### Run Tests with Coverage Report

#### Windows

```powershell
pytest --cov=. --cov-report=html
```

#### Linux

```bash
pytest --cov=. --cov-report=html
```

The coverage report will be generated in `htmlcov/index.html`

### Available Test Files

- `auth_app/tests/test_login.py` - Login functionality tests
- `auth_app/tests/test_registration.py` - User registration tests
- `base_info_app/tests/test_base_info.py` - Base information tests
- `offers_app/tests/test_offers_*.py` - Offer management tests
- `orders_app/tests/test_order_*.py` - Order management tests

## Project Structure

```
CoderrBE/
├── core/                          # Django core settings
│   ├── settings.py               # Main settings file
│   ├── urls.py                   # URL routing configuration
│   ├── asgi.py                   # ASGI configuration
│   └── wsgi.py                   # WSGI configuration
│
├── auth_app/                      # User authentication and registration
│   ├── api/
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── models.py
│   ├── tests/
│   │   ├── test_login.py
│   │   └── test_registration.py
│   └── ...
│
├── profiles_app/                  # User profiles
│   ├── api/
│   ├── models.py
│   ├── tests/
│   └── ...
│
├── offers_app/                    # Offer management
│   ├── api/
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── models.py
│   ├── tests/
│   │   ├── test_offer_delete.py
│   │   ├── test_offer_detail.py
│   │   ├── test_offers_create.py
│   │   └── ...
│   └── ...
│
├── orders_app/                    # Order processing
│   ├── api/
│   ├── models.py
│   ├── tests/
│   │   └── test_order_count.py
│   └── ...
│
├── reviews_app/                   # Review system
│   ├── api/
│   ├── models.py
│   ├── tests/
│   └── ...
│
├── base_info_app/                 # Base information
│   ├── api/
│   ├── models.py
│   ├── tests/
│   │   └── test_base_info.py
│   └── ...
│
├── manage.py                      # Django management script
├── requirements.txt               # Python dependencies
├── pytest.ini                     # Pytest configuration
├── env.template                   # Environment variables template
├── db.sqlite3                     # SQLite database (auto-generated)
└── README.md                      # This file
```

## API Documentation

The API uses RESTful principles. Each app provides API endpoints through DRF (Django REST Framework).

### Available Apps with API Endpoints

- **auth_app** - User authentication endpoints
- **profiles_app** - User profile management
- **offers_app** - Offer CRUD operations
- **orders_app** - Order management
- **reviews_app** - Review management
- **base_info_app** - Base information endpoints

For detailed API documentation, refer to the individual app's `api/views.py` files.

## Troubleshooting

### Common Issues

#### Issue: `ModuleNotFoundError: No module named 'django'`

**Solution:** Make sure your virtual environment is activated:

**Windows:**
```powershell
.\env\Scripts\Activate.ps1
```

**Linux:**
```bash
source env/bin/activate
```

Then run:
```bash
pip install -r requirements.txt
```

#### Issue: `SECRET_KEY not found` or `environ error`

**Solution:** Create a `.env` file from the template:

**Windows:**
```powershell
Copy-Item env.template .env
```

**Linux:**
```bash
cp env.template .env
```

Edit the `.env` file and ensure `SECRET_KEY` is set.

#### Issue: Database error / `OperationalError`

**Solution:** Run migrations:

```bash
python manage.py migrate
```

#### Issue: `CORS errors` when connecting from frontend

**Solution:** Update `CORS_ALLOWED_ORIGINS` in `core/settings.py` with your frontend URL.

#### Issue: Port 8000 already in use

**Solution:** Use a different port:

```bash
python manage.py runserver 8001
```

#### Issue: Permission denied on Linux

**Solution:** Make manage.py executable:

```bash
chmod +x manage.py
```

### Getting Help

1. Check Django documentation: https://docs.djangoproject.com/
2. Check DRF documentation: https://www.django-rest-framework.org/
3. Review pytest documentation: https://docs.pytest.org/
4. Check test files in `*/tests/` directories for examples

## Development Workflow

1. Create a new branch for features
2. Write tests for new functionality
3. Run tests to ensure coverage
4. Make commits with clear messages
5. Push changes and create a pull request
