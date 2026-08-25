from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations
import random


RANKS = ("2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A")
SUITS = ("Hearts", "Diamonds", "Clubs", "Spades")
RANK_VALUES = {rank: index + 2 for index, rank in enumerate(RANKS)}

STREETS = ("IDLE", "PREFLOP", "FLOP", "TURN", "RIVER", "SHOWDOWN", "HAND_OVER")


@dataclass(frozen=True)
class Card:
    rank: str
    suit: str

    @property
    def value(self) -> int:
        return RANK_VALUES[self.rank]

    def __str__(self) -> str:
        return f"{self.rank} {self.suit[0]}"


@dataclass(frozen=True, order=True)
class HandScore:
    category: int
    tiebreakers: tuple[int, ...]
    name: str = field(compare=False)
    cards: tuple[Card, ...] = field(compare=False, default_factory=tuple)


@dataclass
class PlayerState:
    name: str
    stack: int
    is_bot: bool = False
    hand: list[Card] = field(default_factory=list)
    folded: bool = False
    all_in: bool = False
    eliminated: bool = False
    current_bet: int = 0
    total_bet: int = 0
    last_action: str = ""

    def reset_for_hand(self) -> None:
        self.hand.clear()
        self.folded = False
        self.all_in = False
        self.current_bet = 0
        self.total_bet = 0
        self.last_action = ""
        if self.stack <= 0:
            self.eliminated = True


@dataclass(frozen=True)
class PotResult:
    amount: int
    winners: tuple[int, ...]


def create_deck() -> list[Card]:
    return [Card(rank, suit) for suit in SUITS for rank in RANKS]


def evaluate_hand(cards: list[Card] | tuple[Card, ...]) -> HandScore:
    if len(cards) < 5:
        raise ValueError("At least five cards are required to evaluate a hand.")
    return max(_evaluate_five_cards(combo) for combo in combinations(cards, 5))


def _evaluate_five_cards(cards: tuple[Card, ...]) -> HandScore:
    values = sorted((card.value for card in cards), reverse=True)
    counts = {value: values.count(value) for value in set(values)}
    is_flush = len({card.suit for card in cards}) == 1
    straight_high = _straight_high(values)

    if is_flush and straight_high:
        return HandScore(8, (straight_high,), "Straight Flush", cards)

    four = [value for value, count in counts.items() if count == 4]
    if four:
        quad = max(four)
        kicker = max(value for value in values if value != quad)
        return HandScore(7, (quad, kicker), "Four of a Kind", cards)

    triples = sorted((value for value, count in counts.items() if count == 3), reverse=True)
    pairs = sorted((value for value, count in counts.items() if count == 2), reverse=True)
    if triples and pairs:
        return HandScore(6, (triples[0], pairs[0]), "Full House", cards)

    if is_flush:
        return HandScore(5, tuple(values), "Flush", cards)

    if straight_high:
        return HandScore(4, (straight_high,), "Straight", cards)

    if triples:
        trips = triples[0]
        kickers = tuple(value for value in values if value != trips)[:2]
        return HandScore(3, (trips, *kickers), "Three of a Kind", cards)

    if len(pairs) >= 2:
        high_pair, low_pair = pairs[:2]
        kicker = max(value for value in values if value not in (high_pair, low_pair))
        return HandScore(2, (high_pair, low_pair, kicker), "Two Pair", cards)

    if pairs:
        pair = pairs[0]
        kickers = tuple(value for value in values if value != pair)[:3]
        return HandScore(1, (pair, *kickers), "Pair", cards)

    return HandScore(0, tuple(values), "High Card", cards)


def _straight_high(values: list[int]) -> int:
    unique = sorted(set(values), reverse=True)
    if {14, 5, 4, 3, 2}.issubset(unique):
        return 5
    for start in range(len(unique) - 4):
        window = unique[start:start + 5]
        if window[0] - window[-1] == 4:
            return window[0]
    return 0


def active_player_indices(players: list[PlayerState]) -> list[int]:
    return [i for i, player in enumerate(players) if not player.eliminated]


class PokerGame:
    def __init__(
        self,
        names: list[str],
        bot_indices: set[int] | None = None,
        starting_stack: int = 1000,
        small_blind: int = 10,
        big_blind: int = 20,
        rng: random.Random | None = None,
    ):
        if len(names) < 2:
            raise ValueError("A poker game needs at least two players.")
        self.rng = rng or random.Random()
        bot_indices = bot_indices or set()
        self.players = [
            PlayerState(name=name, stack=starting_stack, is_bot=i in bot_indices)
            for i, name in enumerate(names)
        ]
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.dealer_index = -1
        self.current_player_index = 0
        self.street = "IDLE"
        self.deck: list[Card] = []
        self.community_cards: list[Card] = []
        self.current_bet = 0
        self.min_raise = big_blind
        self.acted: set[int] = set()
        self.hand_results: list[PotResult] = []
        self.message = "Start a new hand."

    @property
    def pot(self) -> int:
        return sum(player.total_bet for player in self.players)

    @property
    def current_player(self) -> PlayerState:
        return self.players[self.current_player_index]

    def call_amount(self, index: int | None = None) -> int:
        index = self.current_player_index if index is None else index
        player = self.players[index]
        return max(0, self.current_bet - player.current_bet)

    def legal_actions(self) -> set[str]:
        if self.street not in ("PREFLOP", "FLOP", "TURN", "RIVER"):
            return set()
        player = self.current_player
        if player.folded or player.all_in or player.eliminated:
            return set()
        actions = {"fold", "call"}
        if self.call_amount() == 0:
            actions.add("check")
        if player.stack > self.call_amount():
            actions.add("raise")
        return actions

    def start_hand(self) -> None:
        for player in self.players:
            player.reset_for_hand()
        active = active_player_indices(self.players)
        if len(active) < 2:
            self.street = "IDLE"
            self.message = "Game over."
            return

        self.community_cards = []
        self.hand_results = []
        self.deck = create_deck()
        self.rng.shuffle(self.deck)
        self.street = "PREFLOP"
        self.current_bet = 0
        self.min_raise = self.big_blind
        self.acted = set()

        self.dealer_index = self._next_active_index(self.dealer_index)
        small_blind_index, big_blind_index = self._blind_indices()
        self._take_bet(small_blind_index, self.small_blind)
        self.players[small_blind_index].last_action = f"Small blind ${self.players[small_blind_index].current_bet}"
        self._take_bet(big_blind_index, self.big_blind)
        self.players[big_blind_index].last_action = f"Big blind ${self.players[big_blind_index].current_bet}"
        self.current_bet = max(player.current_bet for player in self.players)

        for _ in range(2):
            for index in active:
                self.players[index].hand.append(self.deck.pop())

        self.current_player_index = self._next_player_who_can_act(big_blind_index)
        self.message = f"{self.current_player.name}'s turn."
        self._maybe_finish_betting_round()

    def fold(self) -> None:
        self._require_action("fold")
        player = self.current_player
        player.folded = True
        player.last_action = "Fold"
        self.acted.add(self.current_player_index)
        self._after_action()

    def check_or_call(self) -> None:
        actions = self.legal_actions()
        if "check" not in actions and "call" not in actions:
            raise ValueError("Check/call is not legal right now.")
        owed = self.call_amount()
        paid = self._take_bet(self.current_player_index, owed)
        player = self.current_player
        player.last_action = "Check" if paid == 0 else ("All in" if player.all_in else f"Call ${paid}")
        self.acted.add(self.current_player_index)
        self._after_action()

    def raise_to(self, total_bet_for_street: int) -> None:
        self._require_action("raise")
        player = self.current_player
        if total_bet_for_street <= self.current_bet:
            raise ValueError("A raise must exceed the current bet.")
        needed = total_bet_for_street - player.current_bet
        if needed > player.stack:
            raise ValueError("Player does not have enough chips for that raise.")

        raise_size = total_bet_for_street - self.current_bet
        is_all_in = needed == player.stack
        if raise_size < self.min_raise and not is_all_in:
            raise ValueError(f"Minimum raise is ${self.min_raise}.")

        self._take_bet(self.current_player_index, needed)
        if total_bet_for_street > self.current_bet:
            if raise_size >= self.min_raise:
                self.min_raise = raise_size
                self.acted = {self.current_player_index}
            else:
                self.acted.add(self.current_player_index)
            self.current_bet = total_bet_for_street
        player.last_action = "All in" if player.all_in else f"Raise to ${total_bet_for_street}"
        self._after_action()

    def bot_take_action(self) -> None:
        player = self.current_player
        if not player.is_bot:
            raise ValueError("Current player is not a bot.")
        score = evaluate_hand(player.hand + self.community_cards) if len(player.hand + self.community_cards) >= 5 else None
        owed = self.call_amount()
        if owed == 0:
            if player.stack > self.big_blind and self.rng.random() < 0.12:
                self.raise_to(player.current_bet + self.big_blind)
            else:
                self.check_or_call()
            return
        if owed >= player.stack:
            self.check_or_call()
            return
        fold_chance = 0.18
        if score and score.category >= 1:
            fold_chance = 0.05
        if self.rng.random() < fold_chance:
            self.fold()
        else:
            self.check_or_call()

    def _after_action(self) -> None:
        if self._award_if_only_one_player_left():
            return
        self._maybe_finish_betting_round()
        if self.street in ("PREFLOP", "FLOP", "TURN", "RIVER"):
            self.current_player_index = self._next_player_who_can_act(self.current_player_index)
            self.message = f"{self.current_player.name}'s turn."

    def _maybe_finish_betting_round(self) -> None:
        while self.street in ("PREFLOP", "FLOP", "TURN", "RIVER"):
            can_act = self._players_who_can_act()
            if not can_act:
                self._deal_remaining_board()
                self._showdown()
                return
            all_called = all(
                player.current_bet == self.current_bet or player.folded or player.all_in or player.eliminated
                for player in self.players
            )
            everyone_acted = all(index in self.acted for index in can_act)
            if not (all_called and everyone_acted):
                return
            self._advance_street()

    def _advance_street(self) -> None:
        for player in self.players:
            player.current_bet = 0
        self.current_bet = 0
        self.min_raise = self.big_blind
        self.acted = set()

        if self.street == "PREFLOP":
            self._deal_board_cards(3)
            self.street = "FLOP"
        elif self.street == "FLOP":
            self._deal_board_cards(1)
            self.street = "TURN"
        elif self.street == "TURN":
            self._deal_board_cards(1)
            self.street = "RIVER"
        elif self.street == "RIVER":
            self._showdown()
            return

        if not self._players_who_can_act():
            return
        self.current_player_index = self._next_player_who_can_act(self.dealer_index)
        self.message = f"{self.street}: {self.current_player.name}'s turn."

    def _showdown(self) -> None:
        self.street = "SHOWDOWN"
        self.hand_results = self._distribute_pots()
        for player in self.players:
            if player.stack <= 0:
                player.eliminated = True
        winners = sorted({winner for result in self.hand_results for winner in result.winners})
        if winners:
            names = ", ".join(self.players[index].name for index in winners)
            self.message = f"{names} won the pot."
        else:
            self.message = "No pot awarded."
        self.street = "HAND_OVER"

    def _award_if_only_one_player_left(self) -> bool:
        contenders = [i for i, player in enumerate(self.players) if not player.folded and not player.eliminated]
        if len(contenders) != 1:
            return False
        winner = self.players[contenders[0]]
        amount = self.pot
        winner.stack += amount
        winner.last_action = f"Won ${amount}"
        for player in self.players:
            player.total_bet = 0
            player.current_bet = 0
            if player.stack <= 0:
                player.eliminated = True
        self.hand_results = [PotResult(amount, (contenders[0],))]
        self.street = "HAND_OVER"
        self.message = f"{winner.name} won ${amount}."
        return True

    def _distribute_pots(self) -> list[PotResult]:
        commitments = {i: player.total_bet for i, player in enumerate(self.players) if player.total_bet > 0}
        results: list[PotResult] = []
        while commitments:
            level = min(commitments.values())
            participants = tuple(sorted(commitments))
            pot_amount = level * len(participants)
            contenders = [i for i in participants if not self.players[i].folded]
            winners = self._best_players(contenders) if contenders else []
            if winners:
                share, remainder = divmod(pot_amount, len(winners))
                for offset, winner_index in enumerate(winners):
                    self.players[winner_index].stack += share + (1 if offset < remainder else 0)
                    self.players[winner_index].last_action = f"Won ${share}"
                results.append(PotResult(pot_amount, tuple(winners)))
            commitments = {
                index: amount - level
                for index, amount in commitments.items()
                if amount - level > 0
            }
        for player in self.players:
            player.total_bet = 0
            player.current_bet = 0
        return results

    def _best_players(self, indices: list[int]) -> list[int]:
        best_score: HandScore | None = None
        winners: list[int] = []
        for index in indices:
            score = evaluate_hand(self.players[index].hand + self.community_cards)
            if best_score is None or score > best_score:
                best_score = score
                winners = [index]
            elif score == best_score:
                winners.append(index)
        return winners

    def _deal_board_cards(self, count: int) -> None:
        for _ in range(count):
            self.community_cards.append(self.deck.pop())

    def _deal_remaining_board(self) -> None:
        while len(self.community_cards) < 5:
            self.community_cards.append(self.deck.pop())

    def _blind_indices(self) -> tuple[int, int]:
        active = active_player_indices(self.players)
        if len(active) == 2:
            return self.dealer_index, self._next_active_index(self.dealer_index)
        small_blind = self._next_active_index(self.dealer_index)
        big_blind = self._next_active_index(small_blind)
        return small_blind, big_blind

    def _take_bet(self, index: int, amount: int) -> int:
        player = self.players[index]
        paid = min(max(0, amount), player.stack)
        player.stack -= paid
        player.current_bet += paid
        player.total_bet += paid
        if player.stack == 0:
            player.all_in = True
        return paid

    def _players_who_can_act(self) -> list[int]:
        return [
            i for i, player in enumerate(self.players)
            if not player.folded and not player.all_in and not player.eliminated
        ]

    def _next_active_index(self, start_index: int) -> int:
        for step in range(1, len(self.players) + 1):
            index = (start_index + step) % len(self.players)
            if not self.players[index].eliminated:
                return index
        raise RuntimeError("No active players remain.")

    def _next_player_who_can_act(self, start_index: int) -> int:
        for step in range(1, len(self.players) + 1):
            index = (start_index + step) % len(self.players)
            player = self.players[index]
            if not player.folded and not player.all_in and not player.eliminated:
                return index
        return start_index

    def _require_action(self, action: str) -> None:
        if action not in self.legal_actions():
            raise ValueError(f"{action} is not legal right now.")
