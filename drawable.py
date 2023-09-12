import itertools as it
import random

from card import Card
from mixins import CardGameMixin


# TODO: define ABC Drawable instead of from_: Deck | Table.


class Deck(CardGameMixin):
    def __init__(self, trump: str):
        self.cards = [Card(v, s, s == trump)
                      for s, v in it.product(self.SUITS, self.RANKS)]

    def __repr__(self):
        cls_name = self.__class__.__name__
        return f'{cls_name}{tuple(self.cards)}'

    def __str__(self):
        cls_name = self.__class__.__name__.lower()
        cards_in_deck = len(self)
        cards = ', '.join(str(card) for card in self.cards)
        return f'{cls_name}[{cards_in_deck}]: {cards}'

    def shuffle(self):
        """Shuffle deck in-place"""
        random.shuffle(self.cards)

    def __len__(self) -> int:
        """Show number of cards left in a deck"""
        return len(self.cards)

    # TODO: add return annotation -> list[Card]
    def draw(self, n: int):
        """Remove and return 'n' cards from the top of a deck"""
        # arguable check, maybe will be removed in the future
        if n < 0:
            raise ValueError('Number of cards must be positive!')
        taken, self.cards = self.cards[:n], self.cards[n:]
        return taken

    def __getitem__(self, item):
        return self.cards[item]

    def __iter__(self):
        return iter(self.cards)


class Table:
    def __init__(self):
        self.cards: list[Card] = []
        self.card_ranks: set[str] = set()
        self.trash: list[Card] = []

    def __len__(self):
        """Return number of cards on a table"""
        return len(self.cards)

    def __bool__(self):
        return bool(self.cards)

    def __repr__(self):
        """Display cards on a table"""
        cls_name = self.__class__.__name__
        return f'{cls_name}{self.cards}'

    def __str__(self):
        """Display cards on a table"""
        return f'{", ".join(str(card) for card in self.cards)}'

    def add_card(self, card: Card) -> None:
        """Put a card on a table"""
        self.cards.append(card)
        self.card_ranks.add(card.ranl)

    def _cleanup(self):
        """Empty table from cards"""
        self.cards.clear()
        self.card_ranks.clear()

    def clear(self):
        """Transfer all cards from table to trash (beaten cards)"""
        self.trash += self.cards
        self._cleanup()

    def draw(self, *args) -> list[Card]:
        """Take all cards from table"""
        cards = self.cards.copy()
        self._cleanup()
        return cards
