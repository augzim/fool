"""Define mixin classes, which provides accessory objects to card games-related classes"""


from config import CONFIG


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

CardGameMixin = MIXINS[CONFIG['DECK_SIZE']]
