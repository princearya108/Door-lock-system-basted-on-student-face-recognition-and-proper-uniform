#!/bin/bash

# Door Lock System Start Script
# This script helps start the system components

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}$1${NC}"
}

# Check if Python is installed
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    print_status "Python 3 found: $(python3 --version)"
}

# Check if virtual environment exists
check_venv() {
    if [ ! -d "venv" ]; then
        print_warning "Virtual environment not found"
        read -p "Do you want to create one? (y/n): " create_venv
        if [ "$create_venv" = "y" ]; then
            python3 -m venv venv
            print_status "Virtual environment created"
        fi
    fi
}

# Activate virtual environment
activate_venv() {
    if [ -d "venv" ]; then
        source venv/bin/activate
        print_status "Virtual environment activated"
    else
        print_warning "No virtual environment found, using system Python"
    fi
}

# Install dependencies
install_deps() {
    print_status "Installing dependencies..."
    pip install -r requirements.txt
}

# Start API server
start_api() {
    print_header "Starting API Server..."
    python main.py --mode api &
    API_PID=$!
    print_status "API server started (PID: $API_PID)"
}

# Start Dashboard
start_dashboard() {
    print_header "Starting Dashboard..."
    python main.py --mode dashboard &
    DASHBOARD_PID=$!
    print_status "Dashboard started (PID: $DASHBOARD_PID)"
}

# Start both
start_both() {
    print_header "Starting Complete System..."
    python main.py --mode both
}

# Setup system
setup_system() {
    print_header "Setting up Door Lock System..."
    python scripts/setup.py
}

# Show help
show_help() {
    echo "Door Lock System Control Script"
    echo ""
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  setup     - Run system setup"
    echo "  api       - Start only API server"
    echo "  dashboard - Start only dashboard"
    echo "  both      - Start both API and dashboard (default)"
    echo "  install   - Install dependencies"
    echo "  help      - Show this help message"
    echo ""
}

# Cleanup function
cleanup() {
    print_warning "Shutting down..."
    if [ ! -z "$API_PID" ]; then
        kill $API_PID 2>/dev/null
        print_status "API server stopped"
    fi
    if [ ! -z "$DASHBOARD_PID" ]; then
        kill $DASHBOARD_PID 2>/dev/null
        print_status "Dashboard stopped"
    fi
    exit 0
}

# Trap Ctrl+C
trap cleanup SIGINT

# Main script
main() {
    print_header "🚪 Door Lock System"
    print_header "====================="
    
    check_python
    
    case "${1:-both}" in
        "setup")
            setup_system
            ;;
        "api")
            check_venv
            activate_venv
            start_api
            wait $API_PID
            ;;
        "dashboard") 
            check_venv
            activate_venv
            start_dashboard
            wait $DASHBOARD_PID
            ;;
        "both")
            check_venv
            activate_venv
            start_both
            ;;
        "install")
            check_venv
            activate_venv
            install_deps
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
