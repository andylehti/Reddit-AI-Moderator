#!/bin/bash

sudo apt install python3.10-venv
echo "this will reboot at the end, cancel now if you do not wish this to happen."
sudo apt-get update && sudo apt-get -y upgrade
sudo apt-get install -y python3-pip python3-dev cron
sudo apt-get install -y libsm6 libxext6 libxrender-dev
sudo apt-get install -y nodejs npm

pip install nltk transformers vaderSentiment fuzzywuzzy pytesseract praw python-dotenv python-Levenshtein
python -m nltk.downloader punkt vader_lexicon

echo "export PATH=$PATH:/home/$USER/.local/bin" >> ~/.bashrc
source ~/.bashrc

git clone https://github.com/andylehti/Reddit-AI-Moderator.git
cd Reddit-AI-Moderator

python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
pip install easyocr
npm install nsfwjs

echo "Installation completed successfully."
