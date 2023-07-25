#!/bin/bash

# Go into the directory
cd Reddit-AI-Moderator

# Activate virtual environment
source venv/bin/activate

# Prompt the user for their Reddit API credentials
echo "Please enter your Reddit API credentials:"
read -p 'Client ID: ' client_id
read -p 'Client Secret: ' client_secret
read -p 'User Agent: ' user_agent
read -p 'Username: ' username
read -p 'Password: ' password

# Check for empty strings
if [ -z "$client_id" ] || [ -z "$client_secret" ] || [ -z "$user_agent" ] || [ -z "$username" ] || [ -z "$password" ]; then
  echo "Error: You must enter all Reddit API credentials."
  exit 1
fi

# Prompt the user for their subreddit
read -p 'Enter your subreddit: ' subreddit

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

# Write the credentials to a JSON file
echo "{
  \"client_id\": \"$client_id\",
  \"client_secret\": \"$client_secret\",
  \"user_agent\": \"$user_agent\",
  \"username\": \"$username\",
  \"password\": \"$password\"
}" > credentials.json

echo "#!/usr/bin/env python3
import praw
import json
from ai-automod import SubredditModerator

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
moderator.start_moderating()" > start-mod.py

# Make the script executable
chmod +x start-mod.py

# Add the script to crontab so that it will run on startup
(crontab -l 2>/dev/null; echo "@reboot nohup $PWD/venv/bin/python $PWD/suremod.py &") | crontab -

echo "Installation completed successfully. The bot will now start automatically whenever the server is rebooted."
