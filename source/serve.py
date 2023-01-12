"""Entry point for the Interlock web server."""

import requests
from flask import Flask, request, render_template
from utility import bot, session, backend_api_key, backend_base_url
from model import SettingsAccessRequest, AllowDomain
from model import find_or_create_channel
from urllib.parse import urlparse


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

@app.route('/user_count', methods=['GET'])
def user_count():
    user_count = 0
    for server in bot.guilds:
        user_count += server.member_count
    return str(user_count)

@app.route('/server_count', methods=['GET'])
def server_count():
    server_count = len(bot.guilds)
    return str(server_count)

@app.route('/settings', methods=['POST'])
def settings_save():
    """Save the user requested settings."""
    key = request.form.get("key")
    access_request = session.query(SettingsAccessRequest).filter_by(key=key).first()
    if access_request:
        channel = find_or_create_channel(access_request.channel_id, access_request.server_id)
        urls_disabled = request.form.get("urls_disabled")
        allowed_urls = request.form.get("allowed_urls")

        if urls_disabled:
            channel.block_links_p = False
        else:
            channel.block_links_p = True

        for url in allowed_urls.split(","):
            url_object = urlparse(url)
            session.add(AllowDomain(url_object.hostname, access_request.server_id))

        session.query(SettingsAccessRequest).filter_by(key=key).delete()
        session.commit()
        return render_template("settings_save.html",
                               server_name=access_request.server_name,
                               channel_name=access_request.channel_name)
    else:
        return "Access forbidden."
