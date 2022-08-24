"""This module provides a function to log to a Discord channel."""

import asyncio
import logging
from utility import client
from utility import configuration


class DiscordLogger(logging.Handler):
    """This class is responsible for logging to Discord."""

    def __init__(self, channel=configuration.get('configuration', 'channel_log'),
                 *args, **kwargs):
        """Create a Discord Logger."""
        super(self.__class__, self).__init__(*args, **kwargs)
        self.channel = channel

    def has_send_permissions(self, channel):
        """Check if the bot can write to a channel."""
        permissions = channel.permissions_for(channel.guild.me)
        return permissions.send_messages

    def log_channels(self):
        """Return the list of channels to log to."""
        if hasattr(self, "channels") and self.channels != []:
            return self.channels
        else:
            self.channels = []
            for guild in client.guilds:
                for channel in guild.channels:
                    if channel.name == self.channel and self.has_send_permissions(channel):
                        self.channels.append(channel)
            return self.channels

    def emit(self, record):
        """Invoke when a log is to be logged."""
        msg = self.format(record)
        for channel in self.log_channels():
            asyncio.create_task(channel.send(msg))
