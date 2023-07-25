#!/bin/bash

# Go into the directory
cd Reddit-AI-Moderator

# Activate virtual environment
source venv/bin/activate

echo "Please enter your Reddit API credentials (separate by '|') or one by one starting with client_id:"
read input

IFS='|' read -ra CREDENTIALS <<< "$input"

if [ ${#CREDENTIALS[@]} -eq 5 ]; then
  client_id=${CREDENTIALS[0]}
  client_secret=${CREDENTIALS[1]}
  user_agent=${CREDENTIALS[2]}
  username=${CREDENTIALS[3]}
  password=${CREDENTIALS[4]}
else
  read -p 'Client ID: ' client_id
  read -p 'Client Secret: ' client_secret
  read -p 'User Agent: ' user_agent
  read -p 'Username: ' username
  read -p 'Password: ' password
fi

# Set environment variables
export CLIENT_ID=$client_id
export CLIENT_SECRET=$client_secret
export USER_AGENT=$user_agent
export USERNAME=$username
export PASSWORD=$password

# Check for empty strings
if [ -z "$client_id" ] || [ -z "$client_secret" ] || [ -z "$user_agent" ] || [ -z "$username" ] || [ -z "$password" ]; then
  echo "Error: You must enter all Reddit API credentials."
  exit 1
fi

# Prompt the user for their subreddit
read -p 'Enter your subreddit: ' subreddit

# Set environment variable
export SUBREDDIT=$subreddit

if [ -z "$subreddit" ]; then
  echo "Error: You must enter a subreddit."
  exit 1
fi

# Validate Reddit API credentials
response=$(curl -s -I -u $username:$password https://www.reddit.com/api/v1/me.json -A $user_agent | grep HTTP)
http_code=$(echo $response | cut -d' ' -f2)

if [ "$http_code" != "200" ]; then
  echo "Error: Invalid Reddit API credentials."
  exit 1
fi

# Ask the user for their scoring preferences
echo 'All removed comments and posts will have their sentiment scores commented by this bot regardless of the choices below:'
read -p 'Do you want the bot to comment the bias and sentiment score for every post? (yes/no) ' score_posts
read -p 'Do you want the bot to comment the bias and sentiment score for every comment? (yes/no) ' score_comments

# Set environment variables
export SCORE_POSTS=$score_posts
export SCORE_COMMENTS=$score_comments

# start_mod.py

echo "#!/usr/bin/env python3
import os
import nltk
import praw
import json
from ai_automod import SubredditModerator

def install_nltk_data():
    nltk.download('punkt')
    nltk.download('vader_lexicon')

install_nltk_data()

reddit = praw.Reddit(
  client_id=os.environ['CLIENT_ID'],
  client_secret=os.environ['CLIENT_SECRET'],
  user_agent=os.environ['USER_AGENT'],
  username=os.environ['USERNAME'],
  password=os.environ['PASSWORD']
)

subreddit = reddit.subreddit(os.environ['SUBREDDIT'])
moderator = SubredditModerator(subreddit, score_posts=os.environ['SCORE_POSTS'] == 'yes', score_comments=os.environ['SCORE_COMMENTS'] == 'yes')
moderator.start_moderating()" > start_mod.py

# Make the script executable
chmod +x start_mod.py

# Add the script to crontab so that it will run on startup
(crontab -l 2>/dev/null; echo "@reboot nohup $PWD/venv/bin/python $PWD/suremod.py &") | crontab -

echo "Installation completed successfully. The bot will now start automatically whenever the server is rebooted."
