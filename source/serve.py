"""Entry point for the Interlock web server."""

import requests
from flask import Flask, request, render_template
from utility import bot, session, backend_api_key, backend_base_url
from model import SettingsAccessRequest, AllowDomain
from model import find_or_create_channel
from urllib.parse import urlparse


app = Flask(__name__)


@app.route('/statistics', methods=['GET'])
def statistics_view():
    """Return a view of KPIs."""
    server_count = len(bot.guilds)
    user_count = 0
    for server in bot.guilds:
        user_count += server.member_count

    json_payload = {
        "key": backend_api_key,
    }

    urls_scanned_count = requests.post("{0}/urls_scanned_count".format(backend_base_url), json=json_payload).text
    malicious_urls_scanned_count = requests.post("{0}/malicious_urls_scanned_count".format(backend_base_url), json=json_payload).text
    unique_urls_scanned_count = requests.post("{0}/unique_urls_scanned_count".format(backend_base_url), json=json_payload).text
    unique_malicious_urls_scanned_count = requests.post("{0}/unique_malicious_urls_scanned_count".format(backend_base_url), json=json_payload).text

    return render_template('statistics.html',
                           server_count=server_count,
                           user_count=user_count,
                           urls_scanned_count=urls_scanned_count,
                           malicious_urls_scanned_count=malicious_urls_scanned_count,
                           unique_urls_scanned_count=unique_urls_scanned_count,
                           unique_malicious_urls_scanned_count=unique_malicious_urls_scanned_count)


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
