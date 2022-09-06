"""Main entry point for the Interlock-Bouncer."""

import gettext
import logging
import discord

from urllib.parse import urlparse
from model import AllowDomain, Message, Channel
from model import find_or_create_channel
from utility import str_from_list, urls_from_str, session, client, token, configuration, MESSAGE
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


@client.event
async def on_ready():
    """Invoke when the bot has connected to Discord."""
    print(f'{client.user} has connected to Discord!')
    # Set the bot profile picture
    with open('docs/profile.png', 'rb') as image:
        await client.user.edit(avatar=image.read())

@client.event
async def on_message(message):
    """Handle a message, deleting or stripping it of links."""

    if message.author == client.user:
        return
        
    channel = session.query(Channel).filter_by(
        channel_id=message.channel.id,
        server_id=message.guild.id).first()
    if channel and channel.block_links_p and str_contains_url_p(message.content):
        logger.log(MESSAGE, "User `%s` posted message `%s` in nolink channel `%s`.",
                   message.author.name,
                   message.content,
                   message.channel.name)
        await message.reply(content=_("Mods have set this channel to have no links from users."))
        await message.delete()
        return

    for url in urls_from_str(message.content):
        url_object = urlparse(url)
        if (allow_url_p(session, url_object, message.guild)):
            logger.log(MESSAGE, "URL ignored: %s", url)
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
            logger.log(MESSAGE, "Ignoring URL %s because it is not HTTP/s", url)
            break
        elif (url_malicious_p(url)):
            await message.reply(
                content=_("Caution: message may contain dangerous links! \n\
**{0}:** `{1}`").format(message.author.name, message.content))
            await message.delete()
            logger.log(MESSAGE, "URL marked as insecure: %s. Message: %s",
                       url, message.content)
            session.add(Message(str(message.author.id), message.content, True))
            session.commit()
            break
        # If we have made it to this point, URL is OK
        logger.log(MESSAGE, "URL marked as secure: \n%s\n%s\n%s", message.author.name, message.channel.name, url)

@client.slash_command()
async def allow_domains(ctx, domains_separated_by_space: discord.Option(discord.SlashCommandOptionType.string)):
    """Allows a set of domains."""
    urls = urls_from_str(domains_separated_by_space)
    for url in urls:
        url_object = urlparse(url)
        session.add(AllowDomain(url_object.hostname,
                                str(ctx.guild.id)))
    session.commit()
    url_str = str_from_list(urls)
    logger.log(MESSAGE, "URLs `%s` added to allow list.", url_str)
    await ctx.respond(_("URLs `{}` added to allow list.")
                                .format(url_str))

@client.slash_command()
async def unallow_domains(ctx, domains_separated_by_space: discord.Option(discord.SlashCommandOptionType.string)):
    """Unallows a set of domains."""
    urls = urls_from_str(domains_separated_by_space)
    for url in urls:
        url_object = urlparse(url)
        session.query(AllowDomain).filter_by(
            hostname=url_object.hostname,
            server_id=ctx.guild.id).delete()
    session.commit()
    url_str = str_from_list(urls)
    logger.log(MESSAGE, "URLs `%s` removed from allow list.", url_str)
    await ctx.respond(_("URLs `{}` removed from allow list.")
                                .format(url_str))

@client.slash_command()
async def unblock_links(ctx):
    """Unblock links."""
    channel = find_or_create_channel(ctx.channel.id, ctx.guild.id)
    channel.block_links_p = False
    session.commit()
    logger.log(MESSAGE, "URLs enabled for channel `%s` by `%s`.",
                ctx.channel.name,
                ctx.author.name)
    await ctx.respond("URLs now allowed on this channel.")

@client.slash_command()
async def block_links(ctx):
    """Block links."""
    channel = find_or_create_channel(ctx.channel.id, ctx.guild.id)
    channel.block_links_p = True
    session.commit()
    logger.log(MESSAGE, "URLs disabled for channel `%s` by `%s`.",
                ctx.channel.name,
                ctx.author.name)
    await ctx.respond("URLs now blocked on this channel.")

if __name__ == '__main__':
    client.run(token)
