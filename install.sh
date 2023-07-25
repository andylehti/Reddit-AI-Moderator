#!/bin/bash

# Install necessary system packages
sudo apt-get update && sudo apt-get -y upgrade
sudo apt-get install -y python3-pip python3-dev cron
sudo apt-get install -y libsm6 libxext6 libxrender-dev
sudo apt-get install -y nodejs npm
pip install nltk transformers vaderSentiment

# Add Python user bin to PATH
echo "export PATH=$PATH:/home/$USER/.local/bin" >> ~/.bashrc
source ~/.bashrc

# Clone the repository and navigate into it
git clone https://github.com/andylehti/Reddit-AI-Moderator.git
cd Reddit-AI-Moderator

# Create a Python virtual environment and activate it
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
pip install -r requirements.txt
# Install the Python and Node packages
pip install praw easyocr nltk
npm install nsfwjs
#!/bin/bash
