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

####################################
from bot_tils import *
import makelogs
####################################
#=========================================================================================================================================================================================================================
#=========================================================================================================================================================================================================================
#=========================================================================================================================================================================================================================
#=========================================================================================================================================================================================================================
client = discord.Client() #Discord client.
token = authenticate.disToken() #Discord token, in a module for discord and reddit OAUTH stuff.
reddit = authenticate.redditAuthenticate() #Reddit API authentification with PRAW.
programStart = time.time()
makelogs.initLogs(('log', 'time_log', 'completed.txt'))

def getCommands():
    commands = (
                '-top "subreddit"',
                '-copypasta',
                '-randpic "subreddit"',
                '-commands'
                )

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


def update(start, log, programStart):
    makelogs.createLogs(start, log)
    makelogs.logCatchUp(programStart)
    return 'done'

#=========================================================================================================================================================================================================================
#=========================================================================================================================================================================================================================
#=========================================================================================================================================================================================================================
#=========================================================================================================================================================================================================================


@client.event
async def on_ready():
    print(f'...{client.user.name} is ready!\n')

@client.event
async def on_resumed():
    print('Resumed')
    pass

@client.event
async def on_message(message):
    start = time.time()
    username = message.author
    received = message.content
    commands = getCommands()
    log = []
    stringsToNotSend = ('success', 'failure')

    if str(username) != 'botty#1436' and validCommand(received, commands): # Syntacitcally correct command.
        commandLog = f'Command entered: {received}\n{username}'
        log.append(commandLog)
    else:
        return

    #Tells discord user list of bot's commands.
    if received == '-commands':
        await message.channel.send('A list of commands to try!')
        await message.channel.send(f'Commands:\n' + '\n'.join(commands))

    #Links the current front page post in a particular subreddit.
    if received.startswith('-top'):
        for i in topLinks(received):
            log.append(i)
            if not i in stringsToNotSend:
                await message.channel.send(i)

    #Random copypasta.
    elif received.lower() == '-copypasta':
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
    elif received.startswith('-randpic'):
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


    update(start, log, programStart)
    return



print(f'Awaiting on botty...')
print('For the formatted continuous log run $ ./runlog.py')
client.run(token)
print('Bot ended')
