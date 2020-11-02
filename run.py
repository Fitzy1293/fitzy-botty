#!/bin/env python3

import discord
import praw
import youtube_dl
import random
import os
import urllib.request as req
import time
from pprint import pprint
import authenticate


client = discord.Client() #Discord client.
token = authenticate.disToken() #Discord token, in a module for discord and reddit OAUTH stuff.
reddit = authenticate.redditAuthenticate() #Reddit API authentification with PRAW.

def getCommands():
    commands = [
                '-top "subreddit"',
                '-copypasta',
                '-randpic "subreddit"',
                '-bottest',
                '-commands'
                ]

    return [f'\t{i}' for i in commands]

@client.event
async def on_ready():
    print(f'...{client.user.name} is ready!')
    print()

@client.event
async def on_message(message):
    commandCt =  open('log', 'r').read().splitlines().count('Command entered')
    start = time.time()
    username = message.author
    received = message.content
    commands =getCommands()
    log = []

    if len(fromDiscord) >= 1:
        if fromDiscord[0] == '-':
            commandTriggers = [i.split()[0] for i in commands]
            commandNoArgs = fromDiscord.split()[0]
            if not commandNoArgs in commandTriggers:
                return
            else:
                print('Command entered')
        else:
            return


    if str(username) != 'botty#1436':
        commandLog = f'{commandCt}\n{username}:\n\t{received}'
        print(commandLog)
        log.extend(('Command entered' + '\n', commandLog + '\n'))

        reportFlag = True
    else:
        reportFlag = False

    #Tells discord user list of bot's commands.
    if received == '-commands':
        await message.channel.send('A list of commands to try!')
        await message.channel.send(f'Commands:\n' + '\n'.join(commands))

    #Links the current front page post in a particular subreddit.
    if message.content.startswith('-top'):
        if ' ' in  message.content:
            discordSubreddit = str(message.content).split(' ')[1]

            try:
                subreddit = reddit.subreddit(discordSubreddit)

                for submission in subreddit.hot(limit=5):
                    if not submission.stickied:
                        link = f'https://www.reddit.com{submission.permalink}'
                        send = '\n'.join((submission.title, link))
                        await message.channel.send(send)
                        break

            except Exception as e:
                print(e)
                await message.channel.send('This sub is either banned, quarantined, or does not exist.')

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
            except exception as e:
                pprint(e)
                continue

    #Sends random image from a subreddit.
    if message.content.startswith('-randpic'):
        if ' ' in  message.content:
            picExtensions = ('.png', '.PNG', '.jpg', '.JPG',)
            discordSubreddit = message.content.split(' ')[1]

            try:
                subreddit = reddit.subreddit(discordSubreddit)
                imageUrls = [i.url for i in subreddit.hot(limit=50) if i.url.endswith(picExtensions)]

                discordReceive = imageUrls[random.randint(0,len(imageUrls) - 1)]

                req.urlretrieve(discordReceive, 'tempDiscord.jpg')
                fullPath = os.path.join(os.getcwd(), 'tempDiscord.jpg')
                file = discord.File(fullPath)
                await message.channel.send(file=file)

                os.remove('tempDiscord.jpg')

            except Exception as e:
                print(e)
                await message.channel.send('This sub is either banned, quarantined, or does not exist.')

    if 'youtube.com' in message.content:
        try:
            youtube_dl.YoutubeDL().download([message.content])
        except:
            pass

    if reportFlag:
        runTime = round(time.time() - start, 2)
        logTime = f'\t{runTime} seconds\n'
        print(logTime)
        log.append(logTime)

        with open('log', 'a+') as f:
            for line in log:
                f.write(line)


def main():
    with open('log', 'w+') as f:
        pass

    print(f'Awaiting the bot...')
    client.run(token)
    print('Bot ended.')

if __name__ == "__main__":
    main()
