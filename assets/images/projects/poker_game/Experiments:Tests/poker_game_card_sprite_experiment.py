import math
import os
import random
import sys

import pygame

from poker_flow import AppScreen, SetupController
from poker_rules import Card, PokerGame


WIDTH, HEIGHT = 1200, 800
FPS = 60
STARTING_STACK = 1000
SMALL_BLIND = 10
BIG_BLIND = 20
PLAYER_COUNT_OPTIONS = (2, 3, 4, 5, 6)
POKER_FONT_PATH = os.path.join("fonts", "Poker_font-Regular.ttf")
PROFILE_DIR = os.path.join("game screen", "Profiles")
CARD_DIR = os.path.join("game screen", "Cards")
CARD_BASE_WIDTH = 86
CARD_BASE_HEIGHT = 130

BG = (17, 19, 24)
FELT = (24, 120, 72)
FELT_DARK = (14, 86, 52)
RIM = (92, 58, 31)
PANEL = (30, 34, 42)
PANEL_LIGHT = (45, 51, 62)
WHITE = (245, 245, 240)
MUTED = (170, 176, 186)
BLACK = (10, 10, 12)
GOLD = (232, 190, 82)
RED = (194, 55, 58)
BLUE = (62, 110, 190)
GREEN = (48, 150, 92)

SUIT_SYMBOLS = {
    "Hearts": "H",
    "Diamonds": "D",
    "Clubs": "C",
    "Spades": "S",
}
RED_SUITS = {"Hearts", "Diamonds"}

HOW_TO_PLAY_LINES = [
    "Make the best five-card poker hand using your two cards and the board.",
    "Blinds start each hand. Action moves around the table.",
    "You can check, call, raise, or fold when it is your turn.",
    "The flop, turn, and river reveal five shared community cards.",
    "Win by having the best hand at showdown or by making everyone else fold.",
]


class Button:
    def __init__(self, text, rect, color, action, image=None):
        self.text = text
        self.rect = pygame.Rect(rect)
        self.color = color
        self.action = action
        self.image = image

    def draw(self, surface, font):
        mouse = pygame.mouse.get_pos()
        if self.image is not None:
            image = self.image
            if self.rect.collidepoint(mouse):
                image = pygame.transform.smoothscale(
                    self.image,
                    (int(self.image.get_width() * 1.04), int(self.image.get_height() * 1.04)),
                )
            image_rect = image.get_rect(center=self.rect.center)
            surface.blit(image, image_rect)
            return

        color = tuple(min(255, channel + 24) for channel in self.color) if self.rect.collidepoint(mouse) else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=7)
        pygame.draw.rect(surface, WHITE, self.rect, width=2, border_radius=7)
        label = font.render(self.text, True, WHITE)
        surface.blit(label, label.get_rect(center=self.rect.center))

    def clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)


class TextInput:
    def __init__(self, rect):
        self.rect = pygame.Rect(rect)
        self.text = ""
        self.active = True

    def clear(self):
        self.text = ""
        self.active = True

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            return None
        if event.type != pygame.KEYDOWN or not self.active:
            return None
        if event.key == pygame.K_RETURN:
            return self.text
        if event.key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]
        elif event.unicode and len(self.text) < 20:
            self.text += event.unicode
        return None

    def draw(self, surface, font, error=False):
        border = RED if error else (GOLD if self.active else MUTED)
        pygame.draw.rect(surface, BLACK, self.rect, border_radius=6)
        pygame.draw.rect(surface, border, self.rect, width=2, border_radius=6)
        label = font.render(self.text, True, WHITE)
        surface.blit(label, (self.rect.x + 14, self.rect.y + 13))


class PokerApp:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Texas Hold'em")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font_cache = {}
        self.font_xl = self._font(56)
        self.font_lg = self._font(34)
        self.font_md = self._font(23)
        self.font_sm = self._font(17)
        self.rng = random.Random()
        self.flow = SetupController(single_player_total=4)
        self.game: PokerGame | None = None
        self.player_profiles = []
        self.raise_total = BIG_BLIND * 2
        self.bot_action_due = 0
        self.name_input = TextInput((450, 520, 300, 54))
        self.title_assets = self._load_title_assets()
        self.select_assets = self._load_player_select_assets()
        self.profile_assets = self._load_profile_assets()
        self.card_assets = self._load_card_assets()
        self.buttons = self._make_buttons()

    def _font(self, size):
        if size not in self.font_cache:
            try:
                self.font_cache[size] = pygame.font.Font(POKER_FONT_PATH, size)
            except (FileNotFoundError, pygame.error):
                self.font_cache[size] = pygame.font.SysFont("arial", size)
        return self.font_cache[size]

    def _load_title_assets(self):
        title_dir = "Title"
        return {
            "bg": self._load_image(title_dir, "Title_BG.png"),
            "cards": self._load_image(title_dir, "Title_Cards.png"),
            "folder": self._load_image(title_dir, "Title_Folder.png"),
            "texas": self._load_image(title_dir, "Title_Texas.png"),
            "holdem": self._load_image(title_dir, "Title_Holdem.png"),
            "single": self._load_image(title_dir, "Title_Button_SinglePlayer.png"),
            "multi": self._load_image(title_dir, "Title_Button_Multiplayer.png"),
            "how_to": self._load_image(title_dir, "Title_Button_HowToPlay.png"),
            "letters": {
                "P": self._load_image(title_dir, "Title_P.png"),
                "O": self._load_image(title_dir, "Title_O.png"),
                "K": self._load_image(title_dir, "Title_K.png"),
                "E": self._load_image(title_dir, "Title_E.png"),
                "R": self._load_image(title_dir, "Title_R.png"),
            },
        }

    def _load_image(self, *parts):
        path = os.path.join(*parts)
        try:
            return pygame.image.load(path).convert_alpha()
        except pygame.error as error:
            raise SystemExit(f"Could not load image asset: {path}") from error

    def _load_optional_image(self, *parts):
        path = os.path.join(*parts)
        try:
            return pygame.image.load(path).convert_alpha()
        except pygame.error:
            return None

    def _load_player_select_assets(self):
        select_dir = "Player Select"
        return {
            "bg": self._load_optional_image(select_dir, "PlayerSelect_BG.png"),
            "title": self._load_optional_image(select_dir, "PlayerSelect_Title.png"),
            "enter_name": self._load_optional_image(select_dir, "PlayerSelect_EnterName.png"),
            "confirm": self._load_optional_image(select_dir, "PlayerSelect_Button_Confirm.png"),
            "buttons": {
                2: self._load_optional_image(select_dir, "PlayerSelect_Button_2P.png"),
                3: self._load_optional_image(select_dir, "PlayerSelect_Button_3P.png"),
                4: self._load_optional_image(select_dir, "PlayerSelect_Button_4P.png"),
                5: self._load_optional_image(select_dir, "PlayerSelect_Button_5P.png"),
                6: self._load_optional_image(select_dir, "PlayerSelect_Button_6P.png"),
                "funny": self._load_optional_image(select_dir, "PlayerSelect_Button_Funny.png"),
            },
        }

    def _load_profile_assets(self):
        if not os.path.isdir(PROFILE_DIR):
            return []

        profile_paths = [
            os.path.join(PROFILE_DIR, filename)
            for filename in sorted(os.listdir(PROFILE_DIR))
            if filename.lower().endswith((".png", ".jpg", ".jpeg"))
        ]
        profiles = []
        for path in profile_paths:
            try:
                profiles.append(pygame.image.load(path).convert_alpha())
            except pygame.error:
                continue
        return profiles

    def _load_card_assets(self):
        if not os.path.isdir(CARD_DIR):
            return {}

        cards = {}
        for folder in ("A-5", "6-10", "Face"):
            folder_path = os.path.join(CARD_DIR, folder)
            if not os.path.isdir(folder_path):
                continue
            for filename in sorted(os.listdir(folder_path)):
                if not filename.lower().endswith(".png"):
                    continue
                key = os.path.splitext(filename)[0]
                try:
                    cards[key] = pygame.image.load(os.path.join(folder_path, filename)).convert_alpha()
                except pygame.error:
                    continue
        return cards

    def _make_buttons(self):
        title_button_w, title_button_h = 400, 70
        title_button_x = 700
        buttons = {
            "single": Button("", (title_button_x - 75, 160, title_button_w, title_button_h), GREEN, "single", self.title_assets["single"]),
            "multi": Button("", (title_button_x + 60, 360, title_button_w, title_button_h), BLUE, "multi", self.title_assets["multi"]),
            "how_to": Button("", (title_button_x - 160, 605, title_button_w, title_button_h), PANEL_LIGHT, "how_to", self.title_assets["how_to"]),
            "back": Button("BACK", (40, 40, 120, 44), RED, "back"),
            "confirm_name": Button("CONFIRM", (400, 650, 400, 70), GREEN, "confirm_name", self.select_assets["confirm"]),
            "new_hand": Button("DEAL HAND", (970, 30, 190, 54), GOLD, "new_hand"),
            "call": Button("CHECK / CALL", (950, 540, 200, 48), BLUE, "call"),
            "raise": Button("RAISE", (950, 605, 200, 48), BLUE, "raise"),
            "fold": Button("FOLD", (950, 670, 200, 48), RED, "fold"),
            "raise_down": Button("-10", (880, 605, 58, 48), PANEL_LIGHT, "raise_down"),
            "raise_up": Button("10", (1162, 605, 58, 48), PANEL_LIGHT, "raise_up"),
            "hands": Button("HANDS", (20, 70, 110, 40), PANEL_LIGHT, "hands"),
            "quit": Button("QUIT", (20, 20, 110, 40), RED, "quit"),
        }
        player_select_positions = {
            2: (250, 250, 220, 70),
            3: (680, 250, 220, 70),
            4: (260, 430, 220, 70),
            5: (700, 430, 220, 70),
            6: (280, 630, 220, 70),
            "funny": (630, 630, 220, 70),
        }
        for count in PLAYER_COUNT_OPTIONS:
            buttons[f"players_{count}"] = Button(
                str(count),
                player_select_positions[count],
                BLUE,
                f"players_{count}",
                self.select_assets["buttons"][count],
            )
        buttons["players_funny"] = Button(
            "",
            player_select_positions["funny"],
            PANEL_LIGHT,
            "players_funny",
            self.select_assets["buttons"]["funny"],
        )
        return buttons

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    self._handle_event(event)
            self._update(dt)
            self._draw()
        pygame.quit()
        sys.exit()

    def _handle_event(self, event):
        screen = self.flow.screen
        if screen == AppScreen.TITLE:
            self._handle_title_event(event)
        elif screen == AppScreen.PLAYER_COUNT:
            self._handle_player_count_event(event)
        elif screen == AppScreen.NAME_ENTRY:
            self._handle_name_entry_event(event)
        elif screen == AppScreen.HOW_TO_PLAY:
            self._handle_how_to_play_event(event)
        elif screen == AppScreen.TABLE:
            self._handle_table_event(event)

    def _handle_title_event(self, event):
        if self.buttons["single"].clicked(event):
            self.flow.choose_single_player()
            self.name_input.clear()
        elif self.buttons["multi"].clicked(event):
            self.flow.choose_multiplayer()
        elif self.buttons["how_to"].clicked(event):
            self.flow.show_how_to_play(return_to=AppScreen.TITLE)

    def _handle_player_count_event(self, event):
        if self.buttons["back"].clicked(event):
            self.flow.back_to_title()
            return
        for count in PLAYER_COUNT_OPTIONS:
            if self.buttons[f"players_{count}"].clicked(event):
                self.flow.choose_player_count(count)
                self.name_input.clear()
                return

    def _handle_name_entry_event(self, event):
        submitted = self.name_input.handle_event(event)
        if self.buttons["back"].clicked(event):
            self.flow.back_to_title()
            self.name_input.clear()
            return
        if self.buttons["confirm_name"].clicked(event):
            submitted = self.name_input.text
        if submitted is not None:
            setup = self.flow.submit_name(submitted)
            if not self.flow.name_error:
                self.name_input.clear()
            if setup is not None:
                self._create_game(setup.names, setup.bot_indices)

    def _handle_how_to_play_event(self, event):
        if self.buttons["back"].clicked(event):
            self.flow.leave_how_to_play()

    def _handle_table_event(self, event):
        if self.buttons["quit"].clicked(event):
            self.flow.back_to_title()
            self.game = None
            return
        if self.buttons["hands"].clicked(event):
            self.flow.show_how_to_play(return_to=AppScreen.TABLE)
            return
        if self.game is None:
            return
        if self.game.street in ("IDLE", "HAND_OVER"):
            if self.buttons["new_hand"].clicked(event):
                self.game.start_hand()
                self._sync_raise_total()
            return

        current = self.game.current_player
        if current.is_bot:
            return

        if self.buttons["fold"].clicked(event) and "fold" in self.game.legal_actions():
            self.game.fold()
            self._sync_raise_total()
        elif self.buttons["call"].clicked(event) and self.game.legal_actions():
            self.game.check_or_call()
            self._sync_raise_total()
        elif self.buttons["raise_down"].clicked(event):
            self.raise_total = max(self._min_raise_to(), self.raise_total - 10)
        elif self.buttons["raise_up"].clicked(event):
            self.raise_total = min(self._max_raise_to(), self.raise_total + 10)
        elif self.buttons["raise"].clicked(event) and "raise" in self.game.legal_actions():
            self.game.raise_to(self.raise_total)
            self._sync_raise_total()

    def _create_game(self, names, bot_indices):
        self.game = PokerGame(
            names,
            bot_indices=bot_indices,
            starting_stack=STARTING_STACK,
            small_blind=SMALL_BLIND,
            big_blind=BIG_BLIND,
            rng=self.rng,
        )
        self.player_profiles = self._choose_player_profiles(len(names))
        self._sync_raise_total()

    def _choose_player_profiles(self, count):
        if not self.profile_assets:
            return []
        if count <= len(self.profile_assets):
            return self.rng.sample(self.profile_assets, count)
        return [self.rng.choice(self.profile_assets) for _ in range(count)]

    def _update(self, dt):
        if self.flow.screen != AppScreen.TABLE or self.game is None:
            return
        if self.game.street in ("PREFLOP", "FLOP", "TURN", "RIVER") and self.game.current_player.is_bot:
            now = pygame.time.get_ticks()
            if self.bot_action_due == 0:
                self.bot_action_due = now + 650
            elif now >= self.bot_action_due:
                self.game.bot_take_action()
                self.bot_action_due = 0
                self._sync_raise_total()
        else:
            self.bot_action_due = 0

    def _sync_raise_total(self):
        if self.game is not None and self.game.street in ("PREFLOP", "FLOP", "TURN", "RIVER"):
            self.raise_total = self._min_raise_to()

    def _min_raise_to(self):
        player = self.game.current_player
        return min(player.current_bet + player.stack, self.game.current_bet + self.game.min_raise)

    def _max_raise_to(self):
        player = self.game.current_player
        return player.current_bet + player.stack

    def _draw(self):
        self.screen.fill(BG)
        screen = self.flow.screen
        if screen == AppScreen.TITLE:
            self._draw_title()
        elif screen == AppScreen.PLAYER_COUNT:
            self._draw_player_count()
        elif screen == AppScreen.NAME_ENTRY:
            self._draw_name_entry()
        elif screen == AppScreen.HOW_TO_PLAY:
            self._draw_how_to_play()
        elif screen == AppScreen.TABLE:
            self._draw_table()
        pygame.display.flip()

    def _draw_title(self):
        self.screen.blit(self.title_assets["bg"], (0, 0))
        self.screen.blit(self.title_assets["cards"], (0, 0))
        self._draw_title_letters()
        self.screen.blit(self.title_assets["folder"], (0, 0))
        self.buttons["single"].draw(self.screen, self.font_md)
        self.buttons["multi"].draw(self.screen, self.font_md)
        self.buttons["how_to"].draw(self.screen, self.font_md)
        self.screen.blit(self.title_assets["texas"], (20, 70))
        self.screen.blit(self.title_assets["holdem"], (140, 155))

    def _draw_title_letters(self):
        start_x = 8
        y_base = 275
        x_offset = 0
        for char in "POKER":
            letter = self.title_assets["letters"][char]
            y = y_base
            if char == "O":
                y += 120
                x_offset -= 80
            if char == "R":
                y -= 20
                x_offset += 20
            self.screen.blit(letter, (start_x + x_offset, y))
            x_offset += letter.get_width() - 40

    def _draw_player_count(self):
        self._draw_player_select_background()
        self.buttons["back"].draw(self.screen, self.font_sm)
        title = self.font_xl.render("MULTIPLAYER", True, GOLD)
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, 30)))
        if self.select_assets["title"] is not None:
            title_image = self.select_assets["title"]
            self.screen.blit(title_image, title_image.get_rect(center=(WIDTH // 2, 165)))
        else:
            prompt = self.font_md.render("Choose number of players", True, WHITE)
            self.screen.blit(prompt, prompt.get_rect(center=(WIDTH // 2, 165)))
        for count in PLAYER_COUNT_OPTIONS:
            self.buttons[f"players_{count}"].draw(self.screen, self.font_lg)
        self.buttons["players_funny"].draw(self.screen, self.font_lg)

    def _draw_name_entry(self):
        self._draw_player_select_background()
        self.buttons["back"].draw(self.screen, self.font_sm)
        if self.select_assets["enter_name"] is not None:
            title = self.select_assets["enter_name"]
            self.screen.blit(title, title.get_rect(center=(WIDTH // 2, 150)))
        else:
            title = self.font_xl.render("NAME ENTRY", True, GOLD)
            self.screen.blit(title, title.get_rect(center=(WIDTH // 2, 130)))
        prompt = self.font_md.render(self.flow.current_name_prompt, True, WHITE)
        self.screen.blit(prompt, prompt.get_rect(center=(WIDTH // 2, 275)))
        self._draw_entered_name_boxes()
        self.name_input.draw(self.screen, self.font_md, error=bool(self.flow.name_error))
        self.buttons["confirm_name"].draw(self.screen, self.font_md)
        if self.flow.name_error:
            error = self.font_sm.render(self.flow.name_error, True, RED)
            self.screen.blit(error, error.get_rect(center=(WIDTH // 2, 735)))

    def _draw_player_select_background(self):
        if self.select_assets["bg"] is not None:
            self.screen.blit(self.select_assets["bg"], (0, 0))
        else:
            self.screen.fill(BG)

    def _draw_entered_name_boxes(self):
        names = self.flow.entered_names
        if not names:
            hint = self.font_sm.render("Entered names will appear here", True, MUTED)
            self.screen.blit(hint, hint.get_rect(center=(WIDTH // 2, 400)))
            return

        box_w, box_h = 260, 50
        gap_x, gap_y = 36, 18
        columns = 2 if len(names) > 1 else 1
        rows = math.ceil(len(names) / columns)
        total_w = columns * box_w + (columns - 1) * gap_x
        total_h = rows * box_h + (rows - 1) * gap_y
        start_x = WIDTH // 2 - total_w // 2
        start_y = 405 - total_h // 2

        for index, name in enumerate(names):
            col = index % columns
            row = index // columns
            rect = pygame.Rect(start_x + col * (box_w + gap_x), start_y + row * (box_h + gap_y), box_w, box_h)
            pygame.draw.rect(self.screen, PANEL, rect, border_radius=7)
            pygame.draw.rect(self.screen, GOLD, rect, width=2, border_radius=7)
            label = self.font_md.render(name, True, WHITE)
            self.screen.blit(label, label.get_rect(center=rect.center))

    def _draw_how_to_play(self):
        self.buttons["back"].draw(self.screen, self.font_sm)
        title = self.font_xl.render("HOW TO PLAY", True, GOLD)
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, 180)))
        for index, line in enumerate(HOW_TO_PLAY_LINES):
            text = self.font_md.render(line, True, WHITE)
            self.screen.blit(text, (220, 280 + index * 48))

    def _draw_table(self):
        if self.game is None:
            return
        self._draw_chamfered_table()
        self._draw_status()
        self._draw_community_cards()
        self._draw_table_players()
        self._draw_current_player_panel()
        self._draw_controls()
        self.buttons["quit"].draw(self.screen, self.font_sm)
        self.buttons["hands"].draw(self.screen, self.font_sm)

    def _draw_chamfered_table(self):
        rim = self._chamfered_rect_points(105, 30, 990, 390, 125)
        felt = self._chamfered_rect_points(140, 58, 920, 334, 105)
        inner = self._chamfered_rect_points(205, 115, 790, 218, 78)
        pygame.draw.polygon(self.screen, RIM, rim)
        pygame.draw.polygon(self.screen, FELT, felt)
        pygame.draw.polygon(self.screen, FELT_DARK, inner, width=4)

    def _chamfered_rect_points(self, x, y, w, h, cut):
        return [
            (x + cut, y),
            (x + w - cut, y),
            (x + w, y + cut),
            (x + w, y + h - cut),
            (x + w - cut, y + h),
            (x + cut, y + h),
            (x, y + h - cut),
            (x, y + cut),
        ]

    def _draw_status(self):
        street = "READY" if self.game.street == "IDLE" else self.game.street.replace("_", " ")
        street_text = self.font_lg.render(street, True, WHITE)
        pot_text = self.font_md.render(f"POT {self.game.pot}", True, GOLD)
        self.screen.blit(street_text, street_text.get_rect(center=(WIDTH // 2, 132)))
        self.screen.blit(pot_text, pot_text.get_rect(center=(WIDTH // 2, 172)))

    def _draw_community_cards(self):
        start_x = WIDTH // 2 - 220
        y = 235
        for index in range(5):
            if index < len(self.game.community_cards):
                self._draw_card(self.game.community_cards[index], start_x + index * 90, y, 1.0, True)
            else:
                self._draw_card_back(start_x + index * 90, y, 1.0)

    def _draw_table_players(self):
        count = len(self.game.players)
        for index, player in enumerate(self.game.players):
            px, py = self._table_player_position(index, count)
            is_turn = index == self.game.current_player_index and self.game.street in ("PREFLOP", "FLOP", "TURN", "RIVER")
            border = GOLD if is_turn else (RED if player.eliminated else WHITE)
            self._draw_profile(index, (px, py), 84, border)
            name = self.font_sm.render(player.name, True, WHITE)
            stack = self.font_sm.render("OUT" if player.eliminated else f"{player.stack}", True, GOLD)
            self.screen.blit(name, (px - 42, py + 48))
            self.screen.blit(stack, (px - 42, py + 69))

    def _table_player_position(self, index, count):
        anchors = {
            2: [(360, 92), (840, 92)],
            3: [(600, 62), (1000, 245), (200, 245)],
            4: [(405, 78), (795, 78), (1032, 250), (168, 250)],
            5: [(600, 60), (360, 92), (840, 92), (1018, 265), (182, 265)],
            6: [(315, 105), (500, 68), (700, 68), (885, 105), (1030, 255), (170, 255)],
        }
        if count in anchors:
            return anchors[count][index]

        table_path = self._chamfered_rect_points(150, 56, 900, 342, 105)
        return table_path[index % len(table_path)]

    def _draw_current_player_panel(self):
        if self.game.street in ("IDLE",) or not self.game.players:
            return
        player = self.game.current_player
        panel = pygame.Rect(35, 505, 330, 235)
        pygame.draw.rect(self.screen, PANEL, panel, border_radius=8)
        pygame.draw.rect(self.screen, GOLD, panel, width=2, border_radius=8)

        stack = self.font_md.render("OUT" if player.eliminated else f"{player.stack}", True, GOLD)
        status = self.font_sm.render(self._player_status(player), True, MUTED)
        self.screen.blit(stack, stack.get_rect(center=(105, 535)))
        self.screen.blit(status, status.get_rect(center=(105, 562)))

        self._draw_profile(self.game.current_player_index, (105, 625), 108, GOLD, player.name)

        name = self.font_lg.render(player.name, True, WHITE)
        self.screen.blit(name, name.get_rect(center=(105, 705)))

        self._draw_current_player_hand(player)

    def _player_status(self, player):
        if player.eliminated:
            return "Out"
        if player.folded:
            return "Folded"
        if player.all_in:
            return "All in"
        if self.game.street in ("IDLE", "HAND_OVER"):
            return "Ready"
        if player.is_bot:
            return "Thinking"
        return "Your turn"

    def _draw_profile(self, index, center, size, border, fallback_name="P"):
        rect = pygame.Rect(0, 0, size, size)
        rect.center = center

        if index < len(self.player_profiles):
            pygame.draw.circle(self.screen, border, center, size // 2 + 3, width=3)
            image = pygame.transform.smoothscale(self.player_profiles[index], (size, size))
            self.screen.blit(image, rect)
        else:
            pygame.draw.circle(self.screen, PANEL_LIGHT, center, size // 2)
            pygame.draw.circle(self.screen, border, center, size // 2, width=3)
            initials = "".join(part[0] for part in fallback_name.split()[:2]).upper() or "P"
            initials_label = self.font_lg.render(initials, True, WHITE)
            self.screen.blit(initials_label, initials_label.get_rect(center=center))

    def _draw_current_player_hand(self, player):
        if not player.hand or player.folded:
            return
        show_cards = self.game.street == "HAND_OVER" or not player.is_bot
        start_x = WIDTH // 2 - 100
        y = 530
        for index, card in enumerate(player.hand):
            x = start_x + index * 105
            if show_cards:
                self._draw_card(card, x, y - index * 8, 1.45, True)
            else:
                self._draw_card_back(x, y - index * 8, 1.45)

    def _draw_controls(self):
        if self.game.street in ("IDLE", "HAND_OVER"):
            self.buttons["new_hand"].draw(self.screen, self.font_sm)
            return
        current = self.game.current_player
        if current.is_bot:
            thinking = self.font_md.render("Thinking...", True, MUTED)
            self.screen.blit(thinking, thinking.get_rect(center=(1048, 615)))
            return
        self.buttons["call"].draw(self.screen, self.font_sm)
        self.buttons["fold"].draw(self.screen, self.font_sm)
        if "raise" in self.game.legal_actions():
            self.buttons["raise"].draw(self.screen, self.font_sm)
            self.buttons["raise_down"].draw(self.screen, self.font_sm)
            self.buttons["raise_up"].draw(self.screen, self.font_sm)
            amount = self.font_md.render(f"{self.raise_total}", True, GOLD)
            self.screen.blit(amount, amount.get_rect(center=(1048, 580)))

    def _draw_card(self, card: Card, x, y, scale, face_up):
        if not face_up:
            self._draw_card_back(x, y, scale)
            return

        sprite = self.card_assets.get(self._card_asset_key(card))
        if sprite is not None:
            w, h = int(CARD_BASE_WIDTH * scale), int(CARD_BASE_HEIGHT * scale)
            rect = pygame.Rect(x, y, w, h)
            pygame.draw.rect(self.screen, BLACK, rect.move(5, 5), border_radius=5)
            image = pygame.transform.smoothscale(sprite, (w, h))
            self.screen.blit(image, rect)
            return

        w, h = int(CARD_BASE_WIDTH * scale), int(CARD_BASE_HEIGHT * scale)
        rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(self.screen, BLACK, rect.move(4, 4), border_radius=5)
        pygame.draw.rect(self.screen, WHITE, rect, border_radius=5)
        pygame.draw.rect(self.screen, BLACK, rect, width=2, border_radius=5)
        color = RED if card.suit in RED_SUITS else BLACK
        rank_font = self._font(max(14, int(22 * scale)))
        suit_font = self._font(max(12, int(18 * scale)))
        rank = rank_font.render(card.rank, True, color)
        suit = suit_font.render(SUIT_SYMBOLS[card.suit], True, color)
        self.screen.blit(rank, (x + 7 * scale, y + 7 * scale))
        self.screen.blit(suit, suit.get_rect(center=rect.center))

    def _card_asset_key(self, card):
        return f"{card.rank}_{card.suit[0]}"

    def _draw_card_back(self, x, y, scale):
        w, h = int(CARD_BASE_WIDTH * scale), int(CARD_BASE_HEIGHT * scale)
        rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(self.screen, BLACK, rect.move(4, 4), border_radius=5)
        pygame.draw.rect(self.screen, RED, rect, border_radius=5)
        pygame.draw.rect(self.screen, WHITE, rect, width=2, border_radius=5)
        inset = rect.inflate(-14 * scale, -14 * scale)
        pygame.draw.rect(self.screen, (130, 26, 36), inset, width=2, border_radius=4)


if __name__ == "__main__":
    PokerApp().run()
