"""Main entry point for the Interlock-Bouncer."""

import gettext
import logging

from urllib.parse import urlparse
from model import AllowDomain, Message, Channel
from model import find_or_create_channel
from utility import urls_from_str, session, bot, token, configuration, MESSAGE
from predicates import (url_http_p, url_malicious_p, allow_url_p,
                        str_contains_url_p)
from discord_logger import DiscordLogger

# Setup gettext for i18n
_ = gettext.gettext

# Max URL length
max_url_length = configuration.getint('configuration', 'max_url_length')

# Set the logging up
logging.basicConfig(filename=configuration.get('configuration', 'log_file'),
                    level=logging.DEBUG)
logger = logging.getLogger()

discord_logger = DiscordLogger()
logger.addHandler(discord_logger)


@bot.event
async def on_ready():
    """Invoke when the bot has connected to Discord."""
    print(f'{bot.user} has connected to Discord!')
    # Set the bot profile picture
    with open('docs/profile.png', 'rb') as image:
        await bot.user.edit(avatar=image.read())


async def process_message(message):
    """Handle a message, deleting or stripping it of links."""
    channel = session.query(Channel).filter_by(
        channel_id=message.channel.id,
        server_id=message.guild.id).first()
    if channel and channel.block_links_p and str_contains_url_p(message.content):
        logger.log(MESSAGE, "User `%s` posted message `%s` in nolink channel `%s`.",
                   message.author.name,
                   message.content,
                   message.channel.name,
                   extra={'server': message.guild})
        await message.reply(content=_("Mods have set this channel to have no links from users."))
        await message.delete()
        return

    for url in urls_from_str(message.content):
        url_object = urlparse(url)
        if (allow_url_p(session, url_object, message.guild)):
            logger.log(MESSAGE, "URL ignored: %s", url, extra={'server': message.guild})
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
            logger.log(MESSAGE, "Ignoring URL %s because it is not HTTP/s", url, extra={'server': message.guild})
            break
        elif (url_malicious_p(url)):
            await message.reply(
                content=_("Caution: message may contain dangerous links! \n\
**{0}:** `{1}`").format(message.author.name, message.content))
            await message.delete()
            logger.log(MESSAGE, "URL marked as insecure: %s. Message: %s",
                       url, message.content,
                       extra={'server': message.guild})
            session.add(Message(str(message.author.id), message.content, True))
            session.commit()
            break
        # If we have made it to this point, URL is OK
        logger.log(MESSAGE, "URL marked as secure: %s", url, extra={'server': message.guild})


@bot.slash_command()
async def unallow_domain(ctx, url):
    """Block a domain in a given channel."""
    url_object = urlparse(url)
    session.query(AllowDomain).filter_by(
        hostname=url_object.hostname,
        server_id=ctx.guild.id).delete()
    session.commit()
    logger.log(MESSAGE, "URL `%s` removed from allow list.", url, extra={'server': ctx.guild})
    await ctx.respond(_("URL `{}` removed from allow list.").format(url))


@bot.slash_command()
async def allow_domain(ctx, url):
    """Allow a domain in a given channel."""
    url_object = urlparse(url)
    session.add(AllowDomain(url_object.hostname, str(ctx.guild.id)))
    session.commit()
    logger.log(MESSAGE, "URL `%s` added to allow list.", url, extra={'server': ctx.guild})
    await ctx.respond(_("URL `{}` added to allow list.").format(url))


@bot.slash_command()
async def block_links(ctx):
    """Block links on a channel."""
    channel = find_or_create_channel(ctx.channel.id, ctx.guild.id)
    channel.block_links_p = True
    session.commit()
    logger.log(MESSAGE, "URLs disabled for channel `%s` by `%s`.",
               ctx.channel.name,
               ctx.author.name,
               extra={'server': ctx.guild})
    await ctx.respond("URLs now blocked on this channel.")


@bot.slash_command()
async def unblock_links(ctx):
    """Enable links on a channel."""
    channel = find_or_create_channel(ctx.channel.id, ctx.guild.id)
    channel.block_links_p = False
    session.commit()
    logger.log(MESSAGE, "URLs enabled for channel `%s` by `%s`.",
               ctx.channel.name,
               ctx.author.name,
               extra={'server': ctx.guild})
    await ctx.respond("URLs now allowed on this channel.")


@bot.event
async def on_message(message):
    """Invoke when a message is received on the Guild/server."""
    if message.author.bot:
        return
    await process_message(message)


@bot.event
async def on_message_edit(message_before, message_after):
    """Invoke when a message is edited on the Guild/server."""
    if message_before.author.bot or message_after.author.bot:
        return
    await process_message(message_after)

if __name__ == '__main__':
    bot.run(token)
