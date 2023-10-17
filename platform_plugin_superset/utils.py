"""
Utilities for platform_plugin_superset app.
"""


def _(text):
    """
    Define a duymmy `gettext` replacement to make string extraction tools scrape strings marked for translation.
    """
    return text
