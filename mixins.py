"""Define mixin classes, which provides accessory objects to card games-related classes"""


import re


class CardGameMixin:
    SUITS = ('Spades', 'Clubs', 'Diamonds', 'Hearts')
    SUITS_UNI = {
        'Spades': '♠',
        'Clubs': '♣',
        'Diamonds': '♦',
        'Hearts': '♥'
    }


class CardGameMixin36(CardGameMixin):
    """Mixin for card games based on 36-card deck"""
    VALUES = ('6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A')


class CardGameMixin52(CardGameMixin):
    """Mixin for card games based on 52-card deck"""
    VALUES = ('2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A')


MIXINS = {
    '36': CardGameMixin36,
    '52': CardGameMixin52,
}

# read deck size from config file and choose appropriate mixin class
with open('settings.cfg') as config:
    for line in config:
        if re.match('DECK_SIZE', line):
            deck_size = line.strip().split('=')[1]
            CardGameMixin = MIXINS[deck_size]
