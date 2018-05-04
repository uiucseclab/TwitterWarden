import numpy as np
import snowflake
from collections import defaultdict

def char_range(c1, c2):
    """Generates the characters from `c1` to `c2`, inclusive."""
    for c in xrange(ord(c1), ord(c2)+1):
        yield chr(c)

def getScreenNameLength(user):
    return len(user['screen_name'])

def getScreenNameDigits(user):
    return len([x for x in user['screen_name'] if x in char_range('0','9')])

def getUserNameLength(user):
    return len(user['name'])

# Will be deprecated May 23, 2018, due to GDPR
def getTimeOffset(user):
    ret = user['utc_offset']
    return ret if ret else 0

def getDefaultProfile(user):
    return user['default_profile']

def getDefaultImage(user):
    return user['default_profile_image']

def getAccountAge(user):
    return (snowflake.utcnow() - snowflake.str2utc(user['created_at'])) / (60.0 * 60.0 * 24.0)

def getProfileDescLen(user):
    return len(user['description'])

def getNumFriends(user):
    return user['friends_count']

def getNumFollowers(user):
    return user['followers_count']

def getNumFavs(user):
    return user['favourites_count']

def getNumStatusesTotal(user):
    return user['statuses_count']

def getRateStatuses(user):
    return (getNumStatusesTotal(user) * 24.0) / getAccountAge(user)

def getProportionRetweets(user, tweets):
    if len(tweets) > 0:
        totalNum = len(tweets)
        totalRetweets = len([x for x in tweets if x['retweeted']])
        return totalRetweets / float(totalNum)
    else:
        return 0.0

def getProportionReplies(user, tweets):
    if len(tweets) > 0:
        totalNum = len(tweets)
        totalRetweets = len([x for x in tweets if x['in_reply_to_status_id']])
        return totalRetweets / float(totalNum)
    else:
        return 0.0

# Main Helper
def getStats(data):
    if len(data) == 0:
        return [0, 0, 0, 0, 0]
    data = np.array(data)
    hi = max(data)
    lo = min(data)
    mean = np.mean(data)
    med = np.median(data)
    std = np.std(data)
    return [hi, lo, mean, med, std]

# Secondary Helper
def getTweetStats(tweets, statsType):
    return getStats([x[statsType] for x in tweets if statsType in x])

# Secondary Helper
def getTimingStats(tweets):
    return getStats([snowflake.str2utc(x['created_at']) - snowflake.str2utc(y['created_at']) for x,y in zip(tweets[:-1],tweets[1:])])

# Actual Data
def getRetweetedStats(tweets):
    return getTweetStats(tweets, 'retweet_count')

def getRepliedStats(tweets):
    return getTweetStats(tweets, 'reply_count')

def getFavoritedStats(tweets):
    return getTweetStats(tweets, 'favorite_count')

def getRetweetTimingStats(tweets):
    return getTimingStats([x for x in tweets if x['retweeted']])

def getReplyTimingStats(tweets):
    return getTimingStats([x for x in tweets if x['in_reply_to_status_id']])

def getOCTimingStats(tweets):
    return getTimingStats([x for x in tweets if not x['in_reply_to_status_id'] and not x['retweeted']])

def getNumLanguages(users):
    return len({x['lang'] for x in users})

def getLanguageEntropy(users):
    langs = defaultdict(int)
    
    for x in users:
        langs[x['lang']] += 1
    
    total = len(users)
    
    entropy = 0
    for lang, count in langs.iteritems():
        entropy += (count / float(total)) * np.log2(count / float(total))
    entropy *= -1

    return entropy

def getAccountAgeStats(users):
    return getStats([getAccountAge(x) for x in users])

# Will be deprecated May 23, 2018, due to GDPR
def getTimeOffsetStats(users):
    return getStats([getTimeOffset(x) for x in users])

def getNumFriendStats(users):
    return getStats([getNumFriends(x) for x in users])

def getNumFollowerStats(users):
    return getStats([getNumFollowers(x) for x in users])

def getNumTweetStats(users):
    return getStats([getNumStatusesTotal(x) for x in users])

def getProfileDescriptionStats(users):
    return getStats([getProfileDescLen(x) for x in users])

def getProportionDefaults(users):
    if len(users) > 0:
        return len([x for x in users if getDefaultProfile(x)]) / float(len(users))
    else:
        return 0.0

def getTweetEntropyStats(ngram, tweets):
    return getStats([ngram.entropy(x['text']) for x in tweets])

def getTweetLengthStats(tweets):
    return getStats([len(x['text'].split(" ")) for x in tweets])

def getAllFeatures(user, tweets, friends, followers):
    features = []
    features.append(getScreenNameLength(user))
    features.append(getScreenNameDigits(user))
    features.append(getUserNameLength(user))
    features.append(getTimeOffset(user))
    features.append(getDefaultProfile(user))
    features.append(getDefaultImage(user))
    features.append(getAccountAge(user))
    features.append(getProfileDescLen(user))
    features.append(getNumFriends(user))
    features.append(getNumFollowers(user))
    features.append(getNumFavs(user))
    features.append(getNumStatusesTotal(user))
    features.append(getRateStatuses(user))
    features.append(getProportionRetweets(user, tweets))
    features.append(getProportionReplies(user, tweets))
    features.extend(getRetweetedStats(tweets))
    features.extend(getRepliedStats(tweets))
    features.extend(getFavoritedStats(tweets))
    features.extend(getRetweetTimingStats(tweets))
    features.extend(getReplyTimingStats(tweets))
    features.extend(getOCTimingStats(tweets))
    features.append(getNumLanguages(followers))
    features.append(getNumLanguages(friends))
    features.append(getLanguageEntropy(followers))
    features.append(getLanguageEntropy(friends))
    features.extend(getAccountAgeStats(followers))
    features.extend(getAccountAgeStats(friends))
    features.extend(getTimeOffsetStats(followers))
    features.extend(getTimeOffsetStats(friends))
    features.extend(getNumFriendStats(followers))
    features.extend(getNumFriendStats(friends))
    features.extend(getNumFollowerStats(followers))
    features.extend(getNumFollowerStats(friends))
    features.extend(getNumTweetStats(followers))
    features.extend(getNumTweetStats(friends))
    features.extend(getProfileDescriptionStats(followers))
    features.extend(getProfileDescriptionStats(friends))
    features.append(getProportionDefaults(followers))
    features.append(getProportionDefaults(friends))
    features.extend(getTweetLengthStats(tweets))
    return features
