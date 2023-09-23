from __future__ import annotations
import re
import socket

from card import Card
from drawable import Deck, Table


# TODO: if user type ^D -> raises EOFError: EOF when reading a line. Handle this case!


class Player:
    LOW, HIGH = 3, 20
    RE_NAME = re.compile(fr'\w{{{LOW},{HIGH}}}')

    def __init__(self, sock: socket.socket) -> None:
        self.sock = sock
        # set player's name
        self.send(
            f'\n\n'
            f'==========================================================================================\n'
            f'                              WELCOME TO A \'FOOL\' CARD GAME!                            \n'
            f'==========================================================================================\n'
            f'                   Hi player, you are on a \'FOOL\' card game server!                     \n'
            f'                   To join a game, you need to enter your name below.                     \n'
            f'------------------------------------------------------------------------------------------\n'
            f'                                    NAME CONSTRAINS:                                      \n'
            f'1) Name must be between {self.LOW} and {self.HIGH} characters (including both ends).      \n'
            f'2) Allowed symbols: upper/lower ascii chars (a-zA-Z), digits (0-9), underscore (_).       \n'
            f'3) No spaces are allowed!                                                                 \n'
            f'------------------------------------------------------------------------------------------\n'
            f'\n'
        )

        # ask a player to send his name until a suitable name is provided
        # TODO: number of attempts -> disconnect
        while True:
            self.send(b'Please enter your name: ')

            # validate unicode
            try:
                # telnet adds '\r\n' at the end of each message, user also might add spaces
                player_name = self.sock.recv(1024).decode(encoding='utf-8').strip()
            except UnicodeDecodeError:
                self.send(b'Wrong input. An input must contain '
                          b'only unicode characters. Try again.\n')
            else:
                # TODO: log user attempts
                # validate name
                if self.RE_NAME.fullmatch(player_name):
                    self.name = player_name
                    break
                else:
                    self.send(b'Wrong name entered. Try again.\n')

        # player's cards
        # TODO: store cards in a more organized way (dict)
        self.hand = []

    # TODO: bytearray?
    def send(self, msg: bytes | str, encoding: str = 'utf-8') -> None:
        """Send a message to a player over tcp protocol"""
        self.sock.send(msg if type(msg) is bytes else msg.encode(encoding=encoding))

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
            self.send(
                f'{self.name}, choose a card to attack {defender.name}.\n'
                f'Your cards: {", ".join(str(card) for card in self.hand)}.\n'
                f'Enter a card or send \'PASS\' (PASS is NOT allowed when table is empty): '
            )
            user_input = self.sock.recv(1024).decode(encoding='utf-8').strip().upper()

            # player does not want to or have no suitable card to attack
            if user_input == 'PASS':
                # there are cards on the table (table is not empty)
                if table:
                    break
                # first attack in the round
                else:
                    self.send('You cannot \'PASS\' when there are '
                              'no cards on the table. Try again.\n')
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
                    self.send(f'No cards with rank {potential_card.rank} '
                              f'on the table. Try again.\n')
            else:
                self.send('Specified card not found. Try again.\n')

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

        while self:
            # ask player to choose a card
            self.send(
                f'{self.name}, choose a card to defend from {attack_card!s}.\n'
                f'Your cards: {", ".join(str(card) for card in self.hand)}.\n'
                f'Enter a card or send \'PASS\': '
            )
            user_input = self.sock.recv(1024).decode(encoding='utf-8').strip().upper()

            if user_input == 'PASS':
                break

            potential_card = self.find_card(user_input)
            if potential_card:
                if potential_card > attack_card:
                    self.hand.remove(potential_card)
                    defend_card = potential_card
                    break
                else:
                    self.send(
                        f'Card {potential_card!s} is not greater than '
                        f'the attack card {attack_card!s}. Try again.\n')
            else:
                self.send(f'Specified card not found. Try again.\n')

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
            # TODO: add defender name here (to signature as well)?
            self.send(
                f'{self.name}, choose at most {max_cards_num} cards to throw.\n'
                f'Cards on the table: {table}.\n'
                f'Your cards: {", ".join(str(card) for card in self.hand)}.\n'
                f'Enter cards (separated by spaces) or send \'PASS\': '
            )
            user_input = self.sock.recv(1024).decode(encoding='utf-8').strip().upper()

            if user_input == 'PASS':
                break
            else:
                # remove duplicates if exist
                user_input = set(user_input.split())

                if len(user_input) > max_cards_num:
                    self.send(f'Number of cards thrown cannot exceed '
                              f'{max_cards_num}. Try again.')
                # empty input
                elif not user_input:
                    self.send(
                        'Send \'PASS\' if you do not want to or have '
                        'not suitable cards to throw. Try again.')
                # proper number of cards
                else:
                    for card in user_input:
                        player_card = self.find_card(card)

                        if player_card:
                            if player_card.rank in table.card_ranks:
                                cards.append(player_card)
                            else:
                                self.send(
                                    f'No cards with rank {player_card.rank} '
                                    f'on the table. Try again.\n')
                                break
                        else:
                            self.send(
                                f'At least one of the specified '
                                f'cards not found. Try again.')
                            break
                    # valid user input (all cards found in player's hand)
                    else:
                        for player_card in cards:
                            self.hand.remove(player_card)
                        # only one correct input from a player is allowed
                        break

        return cards
