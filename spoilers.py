import praw
import pdb
import string
import os
# from pattern.en import conjugate

# spoiler parameters read from file 
def parse(path):
    spoilers = open(path, "r")
    words = spoilers.read().splitlines()
    nouns = True

    for word in words:
        if word[0:2] == "<>":
            nouns = False
        else:
            if nouns == True:
                things.append(word)
            else:
                happenings.append(word)

# load spoiler parameters
parse("spoilers.txt")

# explaining api accesses to reddit
reddit = praw.Reddit(user_agent = "Warning myself about potential GOTS spoilers in comment threads")
# log in main reddit acount
reddit.login(os.environ.get("MAIN_REDDIT_ACCOUNT"), os.environ.get("MAIN_REDDIT_PASSWORD"))

# subreddits I subscribe to
subscribed = list(reddit.get_my_subreddits())

# downvoted submissions to be upvoted by alternate account
downvoted = [] 
things = []
happenings = []

# used for removing punctuation ex: George R. R. Martin -> georgerrmartin
table = string.maketrans("","")

for subreddit in subscribed:
    posts = subreddit.get_hot(limit = 10)

    for post in posts:

        # top level comments
        comments = post.comments[0:20]
        flat_comments = praw.helpers.flatten_tree(comments)

        for comment in flat_comments:

            # skip collapsed comments
            if comment.__class__.__name__ == "MoreComments":
                continue

            # spoiler notification
            warn = False

            # skip symbols that are not recognized
            try:
                comment.body.encode("ascii")
            except UnicodeEncodeError:
                continue

            # remove symbols, spaces, punctuation, capitalization
            condensed = comment.body.encode("ascii").translate(table, string.punctuation).replace(" ","").lower()

            # Potential spoiler detected
            if any(word in condensed for word in things):
                if any(word in condensed for word in happenings):
                    warn = True

            if warn == True:
                # downvote submission, add to downvoted list
                comment.submission.downvote()
                downvoted.append(comment.submission)

# log out main account
reddit.logout()

# log in alternate account to upvote wrongly downvoted posts
reddit2 = praw.Reddit(user_agent = "Neutralizes effects of downvoting links with potential spoilers in the comments as this is not a valid reason to downvote content.")
reddit2.login(os.environ.get("ALTERNATE_REDDIT_ACCOUNT"), os.environ.get("ALTERNATE_REDDIT_PASSWORD"))


for post in downvoted:
    post.upvote()

reddit2.logout()



