
import praw
from authenticate import redditAuthenticate
from traceback import format_exc
from pprint import pprint
import random
import urllib.request as req
import os
import subprocess
from subprocess import check_output


reddit = redditAuthenticate() #Reddit API authentification with PRAW.

def pkaSearch(received):
    if not ' ' in  received:
        return

    query = received.split(' ')[1]

    episodes = open('PKA_timelines.txt', 'r').read().split('\n\n')

    loggedEp = False
    results = []
    for i in episodes:
        lines = i.split('\n\t')
        matches = []
        for j in lines:
            if query in j:
                matches.append(j)

        results.append([lines[0], matches])

    returnAsStr = []
    for i in results:
        if len(i[1]) != 0:
            returnAsStr.extend((i[0], '\t' + '\n\t'.join(i[1])))

    send = '\n'.join(returnAsStr)

    if len(send) < 2000:
        print(len(send))

    else:
        messagesCt = len(send) // 2000
        if messagesCt == 0:
            yield(send)
        else:
            for i in range(messagesCt):
                endSlice = (i+1) * 2000

                yield(send[i * 2000 : endSlice])

            yield(send[endSlice:])


def topLinks(received):
    if not ' ' in  received:
        return

    splitReceived = received.split(' ')
    discordSubreddit = splitReceived[1]
    if len(splitReceived) == 3:
        numOfPosts = int(splitReceived[2])
    else:
        numOfPosts = 1

    try:
        returnCt = 0
        subreddit = reddit.subreddit(discordSubreddit)
        stickyCt = len([True for submission in subreddit.hot(limit=2) if submission.stickied]) #Sticky check
        for i , submission in enumerate(subreddit.hot(limit=numOfPosts + stickyCt)):
            try:
                if i >= stickyCt:
                    titleStr = f'\ttitle:\t{submission.title}'
                    linkStr = f'\tlink:\thttps://www.reddit.com{submission.permalink}'
                    yield ('\n'.join( (f'({returnCt}) - sucess', titleStr, linkStr) ))
                    returnCt += 1

            except Exception as e:
                print(format_exc())

    except Exception as e:
        print(format_exc())
        discordError = 'This sub is either banned, quarantined, or does not exist.'
        yield (f'failure\n{discordError}')

def returnPasta():
    subreddit = reddit.subreddit('copypasta')
    copyPastas = []
    for submission in subreddit.hot(limit=200):
        try:
            copyPastas.append(submission.selftext)
        except Exception as e:
            print(format_exc())

    #Loop for when the post is too long to send to the discord channel.
    ct = 0
    while True:
        try:
            pasta = copyPastas[random.randint(0, len(copyPastas) - 1)]
            if not len(pasta) >= 2000:
                return pasta

        except Exception as e:
            print(format_exc())

        ct += 1
        if ct == 20:
            return 'Could\'nt find a pasta'

def randomPic(received, picExtensions):
    if not ' ' in  received:
        return

    discordSubreddit = received.split()[1]

    try:
        subreddit = reddit.subreddit(discordSubreddit)
        imageUrls = [i.url for i in subreddit.hot(limit=100) if i.url.endswith(picExtensions)]

        discordReceive = imageUrls[random.randint(0,len(imageUrls) - 1)]
        fname = discordReceive.split('/')[-1]
        req.urlretrieve(discordReceive, fname)
        fullPath = os.path.join(os.getcwd(), fname)

        return fullPath

    except Exception as e:
        print(format_exc())
        return 'This sub is either banned, quarantined, or does not exist.'
