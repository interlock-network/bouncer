"""Main entry point for the Interlock-Bouncer."""

import logging

from gettext import gettext
from urllib.parse import urlparse
from model import AllowDomain, Message, Channel, SettingsAccessRequest
from model import find_or_create_channel
from utility import urls_from_str, session, bot, token, configuration, MESSAGE
from utility import max_url_length, bouncer_domain
from predicates import (url_http_p, url_malicious_p, allow_url_p,
                        str_contains_url_p)
from discord_logger import DiscordLogger
from flask import Flask, request, render_template
from secrets import token_urlsafe
from threading import Thread

# Setup gettext for i18n
_ = gettext

# Set the logging up
logging.basicConfig(filename=configuration.get('configuration', 'log_file'),
                    level=logging.DEBUG)
logger = logging.getLogger()

discord_logger = DiscordLogger()
logger.addHandler(discord_logger)

app = Flask(__name__)


@app.route('/settings', methods=['GET'])
def settings_view():
    """Return a page the user can edit settings on."""
    key = request.args.get('key')
    access_request = session.query(SettingsAccessRequest).filter_by(key=key).first()
    if access_request:
        return render_template('settings.html',
                               key=key,
                               server_name=access_request.server_name,
                               channel_name=access_request.channel_name)
    else:
        return "Access forbidden."


@app.route('/settings', methods=['POST'])
def settings_save():
    """Save the user requested settings."""
    key = request.form.get("key")
    access_request = session.query(SettingsAccessRequest).filter_by(key=key).first()
    if access_request:
        channel = find_or_create_channel(access_request.channel_id, access_request.server_id)

        if(request.form.get("urls_disabled")):
            channel.block_links_p = False
        else:
            channel.block_links_p = True

        for url in request.form.get("allowed_urls").split(","):
            url_object = urlparse(url)
            session.add(AllowDomain(url_object.hostname, access_request.server_id))

        session.query(SettingsAccessRequest).filter_by(key=key).delete()
        session.commit()
        return render_template("settings_save.html",
                               server_name=access_request.server_name,
                               channel_name=access_request.channel_name)
    else:
        return "Access forbidden."


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
            logger.log(MESSAGE, "URL marked as insecure: `%s`. Message: `%s`",
                       url, message.content,
                       extra={'server': message.guild})
            session.add(Message(str(message.author.id), message.content, True))
            session.commit()
            break
        # If we have made it to this point, URL is OK
        logger.log(MESSAGE, "URL marked as secure: `%s`", url, extra={'server': message.guild})


@bot.slash_command()
async def edit_settings_web_interface(ctx):
    """Allow the user to edit channel settings via a web interface."""
    key = token_urlsafe(32)
    session.add(SettingsAccessRequest(key, ctx.guild.id, ctx.channel.id,
                                      ctx.guild.name, ctx.channel.name))
    session.commit()
    await ctx.author.send(
        "To edit the settings for channel `{}` in server `{}`, visit: {}/settings?key={} in a browser. This URL can only be used once!".format(
            ctx.channel.name, ctx.guild.name, bouncer_domain, key))
    await ctx.respond("Edit code successfully requested. Please check your direct messages.")


@bot.slash_command()
async def unallow_domain(ctx, url):
    """Remove a domain from the allow list in a given server."""
    url_object = urlparse(url)
    session.query(AllowDomain).filter_by(
        hostname=url_object.hostname,
        server_id=ctx.guild.id).delete()
    session.commit()
    logger.log(MESSAGE, "URL `%s` removed from allow list.", url, extra={'server': ctx.guild})
    await ctx.respond(_("URL `{}` removed from allow list.").format(url))


@bot.slash_command()
async def allow_domain(ctx, url):
    """Allow a domain in a given server."""
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
    # Start Flask on a separate thread.
    Thread(target=lambda: app.run(debug=True, use_reloader=False)).start()
    bot.run(token)
