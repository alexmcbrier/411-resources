#!/bin/bash

# Set the name of the virtual environment directory and requirements file
VENV_DIR="venv"
REQUIREMENTS_FILE="requirements.txt"

# Check if the virtual environment already exists
if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtual environment..."

  # Create the virtual environment
  python3 -m venv "$VENV_DIR"

  # Activate the virtual environment
  source "$VENV_DIR/bin/activate"

  # Install dependencies from requirements.txt
  if [ -f "$REQUIREMENTS_FILE" ]; then
    echo "Installing dependencies from $REQUIREMENTS_FILE..."
    pip install --upgrade pip
    pip install -r "$REQUIREMENTS_FILE"
    pip install pytest pytest-mock
  else
    echo "Error: $REQUIREMENTS_FILE not found."
    exit 1
  fi

  echo "Virtual environment setup complete."
else
  echo "Virtual environment already exists. Activating..."
  source "$VENV_DIR/bin/activate"
fi
