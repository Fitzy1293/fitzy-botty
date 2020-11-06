#!/bin/env python3

import discord
import praw
import asyncio
import random
import os
import time
from pprint import pprint
import authenticate
from traceback import format_exc
from discord.ext import commands

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
                '-commands',
                '-pka-search "query"'
                )
    return commands

def validCommand(received, commands): # Discord message arg parser
    if len(received) >= 1:
        if received[0] == '-': # Check if it starts with command trigger
            commandTriggers = [i.split()[0] for i in commands]
            commandNoArgs = received.split()[0]
            if not commandNoArgs in commandTriggers:
                return False
            else:
                return True
        else:
            return False


async def update(start, log, programStart): # Needs to be async
    makelogs.createLogs(start, log)
    makelogs.logCatchUp(programStart)

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

    if str(username) != 'botty#1436' and validCommand(received, commands): # Syntacitcally correct command.
        commandLog = f'Command entered: {received}\n{username}'
        log.append(commandLog)
    else:
        return

    #Tells discord user list of bot's commands.
    if received == '-commands':
        await message.channel.send(f'A list of commands to try!\nCommands:\n' + '\n'.join(commands))

    #Links the current front page post in a particular subreddit.
    elif received.startswith('-top'):
        for i in topLinks(received):
            log.append(i)
            if 'https://' in i:
                await message.channel.send(str('─' * 125))
            await message.channel.send(i)

    #Random copypasta.
    elif received == '-copypasta':
        discordReceive = returnPasta()
        await message.channel.send(discordReceive)

    #Sends random image from a subreddit.
    elif received.startswith('-randpic'):
        picExtensions = ('.png', '.PNG', '.jpg', '.JPG',)
        randomPicReturn = randomPic(received, picExtensions)

        if randomPicReturn.endswith((picExtensions)):
            log.append(f'\t{randomPicReturn}')
            file = discord.File(randomPicReturn)
            await message.channel.send(file=file)
            os.remove(randomPicReturn)

        else:
            await message.channel.send(randomPicReturn)

    elif received.startswith('-pka-search'):
        grepOutput = pkaSearch(received)
        for i in grepOutput:
            log.append(i)
            await message.channel.send(i)

    await update(start, log, programStart)


print(f'Awaiting on botty...')
print('For the formatted continuous log run $ ./runlog.py')
client.run(token)
print('Bot ended')
