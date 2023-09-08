"""Provide a configuration settings for an entire game with a CONFIG dict."""


# TODO: make it using configparser module
with open('settings.cfg') as config:
    CONFIG = {}

    for line in config:
        if '=' in line:
            key, value = line.strip().split('=')
            CONFIG[key] = int(value) if value.isdigit() else value
