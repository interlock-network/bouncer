"""Models used by the Interlock-Bouncer bot."""

import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer, Boolean, Column, Text, create_engine, String
from sqlalchemy.types import TIMESTAMP
from utility import session, configuration

Base = declarative_base()


class Channel(Base):
    """This class represents a channel on a server."""

    __tablename__ = 'channel'
    id = Column(Integer, primary_key=True)
    channel_id = Column(Text)
    server_id = Column(Text)
    block_links_p = Column(Boolean)

    def __init__(self, channel_id, server_id):
        """Create a Channel.

        :param channel_id: The Discord channel id
        :param server_id: The Discord guild/server id
        :returns: nil
        """
        self.channel_id = channel_id
        self.server_id = server_id


def find_or_create_channel(channel_id, server_id):
    """Find or create channel."""
    channel = session.query(Channel).filter_by(
        channel_id=channel_id,
        server_id=server_id).first()
    if channel:
        return channel
    else:
        channel = Channel(channel_id, server_id)
        session.add(channel)
        return channel


class AllowDomain(Base):
    """This class represents a hostname (domain) to allow on a server."""

    __tablename__ = 'allowdomain'
    id = Column(Integer, primary_key=True)
    hostname = Column(Text)
    server_id = Column(Text)

    def __init__(self, hostname, server_id):
        """Create a AllowDomain.

        :param hostname: The hostname to allow.
        :param server_id: The Discord guild/server id
        :returns: nil
        """
        self.hostname = hostname
        self.server_id = server_id


class Message(Base):
    """This class represents a Discord message on a server."""

    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    author_id = Column(Text)
    message = Column(Text)
    malicious_p = Column(Boolean)
    time = Column('timestamp', TIMESTAMP(timezone=False), nullable=False)

    def __init__(self, author_id, message, malicious_p):
        """Create a Message.

        :param author_id: The ID of the author.
        :param message: The message.
        :param malicious_p: Is the URL malicious?
        :returns: nil

        """
        self.author_id = author_id
        self.message = message
        self.malicious_p = malicious_p
        self.time = datetime.datetime.now()


class APIKey(Base):
    """This class represents an API key."""

    __tablename__ = 'api_key'

    key = Column(String(1024), primary_key=True)

    def __init__(self, key):
        """Create an API key."""
        self.key = key


if __name__ == '__main__':
    # Create the database
    configuration.read('configuration.ini')
    sqlalchemy_url = configuration.get('persistence', 'sqlalchemy_url')
    engine = create_engine(sqlalchemy_url, echo=True, future=True)
    Base.metadata.create_all(engine)
