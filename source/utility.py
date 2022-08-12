"""Utility functions."""

import re
import configparser
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


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
engine = create_engine(sqlalchemy_url, echo=True, future=True)
DBSession = sessionmaker(bind=engine)
session = DBSession()
