import pytest

from card import Card


class TestCard:
    def test___init__(self):
        """Correct args -> correct Card instance"""
        card = Card('A', 'Spades', True)
        assert card.__dict__ == {'rank': 'A', 'suit': 'Spades', 'trump': True}, \
            'Wrong card creation!'

    def test___init_fail(self):
        """Incorrect args, either rank or suit -> ValueError"""
        with pytest.raises(ValueError) as exc_info:
            rank = 'non-existing rank'
            Card(rank, 'SPADES', True)
        assert f'{rank} not in {Card.RANKS}' in str(exc_info), \
            f'Initializing Card instance with a {rank} should raise a ValueError!'

    @pytest.mark.parametrize('s, trump, card', [
        ('JS', 'Hearts', Card('J', 'Spades', False)),
        ('9H', 'Spades', Card('9', 'Hearts', False)),
        ('AD', 'Diamonds', Card('A', 'Diamonds', True)),
    ])
    def test_convert(self, s, trump, card):
        # s: string representation of a card
        assert Card.convert(s, trump).is_identical(card), 'Wrong card conversion!'

    def test_equal_suit(self):
        """For 2 cards with equal suits method should return True"""
        c1 = Card('7', 'Spades', True)
        c2 = Card('A', 'Spades', True)
        assert c1.equal_suit(c2), f'Suits of {c1!s} and {c2!s} must be equal!'

    def test_equal_rank(self):
        """For 2 cards with equal ranks method should return True"""
        c1 = Card('A', 'Hearts', False)
        c2 = Card('A', 'Spades', True)
        assert c1.equal_rank(c2), f'Ranks of {c1!s} and {c2!s} must be equal!'

    @pytest.mark.parametrize(
        'card', ['AS', Card('A', 'Spades', True)]
    )
    def test_is_identical(self, card):
        """Two identical cards, either in a form of a Card instance
        or in a short-string representation should be identical"""
        c = Card('A', 'Spades', True)
        assert c.is_identical(card), f'{c!s} and {card!s} should be identical!'

    @pytest.mark.parametrize('smaller, greater', [
        (Card('7', 'Spades', True), Card('A', 'Spades', True)),
        (Card('7', 'Hearts', False), Card('A', 'Hearts', False)),
        (Card('A', 'Hearts', False), Card('7', 'Spades', True)),
    ])
    def test___gt__(self, smaller, greater):
        """Compare different cards for value"""
        assert smaller < greater, f'{greater!s} should be greater than {smaller!s}!'

    def test__gt__non_comparable(self):
        """Two non-trump cards of different suits cannot be
        compared -> none of them is greater than another"""
        c1 = Card('7', 'Hearts', False)
        c2 = Card('10', 'Clubs', False)
        assert not (c1 < c2 or c2 > c1), \
            'Two non-trump cards of different suits cannot be compared!'
