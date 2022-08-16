"""This module provides a function to log to a Discord channel."""

import logging


class DiscordLogger(logging.Handler):
    """This class is responsible for logging to Discord."""

    def emit(self, record):
        """Invoke when a log is to be logged."""
        msg = self.format(record)
        print(msg)
