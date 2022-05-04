# Linkbot
A Discord bot to scan for & neutralize malicious links.

# Deployment instructions

## Ubuntu 20.04

1. Verify that python3.8 is installed: `python --version`
2. Install `apt install python3.8-venv` to be able to create virtual environments.
3. Install make: `apt install make`.
4. Create a virtual Python environment `python3 -m venv /path/to/environment`
5. Start GNU `screen` to create a new detachable session.
6. Activate your Python virtual environment `source /path/to/environment/bin/activate`
7. Use `pip` to install all Python dependencies as specified in this
   repository's corresponding `shell.nix` file.
8. Execute `make run` within this repository's root.
9. Press `C-a d`. That is, `Ctrl+a`, then let go, then press `d`. This
   will detach you from your `screen` session, and allow `linkbot` to
   continue running when you exit your `sh` session. If you wish to
   reconnect to your `screen` session, execute `screen -r`. For more
   information, please see the documentation for `GNU screen`.

## NixOS

1. Execute `nix-shell` in this repository's root.
2. Execute `make run` in this repository's root.
3. (Optional) utilize `GNU screen` to create a detachable session.

