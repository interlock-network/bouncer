"""Predicates."""
from utility import configuration
import requests
import re

from utility import urls_from_str
from model import AllowDomain

base_url = configuration.get('backend', 'base_url')
api_key = configuration.get('backend', 'api_key')


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


def url_malicious_p(url):
    """Return True or False depending on whether a URL is malicious or not."""
    json_payload = {
        "key": api_key,
        "url": url
    }

    r = requests.post("{0}/malicious_p".format(base_url), json=json_payload)
    rjson = r.json()
    return rjson['malicious']


def allow_url_p(session, url_object, server):
    """Return True or False depending on whether a URL is to be ignored."""
    query = session.query(AllowDomain).filter_by(
        hostname=url_object.hostname,
        server_id=server.id).first()
    if query:
        return True
    else:
        return False
