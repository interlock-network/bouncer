# Dependencies

- Python 3.8
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

# Setup

In order to set-up a bot, you have to do several processes within the
Discord interface. The processes are explained and outlined at the
resource below.

https://realpython.com/how-to-make-a-discord-bot-python/

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
