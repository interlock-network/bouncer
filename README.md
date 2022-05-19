# Interlock-bouncer
A Discord bot to scan for & neutralize malicious links.

# Status
Warning: The Interlock-bouncer is in early alpha. The current
implementation results in a high level of false positives (benign
links marked as dangerous). In simpler terms, we err on the side of
caution to keep your community safe.

# Dependencies:

- Python 3.8
- Python Discord.py
- Python Requests

# Deployment instructions

## Configuration

You'll need to populate the `configuration.ini` file OR set the
environment variable `DISCORD_TOKEN` with the value of your Discord
token.

## Ubuntu 20.04

1. Verify that python3.8 is installed: `python --version`
2. Install `apt install python3.8-venv` to be able to create virtual environments.
3. Install make: `apt install make`.
4. Create a virtual Python environment `python3 -m venv /path/to/environment`
5. Start GNU `screen` to create a new detachable shell session.
6. Activate your Python virtual environment `source /path/to/environment/bin/activate`
7. Use `pip` to install all Python dependencies as specified in this
   repository's corresponding `shell.nix` file.
8. Execute `make run` within this repository's root.
9. Press `C-a d`. That is, `Ctrl+a`, then let go, then press `d`. This
   will detach you from your `screen` session, and allow `bouncer` to
   continue running when you exit your `sh` session. If you wish to
   reconnect to your `screen` session, execute `screen -r`. For more
   information, please see the documentation for `GNU screen`.

## NixOS

1. Execute `nix-shell` in this repository's root.
2. Execute `make run` in this repository's root.
3. (Optional) utilize `GNU screen` to create a detachable session.

# Setting up a bot:

In order to set-up a bot, you have to do several processes within the
Discord interface. The processes are explained and outlined at the
resource below.

https://realpython.com/how-to-make-a-discord-bot-python/

# Authorizing Interlock-bouncer for your server

Visit the following URL to authorize Interlock-bouncer to run on your own
server:
https://discord.com/api/oauth2/authorize?client_id=966558765799342131&permissions=1641751637056&scope=bot

# Testing Interlock-bouncer

To test if Interlock-bouncer is working, post the following
known-unsafe link in a channel Interlock-bouncer is monitoring:
`http://phishing.com`

Your message should immediately be deleted and Interlock-bouncer
should post the following:

```
Message contains dangerous links! NAME: http://phishing.com
```

Here's a screenshot of the expected behavior:

<img width="421" alt="Interlock-bouncer reacting to a malicious link" src="reaction.png">
