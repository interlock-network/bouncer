"""Main entry point for the Interlock-Bouncer."""

import logging

import discord
from gettext import gettext
from urllib.parse import urlparse
from model import AllowDomain, Message, Channel, SettingsAccessRequest
from model import find_or_create_channel
from utility import urls_from_str, session, bot, token, configuration, MESSAGE
from utility import max_url_length, bouncer_domain
from predicates import (url_http_p, url_malicious_p, allow_url_p,
                        str_contains_url_p)
from discord_logger import DiscordLogger

from secrets import token_urlsafe
from threading import Thread
from serve import app

# Setup gettext for i18n
_ = gettext

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
        logger.log(MESSAGE, "Deleted: `%s`\nAuthor: `@%s`\nIn nolink channel: `#%s`",
                   message.content, message.author.name, message.channel.name,
                   extra={'server': message.guild})
        await message.reply(content=_("Denied! Mods said to block URLs in this channel."))
        await message.delete()
        return

    for url in urls_from_str(message.content):
        url_object = urlparse(url)
        if (allow_url_p(session, url_object, message.guild)):
            logger.log(MESSAGE, "Allowlisted URL ignored: `%s`\nChannel: `#%s`",
                       url, message.channel.name, extra={'server': message.guild})
            await message.reply(
                content=_("Mods said `{0}` is safe.")
                .format(url))
            break
        elif (len(url) > max_url_length):
            await message.reply(
                content=_(
                    "Watch it! This message has URLs that can't be scanned.\n**{0}:** `{1}`")
                .format(message.author.name, message.content))
            await message.delete()
            logger.log(MESSAGE, "Deleted URL too long to be scanned: `%s`\nAuthor: `@%s`\nChannel: `#%s`",
                       url, message.author.name, message.channel.name, extra={'server': message.guild})
            break
        elif (not url_http_p(url)):
            await message.reply(
                content=_(
                    "Watch it! This message has URLs that can't be scanned. \n**{0}:** `{1}`")
                .format(message.author.name, message.content))
            await message.delete()
            logger.log(MESSAGE, "Ignoring non-HTTP/S URL: `%s`\nChannel: `#%s`",
                       url, message.channel.name, extra={'server': message.guild})
            break
        elif (url_malicious_p(url)):
            await message.reply(
                content=_(
                    "Watch it! This message may have dangerous links. \n**{0}:** `{1}`")
                .format(message.author.name, message.content))
            if message.author.guild_permissions.administrator:
                await message.reply("Hey mods, if this message is safe, just type `/add_to_allowlist {0}` and then post it again."
                                    .format(url))
            await message.delete()
            logger.log(MESSAGE, "Dangerous URL deleted: `%s`\nMessage: `'%s'`\nAuthor: `@%s`\nChannel: `#%s`",
                       url, message.content, message.author.name, message.channel.name,
                       extra={'server': message.guild})
            session.add(Message(str(message.author.id), message.content, True))
            session.commit()
            break
        # If we have made it to this point, URL is OK
        logger.log(MESSAGE, "Scanned safe URL: `%s`\nChannel: `#%s`",
                   url, message.channel.name,
                   extra={'server': message.guild})


@bot.slash_command()
async def web_channel_edit(ctx):
    """Allow the user to edit channel settings via a web interface."""
    if not ctx.author.guild_permissions.ban_members:
        await ctx.respond("Denied! You're not authorized to do this.")
        return
    key = token_urlsafe(32)
    session.add(SettingsAccessRequest(key, ctx.guild.id, ctx.channel.id,
                                      ctx.guild.name, ctx.channel.name))
    session.commit()
    await ctx.author.send(
        "Yo! To edit your Bouncer settings for channel `#{}` in server `{}`, click {}/settings?key={}. This URL can only be used once!".format(
            ctx.channel.name, ctx.guild.name, bouncer_domain, key))
    await ctx.respond("Check your DMs for your one-time link to edit this channel on the web.")


@bot.slash_command()
async def remove_from_allowlist(ctx, url):
    """Remove a domain from the allow list in a given server."""
    url_object = urlparse(url)
    session.query(AllowDomain).filter_by(
        hostname=url_object.hostname,
        server_id=ctx.guild.id).delete()
    session.commit()
    logger.log(MESSAGE, "URL `%s` removed from allow list.",
               url, extra={'server': ctx.guild})
    await ctx.respond(_("URL `{}` removed from allow list.").format(url))


@bot.slash_command()
async def add_to_allowlist(ctx, url):
    """Allow a domain in a given server."""
    url_object = urlparse(url)
    session.add(AllowDomain(url_object.hostname, str(ctx.guild.id)))
    session.commit()
    logger.log(MESSAGE, "URL `%s` added to allow list.",
               url, extra={'server': ctx.guild})
    await ctx.respond(_("URL `{}` added to allow list.").format(url))


@bot.slash_command()
async def show_allowlist(ctx):
    """Return the allowlist for the user to read."""
    allow_list = session.query(AllowDomain).filter_by(
        server_id=ctx.guild.id).all()
    result_string = ""
    for allow_domain in allow_list:
        if allow_domain.hostname:
            result_string += allow_domain.hostname + "\n"

    msg = discord.Embed(
        title="Allow List",
        description=result_string,
        colour=discord.Colour.blue())

    await ctx.respond(embed=msg)


@bot.slash_command()
async def block_links(ctx):
    """Block links on a channel."""
    if not ctx.guild:
        await ctx.respond("You may only block links in a Server's channel.")
        return
    channel = find_or_create_channel(ctx.channel.id, ctx.guild.id)
    channel.block_links_p = True
    session.commit()
    logger.log(MESSAGE, "URLs disabled for channel `#%s` by `@%s`.",
               ctx.channel.name,
               ctx.author.name,
               extra={'server': ctx.guild})
    await ctx.respond("URLs now blocked on this channel.")


@bot.slash_command()
async def unblock_links(ctx):
    """Enable links on a channel."""
    if not ctx.guild:
        await ctx.respond("You may only unblock links in a Server's channel.")
        return
    channel = find_or_create_channel(ctx.channel.id, ctx.guild.id)
    channel.block_links_p = False
    session.commit()
    logger.log(MESSAGE, "URLs enabled for channel `#%s` by `@%s`.",
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
    # Start Flask on a separate thread.
    Thread(target=lambda: app.run(debug=False,
           use_reloader=False, host='0.0.0.0', port=80)).start()
    bot.run(token)
