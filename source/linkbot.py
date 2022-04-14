"""Main entry point for the Linkbot."""

import configparser
import logging

# Set the logging up
logging.basicConfig(level=logging.INFO)

# Parse the configuration.ini file in the repository root
configuration = configparser.ConfigParser()
configuration.read('configuration.ini')

# Get needed values from the configuration.ini file
token = configuration.get('discord', 'token')
