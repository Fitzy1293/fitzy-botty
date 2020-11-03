
import praw
from authenticate import redditAuthenticate
from traceback import format_exc
from pprint import pprint

utilsreddit = redditAuthenticate() #Reddit API authentification with PRAW.

def topLinks(received):
    if ' ' in  received:
        splitReceived = received.split(' ')
        discordSubreddit = splitReceived[1]
        if len(splitReceived) == 3:
            numOfPosts = int(splitReceived[2])
        else:
            numOfPosts = 1

        try:
            subreddit = utilsreddit.subreddit(discordSubreddit)
            stickyCt = len([True for submission in subreddit.hot(limit=2) if submission.stickied]) #Sticky check
            posts = []
            yield('success')
            for i , submission in enumerate(subreddit.hot(limit=numOfPosts + stickyCt)):

                if i >= stickyCt:
                    titleStr = f'\ttitle:\t{submission.title}'
                    linkStr = f'\tlink:\thttps://www.reddit.com{submission.permalink}'
                    yield (titleStr)
                    yield(linkStr)

        except Exception as e:
            print(format_exc())
            yield ('failure')
            discordError = 'This sub is either banned, quarantined, or does not exist.'
            yield (discordError)
