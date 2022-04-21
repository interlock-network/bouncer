"""Main entry point for the Linkbot."""

import configparser
import logging
import discord
import re

# Set the logging up
logging.basicConfig(level=logging.INFO)

# Parse the configuration.ini file in the repository root
configuration = configparser.ConfigParser()
configuration.read('configuration.ini')

# Get needed values from the configuration.ini file
token = configuration.get('discord', 'token')

# Create a discord client
client = discord.Client()


@client.event
async def on_ready():
    """Invoke when the bot has connected to Discord."""
    print(f'{client.user} has connected to Discord!')


def url(str):
    """Find and return all URLs in a string."""
    urlRegex = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|\
    [!*, ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', str)
    return urlRegex


@client.event
async def on_message(message):
    """Invoke when a message is received on the Guild/server."""
    print(url(message.content))


if __name__ == '__main__':
    client.run(token)
