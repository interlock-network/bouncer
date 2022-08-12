"""Models used by the Interlock-Bouncer bot."""

import configparser
import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer, Boolean, Column, Text, create_engine
from sqlalchemy.types import TIMESTAMP

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


if __name__ == '__main__':
    # Create the database
    configuration = configparser.ConfigParser()
    configuration.read('configuration.ini')

    sqlalchemy_url = configuration.get('persistence', 'sqlalchemy_url')
    engine = create_engine(sqlalchemy_url, echo=True, future=True)
    Base.metadata.create_all(engine)
