import math
import random

from card import Card
from config import CONFIG
from drawable import Deck, Table
from mixins import CardGameMixin
from player import Player


# TODO: write a thorough game description


class FoolCardGame:
    def __init__(self, cards_to_have: int = 6, max_attacks: int = 6) -> None:
        """
        TODO: also write all terminology in here.
        :param cards_to_have: minimum number of cards players need to have in
        the beginning of each round.
        :param max_attacks: max number of attack that defender need to endure.
        """
        # player-related block
        self.PLAYERS_NUM = CONFIG['PLAYERS_NUM']
        self.players = [Player() for _ in range(self.PLAYERS_NUM)]
        # randomize an order of players
        random.shuffle(self.players)
        # players who finished the game and waiting it finishes
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
        self.first_attacker = self._find_first_attacker()
        # in the beginning of each round the first attacker always has index 0, defender - 1
        first_attacker_index = self.players.index(self.first_attacker)
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

        # start game
        # TODO: think about -- self._greet_players()
        self._send_instructions()

    def _take_cards(self) -> None:
        """
        All players take cards from a deck to have required (CARDS_TO_HAVE)
        number of cards. The attacker (a player who started the round with
        an attack) is the first player who takes cards, the defender is the
        last one. For instance, players are sitting around a circle table in
        the following order (from left to right): A (attacker) -> D (defender)
        -> P3 (player3) -> P4 (player4). Then players take cards in the following
        manner: A -> P3 -> P4 -> D. Attacker is a player who always has an index
        equals to 0 in the self.players list, while defender always has an index
        equals to 1 (A -> D -> P3 -> P4[ -> ... -> P6]).
        """
        players_num = len(self.players)
        # round should not start if players_num < 2,
        # thus it's guaranteed that no IndexError occur
        for player_index in (0, *range(2, players_num), 1):
            player = self.players[player_index]
            if len(player) < self.CARDS_TO_HAVE:
                need_cards = self.CARDS_TO_HAVE - len(player)
                player.take_cards(self.deck, need_cards)

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

    @staticmethod
    def _send_instructions():
        """Send instructions to all players"""
        # TODO: write complete instructions message
        instructions = """
---------------------------------------------------------------------------------------
                                     GAME INSTRUCTIONS
---------------------------------------------------------------------------------------
1. ...
2. ...
3. ...
   ...
---------------------------------------------------------------------------------------
"""
        print(instructions)

    def _throw_cards(self, attackers: list[Player], defender: Player, max_attacks: int) -> None:
        """If defender lost the round (end of a round), all other players can give
        him more cards, with ranks same as ranks of cards on the table (THROW PHASE).
        if the first attacker (in the round) cannot give more cards and defender took
        less than max_attacks cards, other players (attackers) can give more cards to
        defender. THROW PHASE is finished when either: 1) card limit is reached or 2)
        attackers do not want to or have no cards to continue."""

        print(f'THROW PHASE: ALL PLAYERS CAN GIVE ADDITIONAL CARDS TO THE DEFENDER {defender.name}.')
        attack_num = math.ceil(len(self.table) / 2)

        for attacker in attackers:
            if attack_num < max_attacks:
                # max cards number to add to defender
                max_cards_num = max_attacks - attack_num
                thrown_cards = attacker.throw_cards(self.table, max_cards_num)
                [self.table.add_card(card) for card in thrown_cards]
                attack_num += len(thrown_cards)
            else:
                break

    def _remove_watchers(self):
        """Exclude players who finished game from 'players' list.
        Add those players to the list of watchers. This method is
        supposed to be called after _take_cards method to remove
        players who still do not have cards after an attempt to
        replenish hand."""
        players = []

        for player in self.players:
            players.append(player) if player else self.watchers.append(player)

        self.players = players

    def _reassign_roles(self):
        """Reorder players in the end of the round according to if defender lost it or won."""
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
        """
        TODO: change doc-string
        End of round conditions:
        1. Defender could not defend.
        2. Defender has no cards to continue.
        3. Last attacker has no cards to continue.
        4. Attackers do not want to attack (all send pass).
        """
        # TODO: if debug = True
        print(f'A trump suit is: {self.TRUMP}.')
        print(f'Number of cards in the deck is {len(self.deck)}.')

        for player in self.players:
            print(player)

        # restore from the prev round
        self._skip_turn = False
        self.round += 1
        attack_num = 0
        attackers = [p for p in self.players if self.players.index(p) != 1]
        defender = self.players[1]
        # number of attack cannot exceed an initial number of cards in defender's hand
        max_attacks = min(self.MAX_ATTACKS, len(defender))
        continue_round: bool = True

        for attacker in attackers:
            while continue_round and attack_num < max_attacks:
                attack_card = attacker.attack(self.table, defender)

                if attack_card:
                    self.table.add_card(attack_card)
                    attack_num += 1
                    defend_card = defender.defend(attack_card)

                    if defend_card:
                        self.table.add_card(defend_card)
                    # defender cannot defend
                    else:
                        # other players can give cards to the defender
                        self._throw_cards(attackers, defender, max_attacks)
                        defender.take_cards(self.table, len(self.table))
                        self._skip_turn = True
                        continue_round = False
                # attacker cannot attack
                else:
                    break

            else:
                break

        print(f'Defender ({defender.name}) lost the round and won\'t attack in the next one.'
              if self._skip_turn else
              f'Defender ({defender.name}) endured the attack, and will attack in the next one.')

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
        return self.__fool

    def play(self):
        while True:
            self._play_round()

            # TODO: match/case
            players_left = len(self.players)

            if players_left < 2:
                if players_left == 1:
                    self.__fool = self.players[0]
                break

        print(f'Game is over, {self.fool.name} is a fool!'
              if self.fool else
              'Congratulations! Nobody is a fool!')
