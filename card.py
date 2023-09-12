from __future__ import annotations
from typing import TypeVar

from mixins import CardGameMixin


# TODO: maybe it's better to set trump to None initially?
class Card(CardGameMixin):
    def __init__(self, rank: str, suit: str, trump: bool) -> None:
        self.rank = self._validate_input(rank, self.RANKS)
        self.suit = self._validate_input(suit, self.SUITS)
        self.trump = trump

    T = TypeVar('T')

    @staticmethod
    def _validate_input(input_: T, possible_values, /) -> T:
        """Validate user input to create a class instance"""
        if input_ in possible_values:
            return input_
        raise ValueError(f'{input_} not in {possible_values}')

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}{self.rank, self.suit, self.trump}'

    def __str__(self) -> str:
        suit_uni = self.SUITS_UNI[self.suit]
        return f'{self.rank}{suit_uni}'

    def equal_suit(self, card: Card) -> bool:
        """Compares two cards suits"""
        return self.suit == card.suit

    def equal_rank(self, card: Card) -> bool:
        """Compares two cards ranks"""
        return self.rank == card.rank

    def is_identical(self, card: Card | str):
        """Check if the card is identical to another (specified) one"""
        try:
            return self.rank == card.rank and self.suit == card.suit
        except AttributeError:
            return f'{self.rank}{self.suit[0]}' == card

    def __gt__(self, other: Card) -> bool:
        """
        One card can be greater than another, if only both have the same suit,
        and a rank of the first one is greater than the rank of another.
        If cards have different suits, then at most one card can be a trump card,
        and if the first card is a trump, then it's gt than another, else it's not
        greater (either because the second card is a trump or both are not trump,
        and thus are not comparable).
        """
        if self.equal_suit(other):
            return self.RANKS.index(self.rank) > other.RANKS.index(other.rank)
        return self.trump
