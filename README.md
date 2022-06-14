# Interlock-Bouncer
Interlock-Bouncer is a Discord bot that scans your server for malicious
links and neutralizes them. It does this by querying our database of
known-malicious sites. If the site is new, we use our proprietary visual
AI to identify 0-day phishing sites. Setup takes just a minute or two
and it begins protecting your server instantly.

Interlock-Bouncer is a project of [Interlock](https://www.interlock.network/),
a web3 company that is decentralizing security. It's free to use in
exchange for an occasional Interlock partnership post. In the future,
Interlock-Bouncer will be powered by $INTR, Interlock's token launching
later this year.

# Status
Warning: The Interlock-Bouncer is in early alpha. The current
implementation results in a high level of false positives (benign
links marked as dangerous). In simpler terms, we err on the side of
caution to keep your community safe.

# Dependencies:

- Python 3.8
- Python Discord.py
- Python Requests
- GNU gettext/xgettext (to update translation files)

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

# Updating the translations

In order to update the translations it is necessary to scan all the
appropriate Python files with `gettext` or `xgettext` to generate the
appropriate `.po` files. An example of the command can be seen below:

`xgettext -o locales/base.pot -L Python source/bouncer.py`

after you create your `base.pot` file, you will need to create a
directory in the following format for each language (example language, en):

`locales/en/LC_MESSAGES/base.po` where you simply copy `base.pot` to
`base.po`.

After you have edited your translations and set your `CHARSET` in your
`base.po` file, you'll need to compile it to machine code using `msgfmt`.

To do so, navigate to `locales/en/LC_MESSAGES` and execute the
following command:

`msgfmt -o base.mo base`

# Setting it up

In order to set-up a bot, you have to do several processes within the
Discord interface. The processes are explained and outlined at the
resource below.

https://realpython.com/how-to-make-a-discord-bot-python/

# Authorizing Interlock-Bouncer for your server

Visit the following URL to authorize Interlock-Bouncer to run on your own
server:
https://discord.com/api/oauth2/authorize?client_id=966558765799342131&permissions=1641751637056&scope=bot

# Testing Interlock-Bouncer

To test if Interlock-Bouncer is working, post the following
known-unsafe link in a channel Interlock-Bouncer is monitoring:
`http://phishing.com`

Your message should immediately be deleted and Interlock-Bouncer
should post the following:

```
Message contains dangerous links! NAME: http://phishing.com
```

Here's a screenshot of the expected behavior:

<img width="421" alt="Interlock-Bouncer reacting to a malicious link" src="reaction.png">
