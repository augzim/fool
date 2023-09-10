from __future__ import annotations
import re

from card import Card
from drawable import Deck, Table


# TODO: check and fix all doc-strings
# TODO: if user type ^D -> raises EOFError: EOF when reading a line. Handle this case!


class Player:
    RE_NAME = re.compile(r'\w{3,20}')

    def __init__(self) -> None:
        # ask a client to send his name until a suitable name is provided
        # TODO: no duplicate names
        while True:
            username = input('Please enter your name: ').strip()
            # handle username
            if self.RE_NAME.fullmatch(username):
                self.name = username
                break

        self.greet_player()
        # player's cards
        self.hand = []

    # TODO: think if transfer this method to the class Game
    def greet_player(self) -> None:
        """Greet player"""
        print(f'Hi, {self.name}, have a nice game and good luck!\n')

    def find_card(self, card: str) -> Card | None:
        """Try to find a specified card in a player's hand."""
        for c in self.hand:
            if c.is_identical(card):
                return c

    def __len__(self):
        """Display the number of cards in a player's hand"""
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
        # Deck and Table classes have draw method for this purpose
        self.hand += from_.draw(num)
        # sort cards in hand every time a player takes cards
        # TODO: add some sorting

    def attack(self, table: Table, defender: Player) -> Card | None:
        """
        Card should be sent by a player in a format 'VS', where V - value and S - suit.

        Possible attacker's behaviour options:
        1. Attacker has no cards at all (does not ask player -> auto-reply) -> return None.
            In real game it's obvious to other players when a player does not have cards,
            thus no need to ask the player at all and loose time.
        2. Attacker has no suitable cards   (attacker sent 'PASS') -> return None.
            It's more realistic if a player explicitly sends 'PASS', even though a
            program can act for him in this situation.
        3. Attacker does not want to attack (attacker sent 'PASS') -> return None.
        4. Attacker has a suitable card and want to attack -> Card.

        Attack restrictions:
        1. In the first subround (empty table) attacker cannot choose a 'PASS' option.
        """
        attack_card = None

        # if attacker has no cards return None
        while self:
            # ask player to choose a card
            # TODO: add addressing to player for each message! Make them more personal!
            user_input = input(f'{self.name}, choose a card to attack {defender.name}: ').strip().upper()

            # player does not want to or have no suitable card to attack
            if user_input == 'PASS':
                # there are cards on the table (table is not empty, first attack in the round)
                if table:
                    break
                else:
                    print('You cannot PASS when there are no cards on the table. Try again.')
                    continue

            potential_card = self.find_card(user_input)
            if potential_card:
                # either table is empty or there are cards on the table with the same value
                if (not table.card_values) or (potential_card.value in table.card_values):
                    self.hand.remove(potential_card)
                    attack_card = potential_card
                    break
                else:
                    print('No cards of the same value on the table. Try again.\n')
            else:
                print('Specified card not found. Try again.\n')

        return attack_card

    def defend(self, attack_card: Card) -> Card | None:
        """Choose Defend from an attack card"""
        defend_card = None

        # TODO: change True for self for consistency (with attack and throw)
        while True:
            # ask player to choose a card
            user_input = input(f'{self.name}, choose a card to defend: ').strip().upper()

            # player does not want to or have no suitable card to defend
            if user_input == 'PASS':
                break

            potential_card = self.find_card(user_input)
            if potential_card:
                if potential_card > attack_card:
                    self.hand.remove(potential_card)
                    defend_card = potential_card
                    break
                else:
                    print(f'A card must be greater than the attack card {attack_card!s}. Try again.\n')
            else:
                print('Specified card not found. Try again.\n')

        return defend_card

    def throw_cards(self, table: Table, max_cards_num: int) -> None:
        """Throw additional cards to defender who lost the round. Only card of
        the same values as cards on the table can be thrown to the defender."""

        print(f'{self.name}, you can throw at most {max_cards_num} cards if '
              f'you want. If you do not want to throw cards, send \'PASS\'.')

        while self:
            cards = []
            # player should specify all cards at once
            user_input = input(f'Please enter at most {max_cards_num} cards,'
                               f' separated by spaces: ').strip().upper()

            if user_input == 'PASS':
                print(f'{self.name} does not want to or have no suitable cards to throw.')
                break
            else:
                user_cards = user_input.split()

                if len(user_cards) > max_cards_num:
                    print(f'Number of cards thrown cannot exceed {max_cards_num}. Try again.')
                elif not user_cards:
                    continue
                # proper number of cards
                else:
                    for card in user_cards:
                        player_card = self.find_card(card)

                        if player_card:
                            cards.append(player_card)
                        else:
                            print(f'Specified cards not found. Try again.')
                            break
                    # valid user input (all cards found in player's hand)
                    else:
                        print(f'{self.name} has thrown {len(cards)} cards: '
                              f'{", ".join(str(card) for card in cards)}.')

                        for player_card in cards:
                            self.hand.remove(player_card)
                            table.add_card(player_card)
                        # only one correct input from a player is allowed
                        break
