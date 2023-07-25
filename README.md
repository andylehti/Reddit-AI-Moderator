# Reddit AI Moderator: Su breddit, Re ddit, Mod erator = suremod.py

This project contains a Reddit bot built with the PRAW (Python Reddit API Wrapper) library that monitors a specified subreddit for new posts and comments, and comments below them with bias and sentiment scores.

### Installation

1. Run the install script:

    ```
    curl -O https://raw.githubusercontent.com/andylehti/Reddit-AI-Moderator/main/configure.sh -O https://raw.githubusercontent.com/andylehti/Reddit-AI-Moderator/main/install.sh && chmod +x configure.sh && chmod +x install.sh
    ./install.sh
    ```

2. Run the configuration script:

    ```
    ./configure.sh
    ```

### Configuration

The `configure.sh` script will prompt you for the following:

- Your Reddit API credentials (Client ID, Client Secret, User Agent, Username, Password)
- The subreddit you want the bot to monitor
- Whether you want the bot to comment the bias and sentiment score for every post
- Whether you want the bot to comment the bias and sentiment score for every comment

These settings will be saved in a `credentials.json` file and in a `suremod.py` script that will be created by the `configure.sh` script.

### Extending Functionality

To extend the functionality of the bot, you can add additional functions to the `SubredditModerator` class in the `suremod.py` script. These functions will have access to the `reddit` and `subreddit` instances created in the script, allowing them to interact with Reddit's API. Ensure that you call your new function properly within the existing structure.

For example, to add a function that replies to any comment containing the word "hello":

```python
def reply_to_hello(self):
  for comment in self.subreddit.stream.comments():
    if "hello" in comment.body.lower():
      comment.reply("Hello, user!")
```

Add a call to this function in the `start_moderating` function:

```python
def start_moderating(self):
  # Existing code...
  self.reply_to_hello()
```

### Function Overview

- `SubredditModerator` is the main class that handles all the moderating functionalities.
    - `__init__(self, subreddit, score_posts, score_comments)`: This is the constructor method which initializes the SubredditModerator object. You can pass the subreddit name, and booleans to indicate whether you want the bot to score posts and comments.
    - `start_moderating(self)`: This method starts the moderation process. It sets up PRAW's stream to continuously fetch new posts and comments from the subreddit, and calls the relevant processing methods on them.
    - `process_post(self, post)`: This method is called for each new post in the subreddit. It computes the bias and sentiment score for the post and, depending on the `score_posts` setting, may comment on the post with the scores.
    - `process_comment(self, comment)`: Similar to `process_post`, but for comments.
    - Additional functions can be added here. Be sure to call them in `start_moderating`.

### About

This bot was built with a focus on extendability. The `SubredditModerator` class can be easily extended with new functions, allowing the bot to perform any action available through Reddit's API. 
Feel free to modify and adapt the bot to suit your own needs.
