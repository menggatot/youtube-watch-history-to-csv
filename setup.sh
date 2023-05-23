#!/bin/bash

# Create a virtual environment
python3 -m venv yt-history-env

# Activate the virtual environment
source yt-history-env/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install colorama beautifulsoup4 yt-dlp lxml

echo ""
echo -e "\e[32mSetup completed successfully!\e[0m"
echo ""
echo -e "You can activate the virtual environment by running:"
echo -e "source yt-history-env/bin/activate"
