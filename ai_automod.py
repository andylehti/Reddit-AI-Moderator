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
from dotenv import load_dotenv
from transformers import pipeline, AutoTokenizer, TFAutoModelForSequenceClassification
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from fuzzywuzzy import fuzz


class SubredditModerator:
    def __init__(self, subreddit, banned_phrases):
        self.subreddit = subreddit
        self.banned_phrases = banned_phrases
        self.analyzer = SentimentIntensityAnalyzer()
        self.tokenizer = AutoTokenizer.from_pretrained("d4data/bias-detection-model")
        self.model = TFAutoModelForSequenceClassification.from_pretrained("d4data/bias-detection-model")
        self.classifier = pipeline('text-classification', model=self.model, tokenizer=self.tokenizer)


    def adhominem_detector(self, text):
        adhominem_pipeline = pipeline("text-classification", model="delboc/ComputationalAdHominemDetection")
        result = adhominem_pipeline(text)
        return result[0]['label'], result[0]['score']
    
    def process_comments(self):
        subreddits = self.config["subreddits"]
        mod_subs = "+".join(subreddits)
        
        for comment in self.reddit.subreddit(mod_subs).stream.comments(skip_existing=True):
            adhominem_label, adhominem_score = self.adhominem_detector(comment.body)
            bias_label, bias_score = self.bias_detector(comment.body)
            sentiment_score = self.sentiment_analyzer(comment.body)
            is_phrase_match = self.check_fuzzy_match(comment.body, self.config["phrases"])
            
            should_remove = ((adhominem_label == "ADHOMINEM" and adhominem_score > 0.45)
                            or (bias_label == "BIAS" and bias_score > 0.49)
                            or sentiment_score < -0.5
                            or is_phrase_match)
            
            if should_remove:
                comment.mod.remove()
                comment.reply(f"**Comment Removed**\nComment Analysis:\nSentiment score: {sentiment_score}\nAd hominem score: {adhominem_score}\nBias score: {bias_score}")
            elif adhominem_score >= 0.3 or bias_score >= 0.3 or sentiment_score <= -0.3:
                comment.reply(f"Comment Analysis:\nSentiment score: {sentiment_score}\nAd hominem score: {adhominem_score}\nBias score: {bias_score}")
            elif comment.author == "Antibotty":
                parent_comment = comment.parent()
                if isinstance(parent_comment, praw.models.Comment):
                    self.process_antibotty_comment(parent_comment)
    
    def process_antibotty_comment(self, comment):
        adhominem_label, adhominem_score = self.adhominem_detector(comment.body)
        bias_label, bias_score = self.bias_detector(comment.body)
        sentiment_score = self.sentiment_analyzer(comment.body)
        
        comment.reply(f"Sentiment score: {sentiment_score}, Ad hominem score: {adhominem_score}, Bias score: {bias_score}")

                
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

import logging
from logging.handlers import RotatingFileHandler

# Setup logger
logger = logging.getLogger('')
logger.setLevel(logging.INFO)

# Setup log handler
handler = RotatingFileHandler('moderator.log', maxBytes=1048576, backupCount=5)
handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S'))

# Add handler to logger
logger.addHandler(handler)

def main():
    load_dotenv()  # Load environment variables from .env file

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
    logger.info("Fetched the most recent posts")

    while True:
        time.sleep(10)  # Wait for 10 seconds

        # Get the 100 most recent posts again
        new_most_recent_posts = [post for post in moderator.subreddit.new(limit=100)]
        logger.info("Fetched the most recent posts again")

        # Find the new posts that were not in the old list of most recent posts
        new_posts = [post for post in new_most_recent_posts if post not in most_recent_posts]
        logger.info(f"Found {len(new_posts)} new posts")

        # Process the new posts (moderation actions, etc.)
        for submission in new_posts:
            is_submission_ok, reason = moderator.process_submission(submission)
            if not is_submission_ok:
                submission.mod.remove()  # Remove submission if it does not meet the criteria
                submission.reply(reason)  # Comment the reason for removal
                logger.info(f"Removed submission: {submission.id}, Reason: {reason}")
        
        # Process comments
        moderator.process_comments()
        
        # Update the list of most recent posts
        most_recent_posts = new_most_recent_posts

if __name__ == '__main__':
    main()
