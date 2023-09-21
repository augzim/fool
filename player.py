from __future__ import annotations
import re

from card import Card
from drawable import Deck, Table


# TODO: check and fix all doc-strings
# TODO: if user type ^D -> raises EOFError: EOF when reading a line. Handle this case!


class Player:
    RE_NAME = re.compile(r'\w{3,20}')

    def __init__(self) -> None:
        # ask a player to send his name until a suitable name is provided
        # TODO: no duplicate names
        while True:
            username = input('Please enter your name: ').strip()
            # handle username
            if self.RE_NAME.fullmatch(username):
                self.name = username
                break

        self.greet_player()
        # player's cards
        # TODO: store cards in a more organized way (dict)
        self.hand = []

    # TODO: think if transfer this method to the class Game
    def greet_player(self) -> None:
        """Greet player"""
        print(f'Hi, {self.name}, have a nice game and good luck!\n')

    def find_card(self, card: Card | str) -> Card | None:
        """Try to find a specified card in a player's hand"""
        for c in self.hand:
            if c == card:
                return c

    def __len__(self):
        """Display a number of cards in a player's hand"""
        return len(self.hand)

    def __bool__(self):
        """Say if player has cards"""
        return bool(self.hand)

    def __repr__(self):
        """Display cards in a player's hand"""
        cls_name = self.__class__.__name__
        return f'{cls_name}{self.hand}'

    def __str__(self):
        """Display cards in a player's hand"""
        return f'{self.name} [{", ".join(str(card) for card in self.hand)}]'

    # TODO: fix signature, define ABC Drawable instead of from_: Deck | Table,
    def take_cards(self, from_: Deck | Table, /, num: int) -> None:
        """Take specified number of cards from a deck or all cards from table"""
        self.hand += from_.draw(num)
        # TODO: sort cards in a player's hand

    def attack(self, table: Table, defender: Player) -> Card | None:
        """Ask a player to choose a card to attack another player (defender).

        Player should send a card in a format 'RS' (R - rank and S - suit).

        Possible attacker's options:
        1. Attacker has no cards at all (do not ask player -> auto-reply) ->
        return None. In real game it's obvious to other players when a player
        does not have cards, thus no need to ask a player and loose time.
        2. Attacker has no suitable cards (should send 'PASS') -> return None.
        It's more realistic if a player explicitly sends 'PASS', even though a
        program can act for him in this situation.
        3. Attacker has suitable cards, but does not want to attack (attacker
        sent 'PASS') -> return None.
        4. Attacker has a suitable card and want to attack -> Card.

        Attack restrictions:
        1. In the first subround (empty table) attacker cannot choose a 'PASS'
        option."""

        attack_card = None

        # attacker has no cards -> None
        while self:
            # ask player to choose a card
            # TODO: add addressing to player for each message! Make them more personal!
            user_input = input(f'{self.name}, choose a card'
                               f' to attack {defender.name}: ').strip().upper()

            # player does not want to or have no suitable card to attack
            if user_input == 'PASS':
                # there are cards on the table (table is not empty)
                if table:
                    print(f'{self.name} does not want to or have no suitable cards to attack.')
                    break
                # first attack in the round
                else:
                    print('You cannot \'PASS\' when there are no cards on the table. Try again.')
                    continue

            potential_card = self.find_card(user_input)
            if potential_card:
                # either table is empty or there are cards on the table with the same rank
                # TODO: not table.card_ranks -> not table
                if (not table.card_ranks) or (potential_card.rank in table.card_ranks):
                    self.hand.remove(potential_card)
                    attack_card = potential_card
                    break
                else:
                    print(f'No cards with rank {potential_card.rank} on a table. Try again.\n')
            else:
                print('Specified card not found. Try again.\n')

        return attack_card

    def defend(self, attack_card: Card) -> Card | None:
        """Ask a player to choose a card to defend from an attack card.

        Player should send a card in a format 'RS' (R - rank and S - suit).

        Possible defender's options:
        1. Defender has no cards at all. Game does not ask player to defend,
        if he does not have cards, since number of cards in defender's hand
        is determined in the beginning of a round, thus players cannot give
        him more cards than he has. Moreover, empty players are stop playing.
        2. Defender has no suitable cards (should send 'PASS') -> None. It's
        more realistic if a player explicitly sends 'PASS', even though the
        program can act for him in this situation.
        3. Defender has suitable cards, but does not want to defend (defender
        sent 'PASS') -> return None.
        4. Defender has a suitable card and want to defend -> Card."""

        defend_card = None

        # TODO: change True for self for consistency (with attack and throw)
        while True:
            # ask player to choose a card
            user_input = input(f'{self.name}, choose a card to defend: ').strip().upper()

            if user_input == 'PASS':
                print(f'{self.name} does not want to or have no suitable cards to defend.')
                break

            potential_card = self.find_card(user_input)
            if potential_card:
                if potential_card > attack_card:
                    self.hand.remove(potential_card)
                    defend_card = potential_card
                    break
                else:
                    print(f'Card {potential_card!s} is not greater than '
                          f'the attack card {attack_card!s}. Try again.\n')
            else:
                print(f'Specified card not found. Try again.\n')

        return defend_card

    def throw_cards(self, table: Table, max_cards_num: int) -> list[Card]:
        """Ask a player to throw cards to defender who lost the round. Only
        cards of the same ranks as cards on a table can be thrown.

        Player can send up to max_cards_num cards in 'RS' format, where R -
        rank and S - suit. Cards need to be separated by spaces.

        Possible player's options:
        1. Player has no cards at all (do not ask a player -> auto-reply) ->
        return None.
        2. Player has no suitable cards (should send 'PASS') -> []. It is more
        realistic if a player explicitly sends 'PASS', even though the program
        can act for him in this situation.
        3. Player has suitable cards, but does not want to throw (player sent
        'PASS') -> [].
        4. Player has a suitable card and want to throw them -> list[Card]."""

        cards = []

        while self:
            # start each input from scratch
            cards.clear()
            # player should specify all cards at once
            user_input = input(f'Please enter at most {max_cards_num} cards to '
                               f'throw (separated by spaces): ').strip().upper()

            if user_input == 'PASS':
                print(f'{self.name} does not want to or have no suitable cards to throw.')
                break
            else:
                # remove duplicates if exist
                user_input = set(user_input.split())

                if len(user_input) > max_cards_num:
                    print(f'Number of cards thrown cannot exceed {max_cards_num}. Try again.')
                # empty input
                elif not user_input:
                    print('Send \'PASS\' if you do not to or have '
                          'not suitable cards to throw. Try again.')
                    continue
                # proper number of cards
                else:
                    for card in user_input:
                        player_card = self.find_card(card)

                        if player_card:
                            if player_card.rank in table.card_ranks:
                                cards.append(player_card)
                            else:
                                print(f'No cards with rank {player_card.rank} '
                                      f'on a table. Try again.\n')
                                break
                        else:
                            print(f'Specified card {player_card!s} not found. Try again.')
                            break
                    # valid user input (all cards found in player's hand)
                    else:
                        print(f'{self.name} has thrown {len(cards)} cards: '
                              f'{", ".join(str(card) for card in cards)}.')

                        for player_card in cards:
                            self.hand.remove(player_card)
                        # only one correct input from a player is allowed
                        break

        return cards
