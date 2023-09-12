"""Provide a configuration settings for an entire game with a CONFIG dict."""


from pathlib import Path


# TODO: make it using configparser module

settings = Path(__file__).parent / 'settings.cfg'

with open(settings) as config:
    CONFIG = {}

    for line in config:
        if '=' in line:
            key, value = line.strip().split('=')
            CONFIG[key] = int(value) if value.isdigit() else value
