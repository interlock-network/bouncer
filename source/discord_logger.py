"""This module provides a function to log to a Discord channel."""

import logging
from utility import client
from utility import configuration


class DiscordLogger(logging.Handler):
    """This class is responsible for logging to Discord."""

    def log_channels(self):
        """Return the list of channels to log to."""
        if hasattr(self, "channels") and self.channels != []:
            return self.channels
        else:
            self.channels = []
            for guild in client.guilds:
                for channel in guild.channels:
                    if channel.name == configuration.get(
                            'configuration', 'channel_log'):
                        self.channels.append(channel)
            return self.channels

    def emit(self, record):
        """Invoke when a log is to be logged."""
        msg = self.format(record)
        print(self.log_channels())
        print(msg)
