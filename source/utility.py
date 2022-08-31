"""Utility functions."""

import logging
import re
import configparser
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import discord
import os


def urls_from_str(str):
    """Find and return all URLs in a string."""
    urlRegex = re.findall('[a-zA-Z]+?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|\
    [!*, ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', str)
    return urlRegex


# Parse the configuration.ini file in the repository root
configuration = configparser.ConfigParser()
configuration.read('configuration.ini')

# Setup the SQLAlchemy session
sqlalchemy_url = configuration.get('persistence', 'sqlalchemy_url')
engine = create_engine(sqlalchemy_url, echo=False, future=True)
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Get the discord token from the configuration.ini file
token_from_config = configuration.get('discord', 'token')
# Get the discord token from the environment variable
token_from_environment = os.getenv('DISCORD_TOKEN')

# Set the token either by config or environment variable
token = token_from_config or token_from_environment

if (token_from_config and token_from_environment and
   token_from_config != token_from_environment):
    logging.warning("Different Discord token set via configuration.ini file \
AND environment variable! Prioritizing token from configuration.ini.")

# Create a discord client
intents = discord.Intents.default()
client = discord.Client(intents=intents)

# Define MESSAGE log level
MESSAGE = 25

# "Register" new loggin level
logging.addLevelName(MESSAGE, 'MESSAGE')


class MyLogger(logging.Logger):
    """Custom logger with additional log level support."""

    def message(self, msg, *args, **kwargs):
        """Log a message."""
        if self.isEnabledFor(MESSAGE):
            self._log(MESSAGE, msg, args, **kwargs)


logging.setLoggerClass(MyLogger)
