"""Predicates."""

import requests
import re
import logging

from utility import urls_from_str
from model import AllowDomain


def url_http_p(str):
    """Return True or False depending on whether a URL is HTTP/s."""
    urlRegex = re.search('^http[s]?', str)
    return urlRegex


def str_contains_url_p(str):
    """Return True or False depending on whether a string contains a URL."""
    if (len(urls_from_str(str)) > 0):
        return True
    else:
        return False


# TODO: Update to use the actual endpoint!
def url_malicious_p(url):
    """Return True or False depending on whether a URL is malicious or not."""
    r = requests.get("https://perceptual.apozy.com/host/{0}".format(url))
    rjson = r.json()

    # If there was an error with the API, we cannot guarantee anything
    try:
        rjson['error']
        logging.warning("API error for URL %s", url)
        return True
    except KeyError:
        pass

    # If there is a corresponding traffic rank entry, the URL is well rated
    try:
        rjson['trafficRank']
        return False
    except KeyError:
        logging.info("Traffic rank not available for URL %s", url)
        return True


def allow_url_p(session, url_object, server):
    """Return True or False depending on whether a URL is to be ignored."""
    query = session.query(AllowDomain).filter_by(
        hostname=url_object.hostname,
        server_id=server.id).first()
    if query:
        return True
    else:
        return False
