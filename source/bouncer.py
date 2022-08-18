"""Main entry point for the Interlock-Bouncer."""

import gettext
import logging

from urllib.parse import urlparse
from model import AllowDomain, Message, Channel
from model import find_or_create_channel
from utility import urls_from_str, session, client, token, configuration
from predicates import (url_http_p, url_malicious_p, allow_url_p,
                        str_contains_url_p)
from discord_logger import DiscordLogger

# Setup gettext for i18n
_ = gettext.gettext

# Max URL length
max_url_length = configuration.getint('configuration', 'max_url_length')

# Set the logging up
log_file = configuration.get('configuration', 'log_file')
logging.basicConfig(filename=log_file, level=logging.INFO)

discord_logger = DiscordLogger()
discord_logger.setLevel(logging.DEBUG)

friendly_discord_logger = DiscordLogger(channel="bouncer-admin-log")
friendly_discord_logger.setLevel(logging.INFO)

logger = logging.getLogger()
logger.addHandler(discord_logger)
logger.addHandler(friendly_discord_logger)


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
    if channel and channel.block_links_p and str_contains_url_p(message.content):
        logging.info("User `%s` posted message `%s` in nolink channel `%s`.",
                     message.author.name,
                     message.content,
                     message.channel.name)
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
            logging.info("Ignoring URL %s because it is not HTTP/s", url)
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
        logging.info("URLS disabled for channel `%s` by `%s`.",
                     message.channel.name,
                     message.author.name)
        return True
    elif (message.content.lower().startswith('!unblock_links')):
        channel = find_or_create_channel(message.channel.id, message.guild.id)
        channel.block_links_p = False
        session.commit()
        await message.channel.send("URLs now allowed on this channel.")
        logging.info("URLS enabled for channel `%s` by `%s`.",
                     message.channel.name,
                     message.author.name)
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
