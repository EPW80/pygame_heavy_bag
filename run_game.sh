#!/bin/bash

# Heavy Bag Training Game Launcher
# This script activates the virtual environment and runs the game

echo "Starting Heavy Bag Training Game..."
echo "=====================================+"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found!"
    echo "Please run the setup commands first:"
    echo "python -m venv venv"
    echo "source venv/bin/activate"
    echo "pip install pygame"
    exit 1
fi

# Activate virtual environment and run the game
source venv/bin/activate
python -m src.main

echo "Game ended. Thanks for playing!"
