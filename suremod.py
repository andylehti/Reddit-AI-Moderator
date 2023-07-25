# AntiBiasMod

import os
import getpass
import praw
import time
import requests
from fuzzywuzzy import fuzz
from PIL import Image
import pytesseract
from nltk.sentiment import SentimentIntensityAnalyzer
from transformers import AutoTokenizer, TFAutoModelForSequenceClassification, pipeline
import nltk

nltk.download('punkt')
nltk.download('vader_lexicon')

class SubredditModerator:
    def __init__(self, subreddit, banned_phrases):
        self.subreddit = subreddit
        self.banned_phrases = banned_phrases
        self.analyzer = SentimentIntensityAnalyzer()
        self.tokenizer = AutoTokenizer.from_pretrained("d4data/bias-detection-model")
        self.model = TFAutoModelForSequenceClassification.from_pretrained("d4data/bias-detection-model")
        self.classifier = pipeline('text-classification', model=self.model, tokenizer=self.tokenizer)

    def process_submission(self, submission):
        if self.check_banned_phrases(submission) or self.check_nsfw_content(submission):
            return False, "Content does not meet criteria"

        bias_score, bias_label = self.check_bias(submission.title + submission.selftext)
        if float(bias_score) > 5:
            return False, f"Bias detected. Score: {bias_score}, Label: {bias_label}"

        submission.comments.replace_more(limit=None)
        for comment in submission.comments.list():
            bias_score, bias_label = self.check_bias(comment.body)
            if float(bias_score) > 0.5:
                return False, f"Bias detected in comment. Score: {bias_score}, Label: {bias_label}"

        return True, "Submission meets all criteria"

    def check_banned_phrases(self, submission):
        for phrase in self.banned_phrases:
            if fuzz.partial_ratio(phrase, submission.title) > 80 or fuzz.partial_ratio(phrase, submission.selftext) > 80:
                return True
        return False

    def check_nsfw_content(self, submission):
        if submission.over_18:
            return True
        if 'imgur.com' in submission.url or 'i.redd.it' in submission.url:
            image = Image.open(requests.get(submission.url, stream=True).raw)
            text = pytesseract.image_to_string(image)
            if fuzz.partial_ratio('NSFW', text) > 80:
                return True
        return False

    def check_bias(self, text):
        result = self.classifier(text)
        return result[0]['score'], result[0]['label']

def main():
    reddit = praw.Reddit(client_id=os.getenv('REDDIT_CLIENT_ID'), 
                         client_secret=os.getenv('REDDIT_CLIENT_SECRET'), 
                         user_agent=os.getenv('REDDIT_USER_AGENT'), 
                         username=os.getenv('REDDIT_USERNAME'), 
                         password=os.getenv('REDDIT_PASSWORD'))

    subreddit_name = getpass.getpass(prompt="Subreddit: ")

    with open('banned_phrases.txt', 'r') as f:
        banned_phrases = [line.strip() for line in f.readlines()]  # Read banned phrases from file

    moderator = SubredditModerator(reddit.subreddit(subreddit_name), banned_phrases)

    # Get the 100 most recent posts
    most_recent_posts = [post for post in moderator.subreddit.new(limit=100)]

    while True:
        time.sleep(10)  # Wait for 10 seconds

        # Get the 100 most recent posts again
        new_most_recent_posts = [post for post in moderator.subreddit.new(limit=100)]

        # Find the new posts that were not in the old list of most recent posts
        new_posts = [post for post in new_most_recent_posts if post not in most_recent_posts]

        # Process the new posts (moderation actions, etc.)
        for submission in new_posts:
            is_submission_ok, reason = moderator.process_submission(submission)
            if not is_submission_ok:
                submission.mod.remove()  # Remove submission if it does not meet the criteria
                submission.reply(reason)  # Comment the reason for removal

        # Update the list of most recent posts
        most_recent_posts = new_most_recent_posts
