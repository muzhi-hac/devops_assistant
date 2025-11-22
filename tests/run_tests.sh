#!/bin/bash
# Automated test runner script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "=========================================="
echo "Parallax OpsPilot - Automated Tests"
echo "=========================================="
echo ""

# Check if pop is installed
if ! command -v pop &> /dev/null; then
    echo "❌ Error: 'pop' command not found"
    echo "Please install the project first:"
    echo "  pip install -e ."
    exit 1
fi

# Check if Parallax is running
if ! curl -s http://localhost:3000/v1/models > /dev/null 2>&1; then
    echo "⚠️  Warning: Parallax API not accessible at http://localhost:3000"
    echo "Please start Parallax first:"
    echo "  parallax run -m Qwen/Qwen3-0.6B --host 0.0.0.0"
    echo ""
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Run tests
echo "Running automated tests..."
echo ""

python3 -m pytest tests/test_runner.py::main -v 2>/dev/null || \
python3 tests/test_runner.py --verbose 2>/dev/null || \
python3 -m tests.test_runner 2>/dev/null || {
    echo "Running test runner directly..."
    cd "$PROJECT_DIR"
    export PATH="$HOME/.local/bin:$PATH"
    python3 "$SCRIPT_DIR/test_runner.py" --verbose
}

echo ""
echo "=========================================="
echo "Tests completed"
echo "=========================================="

