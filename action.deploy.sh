#!/bin/bash

# Define paths
REPO_PATH="/opt/api.ajholzer.net"
VENV_PATH=".venv"

# Go to repo path or exit if it does not exist
cd "$REPO_PATH" || exit 1



# ################### #
#  Update local repo  #
# ################### #

# Clear repo and pull from github
echo "Cleaning and pulling from GitHub..."
git reset --hard HEAD
git clean -fd
git pull origin main



# ############################# #
#  Install python requirements  #
# ############################# #

# Create venv
if [ ! -d "$VENV_PATH" ]; then
    python3 -m venv "$VENV_PATH"
fi

# Activate venv
source "$VENV_PATH/bin/activate"

# Upgrade pip
echo "Upgrading pip..."
pip3 install --upgrade pip

# Install requirements
echo "Installing pip requirements..."
pip3 install -r "$REPO_PATH/requirements.txt"

# Restart api
echo "Restarting API..."
sudo /bin/systemctl restart api.ajholzer.net.service
