"""Provide a configuration settings for an entire game with a CONFIG dict.
Settings should be specified in the settings.py file in the project's root directory."""

# TODO: make it using configparser module
with open('settings.cfg') as config:
    CONFIG = {}

    for line in config:
        if '=' in line:
            key, value = line.strip().split('=')
            CONFIG[key] = value
