from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class AppScreen(Enum):
    TITLE = "title"
    PLAYER_COUNT = "player_count"
    NAME_ENTRY = "name_entry"
    HOW_TO_PLAY = "how_to_play"
    TABLE = "table"


class GameMode(Enum):
    SINGLE_PLAYER = "single_player"
    MULTIPLAYER = "multiplayer"


@dataclass(frozen=True)
class GameSetup:
    names: list[str]
    bot_indices: set[int]


class SetupController:
    def __init__(self, single_player_total: int = 4):
        self.single_player_total = single_player_total
        self.screen = AppScreen.TITLE
        self.mode: GameMode | None = None
        self.player_count = single_player_total
        self.entered_names: list[str] = []
        self.name_error = ""
        self.return_screen = AppScreen.TITLE

    @property
    def expected_manual_names(self) -> int:
        if self.mode == GameMode.SINGLE_PLAYER:
            return 1
        return self.player_count

    @property
    def current_name_prompt(self) -> str:
        next_number = len(self.entered_names) + 1
        if self.mode == GameMode.SINGLE_PLAYER:
            return "Enter your name"
        return f"Enter player {next_number} name"

    def choose_single_player(self) -> None:
        self.mode = GameMode.SINGLE_PLAYER
        self.player_count = self.single_player_total
        self.entered_names = []
        self.name_error = ""
        self.screen = AppScreen.NAME_ENTRY

    def choose_multiplayer(self) -> None:
        self.mode = GameMode.MULTIPLAYER
        self.entered_names = []
        self.name_error = ""
        self.screen = AppScreen.PLAYER_COUNT

    def choose_player_count(self, count: int) -> None:
        if count < 2:
            raise ValueError("A poker table needs at least two players.")
        self.mode = GameMode.MULTIPLAYER
        self.player_count = count
        self.entered_names = []
        self.name_error = ""
        self.screen = AppScreen.NAME_ENTRY

    def show_how_to_play(self, return_to: AppScreen | None = None) -> None:
        self.return_screen = return_to or self.screen
        self.screen = AppScreen.HOW_TO_PLAY

    def back_to_title(self) -> None:
        self.screen = AppScreen.TITLE
        self.name_error = ""

    def leave_how_to_play(self) -> None:
        self.screen = self.return_screen

    def submit_name(self, raw_name: str) -> GameSetup | None:
        name = " ".join(raw_name.strip().split())
        if not name:
            self.name_error = "Name cannot be empty."
            return None
        if name.lower() in {existing.lower() for existing in self.entered_names}:
            self.name_error = "Name already taken."
            return None

        self.entered_names.append(name)
        self.name_error = ""

        if len(self.entered_names) < self.expected_manual_names:
            return None

        setup = self._build_game_setup()
        self.screen = AppScreen.TABLE
        return setup

    def _build_game_setup(self) -> GameSetup:
        if self.mode == GameMode.SINGLE_PLAYER:
            names = [self.entered_names[0]]
            names.extend(f"Bot {index}" for index in range(1, self.single_player_total))
            return GameSetup(names=names, bot_indices=set(range(1, len(names))))

        return GameSetup(names=list(self.entered_names), bot_indices=set())
