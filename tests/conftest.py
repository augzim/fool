import pytest

from card import Card
from drawable import Table


@pytest.fixture(scope='function')
def card():
    return Card('A', 'Spades', True)


@pytest.fixture(scope='function')
def table_and_card(card):
    table = Table()
    table.add_card(card)
    return table, card

