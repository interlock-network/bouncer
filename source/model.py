"""Models used by the Interlock-Bouncer bot."""

import configparser

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Text, create_engine


Base = declarative_base()


class AllowDomain(Base):
    """This class represents a hostname (domain) to allow on a server."""

    __tablename__ = 'user'
    id = Column(Text, primary_key=True)
    hostname = Column(Text)
    server_id = Column(Text)


if __name__ == '__main__':
    # Create the database
    configuration = configparser.ConfigParser()
    configuration.read('configuration.ini')

    sqlalchemy_url = configuration.get('persistence', 'sqlalchemy_url')
    engine = create_engine(sqlalchemy_url, echo=True, future=True)
    Base.metadata.create_all(engine)
