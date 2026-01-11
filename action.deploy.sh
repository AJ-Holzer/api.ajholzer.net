#!/bin/bash

# Define paths
REPO_PATH="/opt/api.ajholzer.net"
VENV_PATH=".venv"

# Go to repo path or exit if it does not exist
cd "$REPO_PATH" || exit 1

# Clear repo and pull from github
echo "Cleaning and pulling from GitHub..."
git reset --hard HEAD
git clean -fd
git pull origin main

# Create venv
if [! -d "$VENV_PATH"]; then
    python3 -m venv "$VENV_PATH"
fi

# Activate venv
source "$VENV_PATH/bin/activate"

# Upgrade pip
pip3 install --upgrade pip

# Install requirements
pip3 install -r "$REPO_PATH/requirements.txt"

# Restart api
sudo systemctl restart api.ajholzer.net
