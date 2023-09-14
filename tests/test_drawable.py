import pytest

from config import CONFIG
from drawable import Deck, Table


class TestDeck:
    @pytest.mark.parametrize('cards_num', [100, CONFIG['DECK_SIZE'], 5, 0])
    def test_draw(self, cards_num):
        """
        1. Number of cards to take is greater than the number of cards is in
            the deck -> get all cards, no cards should leave in the deck.
        2. Draw all cards from the deck -> no cards should leave in the deck.
        3. Number of cards to take is less than the num of cards in the deck,
            -> return specified number of cards and the num of cards left in
            deck should decrease by the number of taken cards.
        4. Zero cards to take -> the num of cards in the deck should stay the
            same.
        """
        deck = Deck(trump='Spades')
        deck_length = len(deck)
        taken_cards = deck.draw(cards_num)
        expected_num = CONFIG['DECK_SIZE'] if cards_num > deck_length else cards_num

        assert len(taken_cards) == expected_num, 'Wrong number of cards taken!'
        assert (len(deck) == deck_length - expected_num
                if cards_num <= CONFIG['DECK_SIZE'] else 0,
                'Wrong number of cards left in the deck!')


class TestTable:
    def test_add_card(self, card):
        table = Table()
        table.add_card(card)
        assert (table.card_ranks == {card.rank} and table.cards == [card],
                'A card was put on the table improperly!')

    def test__cleanup(self, table_and_card):
        table, _ = table_and_card
        table._cleanup()
        assert table.card_ranks == set() and table.cards == [], 'Table is not empty!'

    def test_clear(self, table_and_card):
        table, card = table_and_card
        table.clear()
        assert table.card_ranks == set() and table.cards == [], 'Table is not empty!'
        assert table.trash == [card], 'Beaten cards are not in trash!'

    def test_draw(self, table_and_card):
        table, card = table_and_card
        taken_cards = table.draw()
        assert table.card_ranks == set() and table.cards == [], 'Table is not empty'
        assert taken_cards == [card], 'Wrong cards are taken!'
