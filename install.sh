#!/bin/bash

sudo apt install python3.10-venv
echo "This will reboot at the end. Cancel now if you do not wish for this to happen."

# Install necessary system packages
sudo apt-get update && sudo apt-get -y upgrade
sudo apt-get install -y python3-pip python3-dev cron
sudo apt-get install -y libsm6 libxext6 libxrender-dev
sudo apt-get install -y nodejs npm

# Install packages with pip
pip install --upgrade pip
pip install nltk transformers vaderSentiment fuzzywuzzy pytesseract praw easyocr

# Clone the repository and navigate into it
git clone https://github.com/andylehti/Reddit-AI-Moderator.git
cd Reddit-AI-Moderator

# Create a Python virtual environment and activate it
python3 -m venv venv
source venv/bin/activate

# Upgrade pip and install required packages
pip install --upgrade pip
pip install -r requirements.txt
npm install nsfwjs

# Run the configuration script
./configure.sh

echo "Installation completed successfully. The system will now reboot."
sudo reboot
