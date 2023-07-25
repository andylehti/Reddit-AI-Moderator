#!/bin/bash

# Install necessary system packages
sudo apt-get update && sudo apt-get -y upgrade
sudo apt-get install -y python3-pip python3-dev
sudo apt-get install -y libsm6 libxext6 libxrender-dev
pip install nltk transformers vaderSentiment

# Clone the repository and navigate into it
git clone https://github.com/andylehti/Reddit-AI-Moderator.git
cd Reddit-AI-Moderator

# Create a Python virtual environment and activate it
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install the Python and Node packages
pip install praw easyocr nltk
npm install nsfwjs
pip install -r requirements.txt

# Prompt the user for their Reddit API credentials
echo "Please enter your Reddit API credentials:"
read -p 'Client ID: ' client_id
read -p 'Client Secret: ' client_secret
read -p 'User Agent: ' user_agent
read -p 'Username: ' username
read -p 'Password: ' password

# Prompt the user for their subreddit
read -p 'Enter your subreddit: ' subreddit

# Write the credentials to a JSON file
echo "{
  \"client_id\": \"$client_id\",
  \"client_secret\": \"$client_secret\",
  \"user_agent\": \"$user_agent\",
  \"username\": \"$username\",
  \"password\": \"$password\"
}" > credentials.json

# Ask the user for their scoring preferences
echo 'All removed comments and posts will have their sentiment scores commented by this bot regardless of the choices below:'
read -p 'Do you want the bot to comment the bias and sentiment score for every post? (yes/no) ' score_posts
read -p 'Do you want the bot to comment the bias and sentiment score for every comment? (yes/no) ' score_comments

echo "#!/usr/bin/env python3
import praw
import json
from suremod import SubredditModerator

with open('credentials.json') as f:
    creds = json.load(f)

reddit = praw.Reddit(
  client_id=creds['client_id'],
  client_secret=creds['client_secret'],
  user_agent=creds['user_agent'],
  username=creds['username'],
  password=creds['password']
)

subreddit = reddit.subreddit('$subreddit')
moderator = SubredditModerator(subreddit, score_posts='$score_posts', score_comments='$score_comments')
moderator.start_moderating()" > suremod.py

# Make the script executable
chmod +x suremod.py

# Add the script to crontab so that it will run on startup
(crontab -l 2>/dev/null; echo "@reboot nohup $PWD/venv/bin/python $PWD/suremod.py &") | crontab -

echo "Installation completed successfully. The bot will now start automatically whenever the server is rebooted."
