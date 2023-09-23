import itertools as it
import math
import random

from card import Card
from config import CONFIG
from drawable import Deck, Table
from mixins import CardGameMixin
from player import Player
from server import Server


class FoolCardGame:
    def __init__(self, server: Server, cards_to_have: int = 6, max_attacks: int = 6) -> None:
        """
        :param cards_to_have: minimum number of cards players need to have in
        the beginning of each round (if there are cards in a deck still).
        :param max_attacks: max number of attack that defender need to endure.
        """
        # player-related block
        self.PLAYERS_NUM = CONFIG['PLAYERS_NUM']
        self.players: list[Player] = []

        # accept expected number of players
        while len(self.players) < self.PLAYERS_NUM:
            player_socket, player_address = server.sock.accept()
            player = Player(player_socket)
            self.players.append(player)
            player.send(f'Hi {player.name}, have a nice game and good luck! '
                        f'Game will start soon. Waiting for other players.\n')

        # randomize an order of players
        random.shuffle(self.players)
        # players who finished the game and waiting it ends
        self.watchers = []

        # deck-related part
        # choose a trump suit
        self.TRUMP = random.choice(CardGameMixin.SUITS)
        # prepare deck
        self.deck = Deck(self.TRUMP)
        self.deck.shuffle()

        # players take cards
        self.CARDS_TO_HAVE = cards_to_have
        self._take_cards()

        # TODO: remove rearrangement -> change roles with index
        self._first_attacker = self._find_first_attacker()
        # a player with index 0 is the first attacker in a round
        first_attacker_index = self.players.index(self._first_attacker)
        self.players = (self.players[first_attacker_index:] +
                        self.players[:first_attacker_index])

        # other settings
        self.MAX_ATTACKS = max_attacks
        self.table = Table()
        self.round = 0
        # if current defender will not be an attacker in the next round
        self._skip_turn = False
        # a player who lost game
        self.__fool = None

        # TODO: centralize text automatically
        self._send_all(
            f'==========================================================================================\n'
            f'                                        GAME RULES                                        \n'
            f'==========================================================================================\n'
            f'1. ...                                                                                    \n'
            f'2. ...                                                                                    \n'
            f'3. ...                                                                                    \n'
            f'   ...                                                                                    \n'
            f'------------------------------------------------------------------------------------------\n'
        )

    def _send_all(self, msg: str):
        """Send a message to all players and watchers"""
        [player.send(msg) for player in it.chain(self.players, self.watchers)]

    def _take_cards(self) -> None:
        """
        All players take cards from a deck to have required (CARDS_TO_HAVE)
        number of cards.

        The first attacker (a player who starts a round with an attack) is
        the first player who takes cards, the defender is the last one."""

        players_num = len(self.players)
        # Round should not start if players_num < 2, thus it is guaranteed
        # that no IndexError occur.
        # Players with indices 0 and 1 are the first attacker and defender,
        # respectively
        for player_index in (0, *range(2, players_num), 1):
            player = self.players[player_index]
            if len(player) < self.CARDS_TO_HAVE:
                cards_num = self.CARDS_TO_HAVE - len(player)
                player.take_cards(self.deck, cards_num)

    def _find_first_attacker(self) -> Player:
        """The first attacker is a player who will start the first attack
        in an entire game. Will be determined based on the smallest trump
        card among all players. if None of players have trump cards, then
        the first attacker will be set randomly."""

        first_attacker: Player | None = None
        smallest_trump: Card | None = None

        for player in self.players:
            for card in player.hand:
                if card.trump and ((smallest_trump is None)
                                   or (card < smallest_trump)):
                    smallest_trump = card
                    first_attacker = player

        # None of players have trump cards
        if first_attacker is None:
            first_attacker = random.choice(self.players)

        return first_attacker

    def _throw_cards(self, attackers: list[Player], defender: Player, max_attacks: int) -> None:
        """If defender lost a round, all other players can give (throw) him
        cards, with ranks same as ranks of cards on the table (THROW PHASE).

        if the first attacker in a round cannot throw more cards and defender
        took less than max_attacks cards, other players (attackers) can give
        cards to the defender.

        THROW PHASE is finished when either: 1) a set limit is reached or 2)
        attackers do not want to or 3) have no cards to continue."""

        self._send_all(
            f'------------------------------------------------------------------------------------------\n'
            f'                THROW PHASE: Players can give cards to {defender.name}.                   \n'
            f'------------------------------------------------------------------------------------------\n'
        )
        attack_num = math.ceil(len(self.table) / 2)

        for attacker in attackers:
            if attack_num < max_attacks:
                # max cards number to throw
                max_cards_num = max_attacks - attack_num
                thrown_cards = attacker.throw_cards(self.table, max_cards_num)

                if thrown_cards:
                    # TODO: iterate over the same list of cards twice! optimize
                    self._send_all(
                        f'{attacker.name} has thrown {len(thrown_cards)} card(s): '
                        f'{", ".join(str(card) for card in thrown_cards)}.\n')
                    [self.table.add_card(card) for card in thrown_cards]
                    attack_num += len(thrown_cards)
                else:
                    attacker.send(
                        # TODO: same msg for att and def
                        f'{attacker.name} does not want to or '
                        f'have no suitable cards to throw.\n')
            else:
                break

    def _remove_watchers(self):
        """Exclude players who finished game from players.

        Add these excluded players to the list of watchers. The method removes
        players who have no cards after an attempt to replenish hand (deck is
        empty)."""
        players = []

        for player in self.players:
            players.append(player) if player else self.watchers.append(player)

        self.players = players

    def _reassign_roles(self):
        """Reassign the first attacker and defender roles among players."""
        if len(self.players) > 1:
            # defender lost round
            if self._skip_turn:
                # both attacker and defender are placed in the end of 'players' list
                self.players = self.players[2:] + self.players[:2]
            else:
                # only an initial attacker goes in the end of 'players' list,
                # defender will be the first attacker in the next round
                self.players = self.players[1:] + self.players[:1]

    def _play_round(self):
        """Play a single round of a game.

        General round procedure:
        The first attacker attack a defender with a card. The defender needs
        to find a suitable card to defend. If the defender finds such a card,
        the attacker can attack the defender with another (suitable) card. If
        defender could beat all cards from the attacker, the next player in a
        row becomes an attacker and can attack the defender with his cards. If
        at some moment during a round, the defender cannot beat an attack card,
        other players can throw him additional cards.

        End of round conditions:
        1. Defender could not defend. A defend card needs to be greater than
        the attack one.
        2. Defender has no cards to continue or the limit of cards to attack
        the defender is reached.
        3. The last attacker has no cards to continue.
        4. Attackers do not want to attack (all send pass)."""

        # restore from the prev round
        self._skip_turn = False
        self.round += 1
        attack_num = 0
        attackers = [p for p in self.players if self.players.index(p) != 1]
        defender = self.players[1]
        # num of attack cannot exceed an initial num of cards in defender's hand
        max_attacks = min(self.MAX_ATTACKS, len(defender))
        continue_round: bool = True

        self._send_all(
            f'------------------------------------------------------------------------------------------\n'
            f'                                       ROUND {self.round}                                 \n'
            f'------------------------------------------------------------------------------------------\n'
            f'TRUMP SUIT: {self.TRUMP}.                                                                 \n'
            f'CARDS IN THE DECK: {len(self.deck)}.                                                      \n'
            f'PLAYERS: {", ".join(player.name for player in self.players)}.                             \n'
            f'FIRST ATTACKER: {attackers[0]}.                                                           \n'
            f'DEFENDER: {defender}.                                                                     \n'
            f'------------------------------------------------------------------------------------------\n'
        )

        for attacker in attackers:
            while continue_round and attack_num < max_attacks:
                self._send_all(
                    f'CURRENT ATTACKER: {attacker.name}.\n'
                    f'CARDS ON THE TABLE: {self.table!s}.\n' if self.table else 'TABLE IS EMPTY.\n'
                )

                attack_card = attacker.attack(self.table, defender)
                if attack_card:
                    self.table.add_card(attack_card)
                    attack_num += 1

                    defend_card = defender.defend(attack_card)
                    if defend_card:
                        self.table.add_card(defend_card)
                    # defender cannot defend
                    else:
                        # # TODO: for att and def same msg -> define var!
                        self._send_all(f'{defender.name} does not want to '
                                       f'or have no suitable cards to defend.')
                        # other players can give cards to the defender
                        self._throw_cards(attackers, defender, max_attacks)
                        defender.take_cards(self.table, len(self.table))
                        self._skip_turn = True
                        continue_round = False
                # attacker cannot attack
                else:
                    self._send_all(f'{attacker.name} does not want to '
                                   f'or have no suitable cards to attack.')
                    break

            else:
                break

        self._send_all(
            f'{defender.name} LOST THE ROUND AND WON\'T ATTACK IN THE NEXT ONE.\n'
            if self._skip_turn else
            f'{defender.name} HAS REPELLED THE ATTACK, AND WILL ATTACK IN THE NEXT ROUND.\n'
        )

        # move beaten cards from the table to the trash
        self.table.clear()
        # players take cards from the deck to have required number of cards
        self._take_cards()
        # rearrange players for the next round
        self._reassign_roles()
        # only leave players who have cards
        self._remove_watchers()

    @property
    def fool(self):
        """A player who lost the game."""
        return self.__fool

    def play(self):
        """Play an entire game from the beginning till the end."""
        while True:
            self._play_round()

            # TODO: match/case
            players_left = len(self.players)

            if players_left < 2:
                if players_left == 1:
                    self.__fool = self.players[0]
                break

        self._send_all(
            f'GAME IS OVER, {"NOBODY" if self.fool is None else self.fool.name} IS A FOOL!\n'
        )
