import random
import unittest

from poker_flow import AppScreen, SetupController
from poker_rules import Card, PlayerState, PokerGame, evaluate_hand


def c(rank, suit):
    return Card(rank, suit)


class HandEvaluationTests(unittest.TestCase):
    def test_straight_flush_beats_four_of_a_kind(self):
        straight_flush = evaluate_hand([
            c("9", "Hearts"), c("8", "Hearts"), c("7", "Hearts"),
            c("6", "Hearts"), c("5", "Hearts"), c("A", "Spades"),
            c("2", "Clubs"),
        ])
        quads = evaluate_hand([
            c("A", "Hearts"), c("A", "Diamonds"), c("A", "Clubs"),
            c("A", "Spades"), c("K", "Hearts"), c("3", "Clubs"),
            c("2", "Spades"),
        ])
        self.assertGreater(straight_flush, quads)

    def test_wheel_straight_counts_as_five_high(self):
        score = evaluate_hand([
            c("A", "Hearts"), c("2", "Diamonds"), c("3", "Clubs"),
            c("4", "Spades"), c("5", "Hearts"), c("K", "Clubs"),
            c("Q", "Spades"),
        ])
        self.assertEqual(score.name, "Straight")
        self.assertEqual(score.tiebreakers, (5,))

    def test_pair_kickers_break_ties(self):
        ace_kicker = evaluate_hand([
            c("K", "Hearts"), c("K", "Diamonds"), c("A", "Clubs"),
            c("8", "Spades"), c("4", "Hearts"),
        ])
        queen_kicker = evaluate_hand([
            c("K", "Clubs"), c("K", "Spades"), c("Q", "Clubs"),
            c("8", "Diamonds"), c("4", "Spades"),
        ])
        self.assertGreater(ace_kicker, queen_kicker)


class GameFlowTests(unittest.TestCase):
    def test_heads_up_blinds_and_turn_order(self):
        game = PokerGame(["Alice", "Bob"], rng=random.Random(1))
        game.start_hand()
        self.assertEqual(game.dealer_index, 0)
        self.assertEqual(game.players[0].current_bet, game.small_blind)
        self.assertEqual(game.players[1].current_bet, game.big_blind)
        self.assertEqual(game.current_player_index, 0)

    def test_fold_awards_whole_pot(self):
        game = PokerGame(["Alice", "Bob"], rng=random.Random(1))
        game.start_hand()
        game.fold()
        self.assertEqual(game.street, "HAND_OVER")
        self.assertEqual(game.players[1].stack, 1010)
        self.assertEqual(game.pot, 0)

    def test_side_pot_distribution(self):
        game = PokerGame(["Short", "Middle", "Big"], starting_stack=0)
        game.community_cards = [
            c("A", "Hearts"), c("K", "Diamonds"), c("8", "Clubs"),
            c("4", "Spades"), c("2", "Hearts"),
        ]
        game.players = [
            PlayerState("Short", stack=0, hand=[c("A", "Clubs"), c("A", "Spades")], total_bet=50, all_in=True),
            PlayerState("Middle", stack=0, hand=[c("K", "Clubs"), c("K", "Spades")], total_bet=100, all_in=True),
            PlayerState("Big", stack=0, hand=[c("Q", "Clubs"), c("J", "Spades")], total_bet=100, all_in=True),
        ]
        results = game._distribute_pots()
        self.assertEqual(results[0].amount, 150)
        self.assertEqual(results[0].winners, (0,))
        self.assertEqual(results[1].amount, 100)
        self.assertEqual(results[1].winners, (1,))
        self.assertEqual([player.stack for player in game.players], [150, 100, 0])


class SetupFlowTests(unittest.TestCase):
    def test_single_player_collects_one_name_and_creates_bots(self):
        flow = SetupController(single_player_total=4)
        flow.choose_single_player()
        setup = flow.submit_name("  Avery  ")
        self.assertEqual(flow.screen, AppScreen.TABLE)
        self.assertEqual(setup.names, ["Avery", "Bot 1", "Bot 2", "Bot 3"])
        self.assertEqual(setup.bot_indices, {1, 2, 3})

    def test_multiplayer_collects_names_in_turn(self):
        flow = SetupController()
        flow.choose_multiplayer()
        flow.choose_player_count(3)
        self.assertIsNone(flow.submit_name("A"))
        self.assertIsNone(flow.submit_name("B"))
        setup = flow.submit_name("C")
        self.assertEqual(flow.screen, AppScreen.TABLE)
        self.assertEqual(setup.names, ["A", "B", "C"])
        self.assertEqual(setup.bot_indices, set())

    def test_duplicate_names_are_rejected_case_insensitively(self):
        flow = SetupController()
        flow.choose_multiplayer()
        flow.choose_player_count(2)
        self.assertIsNone(flow.submit_name("Sam"))
        self.assertIsNone(flow.submit_name("sam"))
        self.assertEqual(flow.screen, AppScreen.NAME_ENTRY)
        self.assertEqual(flow.name_error, "Name already taken.")

    def test_how_to_play_returns_to_previous_screen(self):
        flow = SetupController()
        flow.show_how_to_play(return_to=AppScreen.TABLE)
        flow.leave_how_to_play()
        self.assertEqual(flow.screen, AppScreen.TABLE)


if __name__ == "__main__":
    unittest.main()
