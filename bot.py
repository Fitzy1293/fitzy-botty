#!/bin/env python3

import discord
import praw
import random
import os
import urllib.request as req
import time
from pprint import pprint
import authenticate
from traceback import format_exc

#=========================================================================================================================================================================================================================
#=========================================================================================================================================================================================================================
#=========================================================================================================================================================================================================================
#=========================================================================================================================================================================================================================
client = discord.Client() #Discord client.
token = authenticate.disToken() #Discord token, in a module for discord and reddit OAUTH stuff.
reddit = authenticate.redditAuthenticate() #Reddit API authentification with PRAW.
programStart = time.time()

def initLogs(logNames = []):
    for fname in logNames:
        with open(fname, 'w+') as f: # Make sure logs are there and empty on startup.
            pass

def getCommands():
    commands = [
                '-top "subreddit"',
                '-copypasta',
                '-randpic "subreddit"',
                '-commands'
                ]

    return [f'\t{i}' for i in commands]

def validCommand(received, commands): # Discord message arg parser
    if len(received) >= 1:
        if received[0] == '-':
            commandTriggers = [i.split()[0] for i in commands]
            commandNoArgs = received.split()[0]
            if not commandNoArgs in commandTriggers:
                return False
            else:
                return True
        else:
            return False


# With async messages come in before the old ones are finished meaning -
    # Cannot simply chronologically writes messages and runtime for each receive and send
        # You will get a bunch of messages received then a bunch of runtimes
    # Using a second log file that logs the UTC timestamp with the runtime
    # Count received messages in "log" and compare that count to the number of finished jobs that are logged in time_log
    # Completed.txt has an up to date list of completed jobs

def createLogs(start, fail, reportFlag, log):
    if fail:
        log.append('\tfailure')
    else:
        log.append('\tsuccess')

    if reportFlag:
        runTime = round(time.time() - start, 2)
        logTime = f'\t{runTime} seconds'

        with open('time_log', 'a+') as f:
            f.write(f'{start}={logTime.strip()}\n')

    with open('log', 'a+') as f:
        for line in log:
            f.write(line + '\n')
        f.write('END' + '\n')


def logCatchUp(): # If requests come in before the current one is finished, the runtime is logged after the message
    timeData = open('time_log', 'r').read().splitlines()
    currentLog = [i for i in open('log', 'r').read().splitlines() if i != '\n']
    commandCt = [i.split()[0] for i in currentLog if i.startswith('Command')].count('Command') # Counts how many valid messages it received in a session
    if len(timeData) != commandCt:
        print('Catching up')
        return False
    elif len(timeData) == commandCt and commandCt != 0:
        print('Writing to completed.txt')
        messageCt = 0
        revisedLog = []
        for i in currentLog:
            if i != 'END':
                if i.startswith('Command'):
                    revisedLog.append(f'{i} ({messageCt})\n')
                else:
                    revisedLog.append(f'{i}\n')
            else:
                utcAndRunTime = timeData[messageCt].replace('=', '\n\t')
                revisedLog.append(f'\t{utcAndRunTime}\n' )
                messageCt += 1


        revisedLog[-1] = revisedLog[-1].rstrip('\n')

        with open('completed.txt', 'w+') as f: #
            for i in revisedLog:
                f.write(i)
            f.write(f'\n\nmessages = {commandCt}')
            uptime = round(time.time() - programStart)
            f.write(f'\nuptime = {uptime} seconds')

#=========================================================================================================================================================================================================================
#=========================================================================================================================================================================================================================
#=========================================================================================================================================================================================================================
#=========================================================================================================================================================================================================================

@client.event
async def on_ready():
    print(f'...{client.user.name} is ready!\n')

@client.event
async def on_resumed():
    pass

@client.event
async def on_message(message):
    start = time.time()
    username = message.author
    received = message.content
    commands =getCommands()
    log = []
    fail = False

    if str(username) != 'botty#1436' and validCommand(received, commands):
        commandLog = f'Command entered: {username}\n{received}'
        log.append(commandLog)
        reportFlag = True
    else:
        return

    #Tells discord user list of bot's commands.
    if received == '-commands':
        await message.channel.send('A list of commands to try!')
        await message.channel.send(f'Commands:\n' + '\n'.join(commands))

    #Links the current front page post in a particular subreddit.
    if message.content.startswith('-top'):
        if ' ' in  received:
            splitReceived = received.split(' ')
            discordSubreddit = splitReceived[1]
            if len(splitReceived) == 3:
                numOfPosts = int(splitReceived[2])
            else:
                numOfPosts = 1

            try:
                subreddit = reddit.subreddit(discordSubreddit)
                stickyCt = len([True for submission in subreddit.hot(limit=2) if submission.stickied]) #Sticky check

                for submission in subreddit.hot(limit=numOfPosts + stickyCt):
                    if not submission.stickied:
                        link = f'\thttps://www.reddit.com{submission.permalink}'
                        log.append(link)
                        await message.channel.send(f'{submission.title}\n{link}')

            except Exception as e:
                print(format_exc())
                await message.channel.send('This sub is either banned, quarantined, or does not exist.')
                fail = True

    #Mark says a random copypasta.
    if message.content.lower() == '-copypasta':
        subreddit = reddit.subreddit('copypasta')

        copyPastas = []
        for submission in subreddit.hot(limit=200):
            try:
                copyPastas.append(submission.selftext)
            except:
                continue

        #Loop for when the post is too long to send to the discord channel.
        while True:
            try:
                discordReceive = copyPastas[random.randint(0, len(copyPastas) - 1)]
                await message.channel.send(discordReceive)
                break
            except Exception as e:
                print(format_exc())
                continue

    #Sends random image from a subreddit.
    if message.content.startswith('-randpic'):
        if ' ' in  message.content:
            picExtensions = ('.png', '.PNG', '.jpg', '.JPG',)
            discordSubreddit = message.content.split(' ')[1]

            try:
                subreddit = reddit.subreddit(discordSubreddit)
                imageUrls = [i.url for i in subreddit.hot(limit=100) if i.url.endswith(picExtensions)]

                discordReceive = imageUrls[random.randint(0,len(imageUrls) - 1)]

                req.urlretrieve(discordReceive, 'tempDiscord.jpg')
                fullPath = os.path.join(os.getcwd(), 'tempDiscord.jpg')
                file = discord.File(fullPath)
                await message.channel.send(file=file)

                os.remove('tempDiscord.jpg')

            except Exception as e:
                print(format_exc())
                await message.channel.send('This sub is either banned, quarantined, or does not exist.')
                fail = True

    createLogs(start, fail, reportFlag, log)
    logCatchUp()


if __name__ == "__main__":
    programStart = time.time()
    initLogs(('log', 'time_log', 'completed.txt'))

    print(f'Awaiting on botty...')
    print('Continuous log => $ ./runlog.py')
    client.run(token)
    print('Bot ended')
