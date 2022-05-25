"""Utility functions."""

import re


def urls_from_str(str):
    """Find and return all URLs in a string."""
    urlRegex = re.findall('[a-zA-Z]+?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|\
    [!*, ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', str)
    return urlRegex
