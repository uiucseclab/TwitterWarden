import time
from tqdm import tqdm
from twython import Twython
from credentials import *
import numpy as np
from twython.exceptions import TwythonError
from twython.exceptions import TwythonAuthError
from twython.exceptions import TwythonRateLimitError

# get_timeline(user_id, num_tweets, waiting)
# gets a user's recent timeline from twitter, up to the amount of tweets you specify)
# @arg user_id -- the user id of the user we want to pull tweets for
# @arg num_tweets -- the (minimum) number of tweets you want from the user (only applies if they have tweeted at least that many)
# @arg waiting -- how many seconds to wait in between requests (very important to not hit rate limiting)
# @return their recent timeline
def get_timeline(user_id, num_tweets, waiting):
    twitter = Twython(APP_KEY(), access_token=ACCESS_TOKEN())
    tweets = []
    num_iter = int(num_tweets / 200) + 1
    num_iter = num_iter if num_iter <= 16 else 16
    num_iter = num_iter if num_iter >= 1 else 1

    # We need at least one tweet to start with
    while True:
        try:
            user_timeline = twitter.get_user_timeline(user_id=user_id, count=1)
            break
        except TwythonRateLimitError as e:
            print "TwythonRateLimitError... Waiting for 3 minutes (may take multiple waits)"
            for timer in tqdm(range(3*60)):
                time.sleep(1)
            twitter = Twython(APP_KEY(), access_token=ACCESS_TOKEN())
            time.sleep(waiting)
            continue
        except TwythonAuthError as e:
            print "TwythonAuthError... "
            raise TwythonAuthError("Uhh")
        except TwythonError as e:
            print "TwythonError: " + str(e.error_code) + "..."
            continue
    
    # put that one tweet into our list
    tweets.extend(user_timeline)
    if not user_timeline:
        time.sleep(waiting)
        return tweets
    tid = user_timeline[0]['id']
    
    # get more tweets!
    print "Getting tweets of " + user_id + "..."
    for i in tqdm(range(num_iter)):
        while True:
            try:
                time.sleep(waiting)
                # this works because Twython gives us tweets in reverse chronological order (don't want to repeat, so set a max)
                user_timeline = twitter.get_user_timeline(user_id=user_id, count=200, max_id=tid)
                break
            except TwythonRateLimitError as e:
                print "TwythonRateLimitError... Waiting for 3 minutes (may take multiple waits)"
                for timer in tqdm(range(3*60)):
                    time.sleep(1)
                twitter = Twython(APP_KEY(), access_token=ACCESS_TOKEN())
                continue
            except TwythonAuthError as e:
                print "TwythonAuthError... "
                raise TwythonAuthError("Uhh")
            except TwythonError as e:
                print "TwythonError: " + str(e.error_code) + "..."
                continue

        # if twitter gave us no tweets, there's no more to get
        if not user_timeline:
            break

        # otherwise save them and keep track of which one's the oldest (and set one below it to be the max we'll allow)
        tweets.extend(user_timeline)
        tid = user_timeline[-1]['id'] - 1
    
    print "Found " + str(len(tweets)) + " tweets total"
    return tweets

# get_users_around(center, num_friends, num_followers, waiting)
# gets a group of people in the network around the center user
# @arg center -- the central user of the network we intend to build
# @arg num_friends -- maximum number of friends to return
# @arg num_followers -- maximum number of followers to return
# @arg waiting -- how many seconds to wait in between requests (very important to not hit rate limiting)
# @return people who retweeted some tweet within user_timeline, by numerical id
def get_users_around(center, num_friends, num_followers, waiting):
    twitter = Twython(APP_KEY(), access_token=ACCESS_TOKEN())
    following = dict()
    following = dict()

    # get friends and followers around a central user
    print "Getting users..."
    while True:
        try:
            following = twitter.get_friends_ids(screen_name=center, count=5000)
            time.sleep(0.1)
            followers = twitter.get_followers_ids(screen_name=center, count=5000)
            break
        except TwythonRateLimitError as e:
            print "TwythonRateLimitError... Waiting for 3 minutes (may take multiple waits)"
            for timer in tqdm(range(3*60)):
                time.sleep(1)
            twitter = Twython(APP_KEY(), access_token=ACCESS_TOKEN())
            time.sleep(waiting)
            continue
        except TwythonAuthError as e:
            print "TwythonAuthError... "
            raise TwythonAuthError("Uhhh")
        except TwythonError as e:
            print "TwythonError: " + str(e.error_code) + "..."
            time.sleep(waiting)
            continue

    # choose out random friends and followers from the previous list
    if len(following['ids']) > 0:
        following = map(lambda x: str(x), np.random.choice(following['ids'], min(int(num_friends), len(following['ids'])), replace=False))
        following = get_users(following, waiting, True)
    else:
        following = []
    if len(followers['ids']) > 0:
        followers = map(lambda x: str(x), np.random.choice(followers['ids'], min(int(num_followers), len(followers['ids'])), replace=False))
        followers = get_users(followers, waiting, True)
    else:
        followers = []

    return (following, followers)

# get_users(users, waiting)
# gets the fully-hydrated users for every numerical id (in string form) in user_ids
# @arg user_ids -- a set of stringified numerical ids for our users
# @arg waiting -- how many seconds to wait in between requests (very important to not hit rate limiting)
# @return usernames for these users
def get_users(user_ids, waiting, allowProtected):
    twitter = Twython(APP_KEY(), access_token=ACCESS_TOKEN())
    users_out = []

    print "Finding screen names of users..."
    for i in tqdm(range((len(user_ids) - 1) / 100 + 1)):
        while True:
            try:
                time.sleep(waiting)
                # look up up to 100 users in one request (don't hit that rate limit!)
                looking_up = ",".join(user_ids[i * 100 : min((i+1) * 100, len(user_ids))])
                result = twitter.lookup_user(user_id=looking_up)
                break
            except TwythonRateLimitError as e:
                print "TwythonRateLimitError... Waiting for 3 minutes (may take multiple waits)"
                for timer in tqdm(range(15*60)):
                    time.sleep(1)
                twitter = Twython(APP_KEY(), access_token=ACCESS_TOKEN())
                continue
            except TwythonAuthError as e:
                print "TwythonAuthError... "
                time.sleep(waiting)
                continue
            except TwythonError as e:
                print "TwythonError: " + str(e.error_code) + "..."
                continue

        if allowProtected:
            users_out.extend(result)
        else:
            users_out.extend([x for x in result if not x['protected']])

    return users_out