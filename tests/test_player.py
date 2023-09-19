from unittest import mock

import _pytest.fixtures
import pytest

from card import Card
from drawable import Deck, Table
from player import Player


# TODO: in each case check if player specified card that he already send the second time (throw_cards especially)


class TestPlayer:
    @pytest.mark.parametrize('user_input', [
        # check input length (bottom edge)
        ('', 'AS', 'Sue'),
        # check input length (top edge)
        ('S' * 21, 'S' * 20),
        # check allowed characters
        ('NO SPACES!', 'i*/?!', '920202!', '0w90r_)9', '--!_335f', '\r\n', '\n\n\n\n\n', 'Bob'),
    ])
    def test___init__(self, user_input, capsys):
        """Check length of and allowed characters in user inputs"""
        with mock.patch('player.input', side_effect=user_input):
            Player()
        output = capsys.readouterr().out.strip()
        correct_name = user_input[-1]
        assert output == f'Hi, {correct_name}, have a nice game and good luck!', \
            'Unacceptable username was set!'

    @pytest.mark.parametrize('target_card, hand, expected_card', [
        ('AS', [Card('A', 'Spades', True), Card('7', 'Clubs', False)],
         Card('A', 'Spades', True)),
        # object-like card representation
        (Card('A', 'Spades', True), [Card('A', 'Spades', True)], Card('A', 'Spades', True)),
        # empty hand
        ('AS', [], None),
        # no specified card
        ('AS', [Card('K', 'Spades', True), Card('Q', 'Hearts', False)], None)
    ])
    def test_find_card(self, target_card, hand, expected_card):
        """
        1. Card (str) in player's hand -> find card.
        2. Card (instance of 'Card') in player's hand -> find card.
        3. Card (str) NOT in player's hand (empty) -> get None.
        4. Card (str) NOT in player's hand (NOT empty) -> get None.
        """
        with mock.patch('player.input', return_value='PLAYER'):
            player = Player()
            player.hand = hand

        actual_card = player.find_card(target_card)
        assert actual_card == expected_card \
            if actual_card is not None else actual_card is expected_card, \
            'Wrong card was found!'

    @pytest.mark.parametrize('from_, cards_num', [
        (Deck('Spades'), 0), (Deck('Spades'), 2), (Table(), 3),
    ])
    def test_take_cards(self, from_, cards_num):
        """
        1. From Deck.
        2. From Table (always take all cards from a table).
        3. Check that in both cases cards get into hand
            and number of cards taken should be correct.
        """
        # preparation
        if isinstance(from_, Table):
            cards = [Card('A', 'Spades', True),
                     Card('7', 'Hearts', False),
                     Card('6', 'Clubs', False)]

            [from_.add_card(card) for card in cards]

        with mock.patch('player.input', return_value='PLAYER'):
            player = Player()
            player.hand = []

        player.take_cards(from_, cards_num)
        assert len(player.hand) == cards_num, 'Player took wrong number of cards!'

    @pytest.mark.parametrize('user_input, table, hand, expected_card', [
        # find 'AS' only if first 'PASS' is ignored
        (('PASS', 'AS'), Table(), [Card('A', 'Spades', True)], Card('A', 'Spades', True)),
        # player's hand does not really matter here at all
        (('PASS',), 'table_and_card', [Card('A', 'Clubs', False)], None),
        # 2nd block
        (('AS',), Table(), [Card('A', 'Spades', True)], Card('A', 'Spades', True)),
        (('6H', 'PASS'), 'table_and_card', [Card('6', 'Hearts', False)], None),
        (('AC',), 'table_and_card', [Card('A', 'Clubs', False)], Card('A', 'Clubs', False)),
        # 3rd block
        (('not a card', '**99077', '', '  ',  'PASS'), 'table_and_card', [Card('A', 'Clubs', False)], None),
        (('AC', 'PASS'), 'table_and_card', [Card('6', 'Hearts', False)], None),
    ])
    def test_attack(self, user_input, table, hand, expected_card, request):
        """
        1. User sends 'PASS'
            1.1. NO cards on a table (Table is empty).
            1.2. There are cards on a table.
        2. Specified card was found.
            2.1. Table is empty.
            2.2. Table is NOT empty. NO cards with the same rank on a table.
            2.3. Table is NOT empty. Cards with the same rank are on a table.
        3. Specified card NOT found.
            3.1. Not a card (just random string) + empty sting (input).
            3.2. A card suitable for the attack, but is NOT in player's hand.
        """
        initial_cards_num = len(hand)

        try:
            table, _ = request.getfixturevalue(table)
        except _pytest.fixtures.FixtureLookupError:
            table = table

        player_names = 'ATTACKER', 'DEFENDER'

        with mock.patch('player.input', side_effect=player_names):
            attacker, defender = [Player() for _ in player_names]
            attacker.hand = hand

        with mock.patch('player.input', side_effect=user_input):
            attack_card = attacker.attack(table, defender)

        assert attack_card == expected_card \
            if expected_card is not None else attack_card is expected_card, \
            'Chosen a wrong card to attack!'

        if attack_card is not None:
            assert (attack_card not in attacker.hand) and (len(attacker.hand) == initial_cards_num - 1), \
                'Attack card should be removed from attacker\'s hand!'
        else:
            assert len(attacker.hand) == initial_cards_num, \
                'No cards should be removed from attacker\'s hand!'

    @pytest.mark.parametrize('user_input, attack_card, hand, expected_card', [
        # block 1
        # player send 'PASS' attack_card and hand does not matter
        (('PASS',), Card('6', 'Spades', True), [Card('A', 'Spades', True)], None),
        # block 2
        (('AS',), Card('6', 'Spades', True), [Card('A', 'Spades', True)], Card('A', 'Spades', True)),
        (('6S', 'PASS'), Card('A', 'Spades', True), [Card('6', 'Spades', True)], None),
        # block 3
        (('not a card', '**99077', '', '  ',  'PASS'), Card('A', 'Spades', True), [Card('6', 'Spades', True)], None),
        (('AS', 'PASS'), Card('6', 'Spades', True), [Card('A', 'Clubs', False)], None),
    ])
    def test_defend(self, user_input, attack_card, hand, expected_card):
        """
        1. User sends 'PASS' -> None.
            1.1. 'PASS'
        2. Specified card was found.
            2.1. Card is greater than attack card.
            2.2. Card is NOT greater than attack card.
        3. Specified card NOT found.
            3.1. Not a card (just random string) + empty sting (input).
            3.2. A card suitable for the attack, but is NOT in player's hand.
        """
        initial_cards_num = len(hand)

        with mock.patch('player.input', return_value='DEFENDER'):
            defender = Player()
            defender.hand = hand

        with mock.patch('player.input', side_effect=user_input):
            defend_card = defender.defend(attack_card)

        assert defend_card == expected_card \
            if expected_card is not None else defend_card is expected_card, \
            'Chosen a wrong card to defend!'

        if defend_card is not None:
            assert (defend_card not in defender.hand) and (len(defender.hand) == initial_cards_num - 1), \
                'Defend card should be removed from defender\'s hand!'
        else:
            assert len(defender.hand) == initial_cards_num, \
                'No cards should be removed from defender\'s hand!'

    @pytest.mark.parametrize('user_input, table, hand, max_cards_num, expected_cards', [
        (('PASS',), ('6H', '9H', '6S'), ['7S', 'AH'], 2, []),
        (('PASS',), ('6H', '9H', '6S'), ['7S', 'AH'], 2, []),
        # 2
        (('6C 6D 9S', '6C'), ('6H', '9H', '6S'), ['6C', '6D', '9S'], 1, ['6C']),
        # 3
        (('', '   ', 'PASS'), ('6H',), ['AS'], 1, []),
        # 4.1.1.
        (('%6^334i', '11S', '5H', 'SJ', 'J7', 'PASS'), ('6H',), ['AS'], 1, []),
        # 4.1.2. (fist input will be accepted, no need for any following ones.
        (('6C 6C 9C', '9C 6C 9C', '9C 9C', '6C 9C'), ('6H', '9H', '6S'), ['6C', '9C'], 3, ['6C', '9C']),
        # 4.2.1.
        (('6C AS', '6C'), ('6H', '9H', '6S'), ['6C', 'AS'], 3, ['6C']),
    ])
    def test_throw_cards(self, user_input, table, hand, max_cards_num, expected_cards):
        """
        1. PASS.
        2. Num of cards is greater than it should be.
        3. Empty input.
        4. Correct number of cards.
            4.1. At least one of specified cards NOT found in player's hand.
                4.1.1. Non-existing cards also fall into this case.
                4.1.2. Player specified the same card (that he has) twice!
            4.2. All cards were found.
                4.2.1. Check that card can be thrown (card of the same rank
                    on a table).

        Check that cards were removed from player's hand.
        Check that correct cards were returned.
        """
        trump = 'Spades'
        hand = [Card.convert(card, trump) for card in hand]
        _table = Table()
        [_table.add_card(Card.convert(card, trump)) for card in table]
        expected = {Card.convert(card, trump) for card in expected_cards}

        cards_in_hand = len(hand)

        with mock.patch('player.input', return_value='PLAYER'):
            player = Player()
            player.hand = hand

        with mock.patch('player.input', side_effect=user_input):
            thrown_cards = player.throw_cards(_table, max_cards_num)

        correct_input = user_input[-1]
        cards_num = len(correct_input.split()) if correct_input != 'PASS' else 0

        assert set(thrown_cards) == expected, 'Wrong cards were thrown!'
        assert len(thrown_cards) == len(expected), 'Wrong number of thrown cards!'
        assert len(player.hand) == cards_in_hand - cards_num, 'Wrong number of cards in a player\'s hand!'
