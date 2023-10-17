from os import getenv
import not_tweepy as tweepy
import spacy
from .models import DB, Tweet, User

# Get our API keys form our .env file
key = getenv('TWITTER_API_KEY')
secret = getenv('TWITTER_API_KEY_SECRET')

# connect to twitter API
TWITTER_AUTH = tweepy.OAuthHandler(key, secret)
TWITTER = tweepy.API(TWITTER_AUTH)


def add_or_update_user(username):
    try:
        # get the user information from twitter
        twitter_user = TWITTER.get_user(screen_name=username)

        # Check to see if this user is already in the database
        # Is there a user with the same ID already in the database
        # If we don't already have that user, then we'll create a new one
        db_user = (User.query.get(twitter_user.id)) or User(id=twitter_user.id,
                                                            username=username)

        # imaginary if statement
        # if (age > 20) or (height > 60):
            # get into the if block if either condition is true

        # add the user to the database
        # this won't re-add a user if they've already been added
        DB.session.add(db_user)

        # get the user's tweets (in a list)
        tweets = twitter_user.timeline(count=200,
                                       exclude_replies=True,
                                       include_rts=False,
                                       tweet_mode='extended',
                                       since_id=db_user.newest_tweet_id)

        # update the newest_tweet_id if there have been new tweets
        #since the last time this user tweeted
        if tweets:
            db_user.newest_tweet_id = tweets[0].id
        # all all of the individual tweets to the database

        for tweet in tweets:
            tweet_vector = vectorize_tweet(tweet.full_text)
            db_tweet = Tweet(id=tweet.id,
                             text=tweet.full_text[:300],
                             vect=tweet_vector,
                             user_id=db_user.id)
            db_user.tweets.append(db_tweet)
            DB.session.add(db_tweet)
    except Exception as e:
        print(f"Error processing {username}: {e}")
        raise e

    else: 
        # Save the changes to the DB
        DB.session.commit()


nlp = spacy.load('my_model/')
# We have the same tool we used in the flask shell


# give the function some text, it returns a word embedding
def vectorize_tweet(tweet_text):
    return nlp(tweet_text).vector
