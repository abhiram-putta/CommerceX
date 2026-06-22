#!/bin/bash

# sMart E-Commerce Backend Setup Script
# This script automates the setup process for the sMart backend

set -e  # Exit on error

echo "=================================================="
echo "  sMart E-Commerce Backend Setup"
echo "=================================================="
echo ""

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "→ $1"
}

# Check if running from project root
if [ ! -f "app/main.py" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

print_info "Starting setup process..."
echo ""

# Step 1: Check Python version
print_info "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then
    print_success "Python $PYTHON_VERSION detected"
else
    print_error "Python 3.10+ required. Found: $PYTHON_VERSION"
    exit 1
fi
echo ""

# Step 2: Create virtual environment
print_info "Creating virtual environment..."
if [ -d "venv" ]; then
    print_warning "Virtual environment already exists. Skipping..."
else
    python3 -m venv venv
    print_success "Virtual environment created"
fi
echo ""

# Step 3: Activate virtual environment
print_info "Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated"
echo ""

# Step 4: Upgrade pip
print_info "Upgrading pip..."
pip install --upgrade pip --quiet
print_success "Pip upgraded"
echo ""

# Step 5: Install dependencies
print_info "Installing dependencies..."
print_info "This may take a few minutes..."

if pip install -r requirements/base.txt --quiet; then
    print_success "Base dependencies installed"
else
    print_error "Failed to install base dependencies"
    exit 1
fi

if pip install -r requirements/ml.txt --quiet; then
    print_success "ML dependencies installed"
else
    print_warning "Failed to install ML dependencies (optional)"
fi

if pip install -r requirements/dev.txt --quiet; then
    print_success "Development dependencies installed"
else
    print_warning "Failed to install dev dependencies (optional)"
fi
echo ""

# Step 6: Set up environment file
print_info "Setting up environment variables..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_success "Created .env file from .env.example"
        print_warning "Please update .env with your configuration!"
    else
        print_warning "No .env.example found. You'll need to create .env manually"
    fi
else
    print_warning ".env file already exists"
fi
echo ""

# Step 7: Check PostgreSQL
print_info "Checking PostgreSQL..."
if command -v psql &> /dev/null; then
    print_success "PostgreSQL is installed"

    # Try to connect
    if pg_isready &> /dev/null; then
        print_success "PostgreSQL is running"
    else
        print_warning "PostgreSQL is not running. Please start it:"
        print_info "  brew services start postgresql@14  (macOS)"
        print_info "  sudo service postgresql start       (Linux)"
    fi
else
    print_warning "PostgreSQL not found. Please install it:"
    print_info "  brew install postgresql@14  (macOS)"
    print_info "  sudo apt install postgresql (Ubuntu)"
fi
echo ""

# Step 8: Check Redis
print_info "Checking Redis..."
if command -v redis-cli &> /dev/null; then
    print_success "Redis is installed"

    # Try to ping Redis
    if redis-cli ping &> /dev/null 2>&1; then
        print_success "Redis is running"
    else
        print_warning "Redis is not running. Please start it:"
        print_info "  brew services start redis  (macOS)"
        print_info "  sudo service redis start   (Linux)"
    fi
else
    print_warning "Redis not found. Please install it:"
    print_info "  brew install redis  (macOS)"
    print_info "  sudo apt install redis-server (Ubuntu)"
fi
echo ""

# Step 9: Database setup
print_info "Database setup..."
read -p "Do you want to set up the database? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "Enter database name (default: smart_db): " DB_NAME
    DB_NAME=${DB_NAME:-smart_db}

    if psql -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
        print_warning "Database $DB_NAME already exists"
    else
        createdb "$DB_NAME" && print_success "Database $DB_NAME created"
    fi

    # Run migrations
    print_info "Running database migrations..."
    if alembic upgrade head; then
        print_success "Migrations completed"
    else
        print_error "Migration failed. Please check your database connection"
    fi
fi
echo ""

# Step 10: Generate sample data
print_info "Sample data generation..."
read -p "Do you want to generate sample data? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -f "scripts/generate_mock_data.py" ]; then
        print_info "Generating mock data..."
        python scripts/generate_mock_data.py
        print_success "Mock data generated"
    fi

    if [ -f "scripts/realistic_product_data.py" ]; then
        print_info "Generating realistic product data..."
        python scripts/realistic_product_data.py
        print_success "Realistic product data generated"
    fi
fi
echo ""

# Step 11: Train ML models
print_info "ML model training..."
read -p "Do you want to train ML models? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -f "scripts/train_ml_models.py" ]; then
        print_info "Training ML models..."
        print_info "This may take several minutes..."
        python scripts/train_ml_models.py
        print_success "ML models trained"
    fi
fi
echo ""

# Step 12: Run tests
print_info "Testing..."
read -p "Do you want to run tests? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Running tests..."
    pytest -v
fi
echo ""

# Summary
echo "=================================================="
echo "  Setup Complete! 🎉"
echo "=================================================="
echo ""
print_success "Installation successful!"
echo ""
echo "Next steps:"
echo ""
print_info "1. Update .env file with your configuration"
print_info "2. Ensure PostgreSQL and Redis are running"
print_info "3. Start the application:"
echo "   uvicorn app.main:app --reload"
echo ""
print_info "4. Access the API documentation:"
echo "   http://localhost:8000/docs"
echo ""
print_info "5. Check the health endpoint:"
echo "   http://localhost:8000/health"
echo ""
echo "For detailed setup instructions, see SETUP_GUIDE.md"
echo "For API documentation, see API_DOCUMENTATION.md"
echo ""
echo "=================================================="
