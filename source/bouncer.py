"""Main entry point for the Interlock-Bouncer."""

import configparser
import gettext
import logging
import discord
import os

from urllib.parse import urlparse
from model import AllowDomain, Message, Channel
from model import find_or_create_channel
from utility import urls_from_str, session
from predicates import (url_http_p, url_malicious_p, allow_url_p,
                        str_contains_url_p)

# Setup gettext for i18n
_ = gettext.gettext

# Parse the configuration.ini file in the repository root
configuration = configparser.ConfigParser()
configuration.read('configuration.ini')

# Max URL length (from issue #28)
max_url_length = configuration.getint('configuration', 'max_url_length')

# Set the logging up
log_file = configuration.get('configuration', 'log_file')
logging.basicConfig(filename=log_file, level=logging.INFO)

# Get the discord token from the  configuration.ini file
token_from_config = configuration.get('discord', 'token')
# Get the discord token from the environment variable
token_from_environment = os.getenv('DISCORD_TOKEN')

# Set the token either by config or environment variable
token = token_from_config or token_from_environment

if (token_from_config and token_from_environment and
   token_from_config != token_from_environment):
    logging.warning("Different Discord token set via configuration.ini file \
AND environment variable! Prioritizing token from configuration.ini.")


# Create a discord client
client = discord.Client()


@client.event
async def on_ready():
    """Invoke when the bot has connected to Discord."""
    print(f'{client.user} has connected to Discord!')
    # Set the bot profile picture
    with open('profile.png', 'rb') as image:
        await client.user.edit(avatar=image.read())


async def process_message(message):
    """Handle a message, deleting or stripping it of links."""
    channel = session.query(Channel).filter_by(
        channel_id=message.channel.id,
        server_id=message.guild.id).first()
    if channel.block_links_p and str_contains_url_p(message.content):
        await message.reply(content=_("Mods have set this channel to have no links from users."))
        await message.delete()
        return

    for url in urls_from_str(message.content):
        url_object = urlparse(url)
        if (allow_url_p(session, url_object, message.guild)):
            logging.info("URL ignored: %s", url)
            await message.reply(
                content=_("URL `{0}` marked safe by server moderator.")
                .format(url))
            break
        elif (len(url) > max_url_length):
            await message.reply(
                content=_("Caution: message contains URLs which cannot be scanned! \n\
**{0}:** `{1}`").format(message.author.name, message.content))
            await message.delete()
            break
        elif (not url_http_p(url)):
            await message.reply(
                content=_("Caution: message contains URLs which cannot be scanned! \n\
**{0}:** `{1}`").format(message.author.name, message.content))
            await message.delete()
            break
        elif (url_malicious_p(url)):
            await message.reply(
                content=_("Caution: message may contain dangerous links! \n\
**{0}:** `{1}`").format(message.author.name, message.content))
            await message.delete()
            logging.info("URL marked as insecure: %s. Message: %s",
                         url, message.content)
            session.add(Message(str(message.author.id), message.content, True))
            session.commit()
            break
        # If we have made it to this point, URL is OK
        logging.info("URL marked as secure: %s", url)


async def process_message_command(message):
    """Handle a command delivered as a message.

    Return True if the message is a command.
    """
    if (message.content.lower().startswith('!allow_domains')):
        urls = urls_from_str(message.content)
        for url in urls:
            url_object = urlparse(url)
            session.add(AllowDomain(url_object.hostname,
                                    str(message.guild.id)))
        session.commit()
        await message.channel.send(_("URLs `{}` added to allow list.")
                                   .format(urls))
        return True
    elif (message.content.lower().startswith('!unallow_domains')):
        urls = urls_from_str(message.content)
        for url in urls:
            url_object = urlparse(url)
            session.query(AllowDomain).filter_by(
                hostname=url_object.hostname,
                server_id=message.guild.id).delete()
        session.commit()
        await message.channel.send(_("URLs `{}` removed from allow list.")
                                   .format(urls))
        return True
    elif (message.content.lower().startswith('!block_links')):
        channel = find_or_create_channel(message.channel.id, message.guild.id)
        channel.block_links_p = True
        session.commit()
        await message.channel.send("URLs now blocked on this channel.")
        return True
    elif (message.content.lower().startswith('!unblock_links')):
        channel = find_or_create_channel(message.channel.id, message.guild.id)
        channel.block_links_p = False
        session.commit()
        await message.channel.send("URLs now allowed on this channel.")
        return True
    else:
        return False


@client.event
async def on_message(message):
    """Invoke when a message is received on the Guild/server."""
    if message.author.bot:
        return
    if (not await process_message_command(message)):
        await process_message(message)


@client.event
async def on_message_edit(message_before, message_after):
    """Invoke when a message is edited on the Guild/server."""
    if message_before.author.bot or message_after.author.bot:
        return
    await process_message(message_after)

if __name__ == '__main__':
    client.run(token)
