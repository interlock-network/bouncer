"""This module provides a function to log to a Discord channel."""

import asyncio
import logging
from utility import configuration, MESSAGE


class DiscordLogger(logging.Handler):
    """This class is responsible for logging to Discord."""

    def __init__(self, emit_level=MESSAGE, channel=configuration.get('configuration', 'channel_log'),
                 *args, **kwargs):
        """Create a Discord Logger."""
        super(self.__class__, self).__init__(*args, **kwargs)
        self.channel = channel
        self.emit_level = emit_level

    def has_send_permissions(self, channel):
        """Check if the bot can write to a channel."""
        permissions = channel.permissions_for(channel.guild.me)
        return permissions.send_messages

    def log_channel(self, server):
        """Return the logging channel for a given server."""
        for channel in server.channels:
            if channel.name == self.channel and self.has_send_permissions(channel):
                return channel

    def emit(self, record):
        """Invoke when a log is to be logged."""
        if not record.levelno == self.emit_level:
            return
        msg = self.format(record)
        channel = self.log_channel(record.server)
        asyncio.create_task(channel.send(msg))
