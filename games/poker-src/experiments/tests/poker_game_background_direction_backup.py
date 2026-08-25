import math
import os
import random
import sys
from dataclasses import dataclass, field

import pygame


def find_project_root(start_dir):
    current = os.path.abspath(start_dir)
    while True:
        if os.path.exists(os.path.join(current, "poker_rules.py")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            return os.path.abspath(start_dir)
        current = parent


PROJECT_ROOT = find_project_root(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from poker_flow import AppScreen, SetupController
from poker_rules import Card, PokerGame


def first_existing_dir(*relative_paths):
    for relative_path in relative_paths:
        path = os.path.join(PROJECT_ROOT, relative_path)
        if os.path.isdir(path):
            return path
    return os.path.join(PROJECT_ROOT, relative_paths[0])


WIDTH, HEIGHT = 1200, 800
FPS = 60
STARTING_STACK = 1000
SMALL_BLIND = 10
BIG_BLIND = 20
PLAYER_COUNT_OPTIONS = (2, 3, 4, 5, 6)
POKER_FONT_PATH = os.path.join(PROJECT_ROOT, "fonts", "Poker_font-Regular.ttf")
GAME_SCREEN_DIR = first_existing_dir("Game Screen", "game screen")
PROFILE_DIR = os.path.join(GAME_SCREEN_DIR, "Profiles")
CARD_DIR = os.path.join(GAME_SCREEN_DIR, "Cards")
BACKGROUND_DIR = os.path.join(GAME_SCREEN_DIR, "Background")
UI_DIR = os.path.join(GAME_SCREEN_DIR, "UI")
CARD_BASE_WIDTH = 90
CARD_BASE_HEIGHT = 145
BLEND_EDGE_FEATHER = 220
BACKGROUND_SECONDARY_FOLLOW_SPEED = 4.0
BACKGROUND_LAYER_ORDER = (
    "BG_Solid.png",
    "BG_Dots.png",
    "BG_Blend_Blue.png",
    "BG_Blend_Pink.png",
    "BG_Box.png",
    "BG_Box2.png",
    "BG_Box3.png",
    "BG_Box4.png",
    "BG_Button.png",
    "BG_Button2.png",
    "BG_Cap.png",
    "BG_Card1.png",
    "BG_Card2.png",
    "BG_Card3.png",
    "BG_Eye.png",
    "BG_Sticky.png",
    "BG_Pic.png",
)
BACKGROUND_STAGE_INTENSITIES = {
    "IDLE": 0.2,
    "PREFLOP": 0.4,
    "FLOP": 0.6,
    "TURN": 0.8,
    "RIVER": 1.0,
    "SHOWDOWN": 1.0,
    "HAND_OVER": 0.55,
}
GAME_UI_ASSETS = {
    "table": "UI_Table.png",
    "profile_card": "UI_ProfileCard.png",
    "call": "UI_Check.png",
    "raise": "UI_Raise.png",
    "raise_down": "UI_-10.png",
    "raise_up": "UI_+10.png",
    "fold": "UI_Fold.png",
    "quit": "UI_Quit.png",
    "hands": "UI_Hands.png",
    "new_hand": "UI_Deal.png",
}
ACTION_UI_LAYER_ORDER = ("call", "raise_down", "raise_up", "raise", "fold")
GAME_ACTION_BUTTON_BASE_OFFSET = pygame.Vector2(0, 10)
GAME_ACTION_BUTTON_HOVER_OFFSET = pygame.Vector2(0, 0)
GAME_ACTION_BUTTON_HOVER_SPEED = 0.24
SCREEN_SLIDE_DURATION_MS = 520
CURRENT_HAND_CARD_SCALE = 2.5
CURRENT_HAND_START_X = WIDTH // 2 - 200
CURRENT_HAND_Y = 468
CURRENT_HAND_X_SPACING = 200
CURRENT_HAND_Y_STEP = -12
CURRENT_HAND_CARD_ANGLES = (3, -5)

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


@dataclass
class MotionProfile:
    pattern: str
    velocity: pygame.Vector2
    wave_amplitude: pygame.Vector2
    wave_speed: float
    phase: float
    wrap: bool = True
    y_amplitude: float = 0.0
    y_speed: float = 0.0
    y_direction: float = 1.0


@dataclass
class BackgroundLayer:
    name: str
    image: pygame.Surface
    motion: MotionProfile
    blend_flags: int = 0
    offset: pygame.Vector2 = field(default_factory=pygame.Vector2)
    drift_offset: pygame.Vector2 = field(default_factory=pygame.Vector2)
    secondary_offset: pygame.Vector2 = field(default_factory=pygame.Vector2)


@dataclass
class ScreenTransition:
    from_screen: AppScreen
    to_screen: AppScreen
    kind: str
    elapsed_ms: int = 0
    duration_ms: int = SCREEN_SLIDE_DURATION_MS


class Button:
    def __init__(self, text, rect, color, action, image=None):
        self.text = text
        self.rect = pygame.Rect(rect)
        self.color = color
        self.action = action
        self.image = image
        self.scaled_image_cache = {}
        self.current_scale = 1.0
        self.base_scale = 1.0
        self.hover_scale = 1.08
        self.hover_speed = 0.2

    def draw(self, surface, font, offset=(0, 0)):
        mouse = pygame.mouse.get_pos()
        offset_x, offset_y = offset
        draw_rect = self.rect.move(offset_x, offset_y)
        if self.image is not None:
            target_scale = self.hover_scale if draw_rect.collidepoint(mouse) else self.base_scale
            self.current_scale += (target_scale - self.current_scale) * self.hover_speed
            image_size = (
                max(1, round(self.image.get_width() * self.current_scale)),
                max(1, round(self.image.get_height() * self.current_scale)),
            )
            if image_size not in self.scaled_image_cache:
                self.scaled_image_cache[image_size] = pygame.transform.smoothscale(self.image, image_size)
            image = self.scaled_image_cache[image_size]
            image_rect = image.get_rect(center=draw_rect.center)
            surface.blit(image, image_rect)
            return

        color = tuple(min(255, channel + 24) for channel in self.color) if draw_rect.collidepoint(mouse) else self.color
        pygame.draw.rect(surface, color, draw_rect, border_radius=7)
        pygame.draw.rect(surface, WHITE, draw_rect, width=2, border_radius=7)
        label = font.render(self.text, True, WHITE)
        surface.blit(label, label.get_rect(center=draw_rect.center))

    def clicked(self, event, offset=(0, 0)):
        offset_x, offset_y = offset
        return event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.rect.move(offset_x, offset_y).collidepoint(event.pos)


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

    def draw(self, surface, font, error=False, offset=(0, 0)):
        offset_x, offset_y = offset
        rect = self.rect.move(offset_x, offset_y)
        border = RED if error else (GOLD if self.active else MUTED)
        pygame.draw.rect(surface, BLACK, rect, border_radius=6)
        pygame.draw.rect(surface, border, rect, width=2, border_radius=6)
        label = font.render(self.text, True, WHITE)
        surface.blit(label, (rect.x + 14, rect.y + 13))


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
        self.card_back_assignments = {}
        self.scaled_image_cache = {}
        self.raise_total = BIG_BLIND * 2
        self.bot_action_due = 0
        self.name_input = TextInput((450, 520, 300, 54))
        self.title_assets = self._load_title_assets()
        self.select_assets = self._load_player_select_assets()
        self.profile_assets = self._load_profile_assets()
        self.card_assets = self._load_card_assets()
        self.card_back_assets = self._load_card_back_assets()
        self.game_background_layers = self._load_game_background_layers()
        self.background_elapsed = 0.0
        self.background_intensity = 0.35
        self.background_target_intensity = 0.35
        self.background_trajectory_angle = 0.0
        self.background_target_trajectory_angle = 0.0
        self.background_stage = None
        self.game_ui_assets = self._load_game_ui_assets()
        self.game_ui_bounds = {
            key: image.get_bounding_rect(min_alpha=16)
            for key, image in self.game_ui_assets.items()
        }
        self.game_ui_offsets = {
            key: pygame.Vector2(self._game_ui_base_offset(key))
            for key in self.game_ui_assets
        }
        self.transition: ScreenTransition | None = None
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
        path = self._asset_path(*parts)
        try:
            return pygame.image.load(path).convert_alpha()
        except pygame.error as error:
            raise SystemExit(f"Could not load image asset: {path}") from error

    def _load_optional_image(self, *parts):
        path = self._asset_path(*parts)
        try:
            return pygame.image.load(path).convert_alpha()
        except pygame.error:
            return None

    def _asset_path(self, *parts):
        path = os.path.join(*parts)
        if os.path.isabs(path):
            return path
        return os.path.join(PROJECT_ROOT, path)

    def _scaled_image(self, image, size):
        size = (int(size[0]), int(size[1]))
        cache_key = (id(image), size)
        if cache_key not in self.scaled_image_cache:
            self.scaled_image_cache[cache_key] = pygame.transform.smoothscale(image, size)
        return self.scaled_image_cache[cache_key]

    def _rotated_image(self, image, angle):
        if angle == 0:
            return image
        angle = round(angle, 2)
        cache_key = ("rotated", id(image), angle)
        if cache_key not in self.scaled_image_cache:
            self.scaled_image_cache[cache_key] = pygame.transform.rotozoom(image, angle, 1.0)
        return self.scaled_image_cache[cache_key]

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
                    image = pygame.image.load(os.path.join(folder_path, filename)).convert_alpha()
                    cards[key] = image
                except pygame.error:
                    continue
        return cards

    def _load_card_back_assets(self):
        back_dir = None
        for name in ("back", "Back"):
            candidate = os.path.join(CARD_DIR, name)
            if os.path.isdir(candidate):
                back_dir = candidate
                break
        if back_dir is None:
            return []

        backs = []
        for filename in sorted(os.listdir(back_dir)):
            if not filename.lower().endswith(".png"):
                continue
            try:
                image = pygame.image.load(os.path.join(back_dir, filename)).convert_alpha()
                backs.append(image)
            except pygame.error:
                continue
        return backs

    def _load_game_background_layers(self):
        if not os.path.isdir(BACKGROUND_DIR):
            return []

        ordered_names = [name for name in BACKGROUND_LAYER_ORDER if os.path.isfile(os.path.join(BACKGROUND_DIR, name))]
        known_names = {name.lower() for name in ordered_names}
        extra_names = sorted(
            filename
            for filename in os.listdir(BACKGROUND_DIR)
            if filename.lower().endswith((".png", ".jpg", ".jpeg")) and filename.lower() not in known_names
        )

        rng = random.Random(17)
        layers = []
        for index, filename in enumerate([*ordered_names, *extra_names]):
            path = os.path.join(BACKGROUND_DIR, filename)
            try:
                image = pygame.image.load(path).convert_alpha()
            except pygame.error:
                continue
            is_blend_layer = "blend" in filename.lower()
            if is_blend_layer:
                image = self._prepare_additive_light_layer(image)
            blend_flags = pygame.BLEND_RGB_ADD if is_blend_layer else 0
            name = os.path.splitext(filename)[0]
            motion = self._background_motion_for_layer(name, index, rng)
            layers.append(BackgroundLayer(name, image, motion, blend_flags))
        return layers

    def _background_motion_for_layer(self, name, index, rng):
        if name == "BG_Solid":
            return MotionProfile("subtle_oscillation", pygame.Vector2(), pygame.Vector2(4, 3), 0.08, 0.0, wrap=False)

        if name in {"BG_Dots", "BG_Blend_Blue", "BG_Blend_Pink"}:
            return MotionProfile(
                "subtle_oscillation",
                pygame.Vector2(),
                pygame.Vector2(rng.uniform(8.0, 20.0), rng.uniform(6.0, 16.0)),
                rng.uniform(0.035, 0.075),
                rng.uniform(0, math.tau),
                wrap=False,
            )

        direction = -1 if index % 2 else 1
        speed = 5 + index * 1.8
        velocity = pygame.Vector2(
            direction * speed,
            rng.uniform(-4.0, 4.0) + math.sin(index) * 3,
        )
        wave_amplitude = pygame.Vector2(
            rng.uniform(8.0, 28.0),
            rng.uniform(6.0, 22.0),
        )
        wave_speed = rng.uniform(0.16, 0.42)
        phase = rng.uniform(0, math.tau)

        if "Box" in name:
            return MotionProfile(
                "box_wave",
                velocity,
                wave_amplitude,
                wave_speed,
                phase,
                wrap=True,
                y_amplitude=rng.uniform(22.0, 46.0),
                y_speed=rng.uniform(0.36, 0.72),
            )

        if "Card" in name:
            direction = 1 if index % 2 else -1
            velocity = pygame.Vector2(
                direction * (speed * 1.35),
                rng.uniform(-2.0, 2.0),
            )
            y_direction = -1 if name in {"BG_Card1", "BG_Card3"} else 1
            return MotionProfile(
                "card_pulse",
                velocity,
                pygame.Vector2(rng.uniform(5.0, 13.0), 0),
                rng.uniform(0.14, 0.24),
                phase,
                wrap=True,
                y_amplitude=42.0,
                y_speed=0.12,
                y_direction=y_direction,
            )

        if name == "BG_Pic":
            velocity *= 0.45
            wave_amplitude *= 0.7

        return MotionProfile("drift", velocity, wave_amplitude, wave_speed, phase, wrap=True)

    def _prepare_additive_light_layer(self, surface):
        prepared = pygame.Surface(surface.get_size())
        width, height = surface.get_size()
        feather = max(1, min(BLEND_EDGE_FEATHER, width // 2, height // 2))

        surface.lock()
        prepared.lock()
        try:
            for y in range(height):
                y_edge = min(y, height - 1 - y)
                y_factor = min(1.0, y_edge / feather)
                for x in range(width):
                    red, green, blue, alpha = surface.get_at((x, y))
                    if alpha == 0:
                        prepared.set_at((x, y), (0, 0, 0))
                        continue

                    x_edge = min(x, width - 1 - x)
                    edge_factor = min(y_factor, min(1.0, x_edge / feather))
                    intensity = (alpha / 255) * edge_factor
                    prepared.set_at(
                        (x, y),
                        (
                            round(red * intensity),
                            round(green * intensity),
                            round(blue * intensity),
                        ),
                    )
        finally:
            prepared.unlock()
            surface.unlock()

        return prepared.convert()

    def _load_game_ui_assets(self):
        assets = {}
        if not os.path.isdir(UI_DIR):
            return assets

        for key, filename in GAME_UI_ASSETS.items():
            path = os.path.join(UI_DIR, filename)
            try:
                assets[key] = pygame.image.load(path).convert_alpha()
            except pygame.error:
                continue
        return assets

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
        if self.transition is not None:
            return
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
            from_screen = self.flow.screen
            self.flow.choose_single_player()
            self.name_input.clear()
            self._start_transition(from_screen, self.flow.screen, "horizontal")
        elif self.buttons["multi"].clicked(event):
            from_screen = self.flow.screen
            self.flow.choose_multiplayer()
            self._start_transition(from_screen, self.flow.screen, "horizontal")
        elif self.buttons["how_to"].clicked(event):
            self.flow.show_how_to_play(return_to=AppScreen.TITLE)

    def _handle_player_count_event(self, event):
        if self.buttons["back"].clicked(event):
            self.flow.back_to_title()
            return
        for count in PLAYER_COUNT_OPTIONS:
            if self.buttons[f"players_{count}"].clicked(event):
                from_screen = self.flow.screen
                self.flow.choose_player_count(count)
                self.name_input.clear()
                self._start_transition(from_screen, self.flow.screen, "vertical_setup")
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
        if self._game_button_clicked("quit", event):
            self.flow.back_to_title()
            self.game = None
            return
        if self._game_button_clicked("hands", event):
            self.flow.show_how_to_play(return_to=AppScreen.TABLE)
            return
        if self.game is None:
            return
        if self.game.street in ("IDLE", "HAND_OVER"):
            if self._game_button_clicked("new_hand", event):
                self.game.start_hand()
                self._sync_raise_total()
            return

        current = self.game.current_player
        if current.is_bot:
            return

        legal_actions = self.game.legal_actions()
        if self._game_button_clicked("fold", event) and "fold" in legal_actions:
            self.game.fold()
            self._sync_raise_total()
        elif self._game_button_clicked("raise", event) and "raise" in legal_actions:
            self.game.raise_to(self.raise_total)
            self._sync_raise_total()
        elif self._game_button_clicked("raise_up", event) and "raise" in legal_actions:
            self.raise_total = min(self._max_raise_to(), self.raise_total + 10)
        elif self._game_button_clicked("raise_down", event) and "raise" in legal_actions:
            self.raise_total = max(self._min_raise_to(), self.raise_total - 10)
        elif self._game_button_clicked("call", event) and legal_actions:
            self.game.check_or_call()
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

    def _start_transition(self, from_screen, to_screen, kind):
        self.transition = ScreenTransition(from_screen, to_screen, kind)

    def _update(self, dt):
        if self.transition is not None:
            self.transition.elapsed_ms += dt
            if self.transition.elapsed_ms >= self.transition.duration_ms:
                self.transition = None
            return

        if self.flow.screen != AppScreen.TABLE or self.game is None:
            return
        self._update_game_background(dt)
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

    def _update_game_background(self, dt):
        self._sync_background_stage()
        seconds = dt / 1000
        self.background_elapsed += seconds
        self.background_intensity += (self.background_target_intensity - self.background_intensity) * min(1.0, seconds * 3.0)
        self.background_trajectory_angle += (
            self.background_target_trajectory_angle - self.background_trajectory_angle
        ) * min(1.0, seconds * 1.6)

        speed_multiplier = 0.35 + self.background_intensity * 1.65
        drift_multiplier = 0.45 + self.background_intensity * 1.1
        for layer in self.game_background_layers:
            layer.offset = self._background_layer_offset(layer, seconds, speed_multiplier, drift_multiplier)

    def _sync_background_stage(self):
        street = self.game.street if self.game is not None else "IDLE"
        if street == self.background_stage:
            return

        self.background_stage = street
        self.background_target_intensity = BACKGROUND_STAGE_INTENSITIES.get(street, 0.35)
        self._advance_background_trajectory()

    def _background_layer_offset(self, layer, seconds, speed_multiplier, drift_multiplier):
        motion = layer.motion

        if motion.pattern == "subtle_oscillation":
            radius_multiplier = 0.82 + self.background_intensity * 0.25
            x = math.sin(self.background_elapsed * motion.wave_speed + motion.phase) * motion.wave_amplitude.x
            y = math.cos(self.background_elapsed * motion.wave_speed * 0.73 + motion.phase) * motion.wave_amplitude.y
            return pygame.Vector2(x, y) * radius_multiplier

        if motion.pattern == "box_wave":
            drift = self._background_trajectory_vector(motion.velocity.x, motion.velocity.y)
            layer.drift_offset += drift * seconds * speed_multiplier
            self._wrap_background_drift_offset(layer)
            wave_x = math.sin(self.background_elapsed * motion.wave_speed + motion.phase) * motion.wave_amplitude.x
            gentle_y = math.cos(self.background_elapsed * motion.wave_speed * 0.85 + motion.phase) * motion.wave_amplitude.y
            wave_speed_multiplier = 0.55 + self.background_intensity * 1.75
            wave_y = math.sin(self.background_elapsed * motion.y_speed * wave_speed_multiplier + motion.phase) * motion.y_amplitude
            wave = pygame.Vector2(wave_x, gentle_y) * drift_multiplier
            secondary = self._smooth_background_secondary_offset(
                layer,
                self._background_perpendicular_to(drift) * wave_y,
                seconds,
            )
            return layer.drift_offset + wave + secondary

        if motion.pattern == "card_pulse":
            drift = self._background_trajectory_vector(motion.velocity.x, motion.velocity.y)
            layer.drift_offset += drift * seconds * (speed_multiplier * 1.28)
            self._wrap_background_drift_offset(layer)
            wave_x = math.sin(self.background_elapsed * motion.wave_speed + motion.phase) * motion.wave_amplitude.x * drift_multiplier
            pulse_speed_multiplier = 0.55 + self.background_intensity * 1.75
            pulse_y = motion.y_direction * self._background_ease_pulse_y(
                self.background_elapsed * motion.y_speed * pulse_speed_multiplier,
                motion.y_amplitude,
            )
            secondary = self._smooth_background_secondary_offset(
                layer,
                self._background_perpendicular_to(drift) * pulse_y,
                seconds,
            )
            return layer.drift_offset + pygame.Vector2(wave_x, 0) + secondary

        drift = self._background_trajectory_vector(motion.velocity.x, motion.velocity.y)
        layer.drift_offset += drift * seconds * speed_multiplier
        self._wrap_background_drift_offset(layer)
        wave_x = math.sin(self.background_elapsed * motion.wave_speed + motion.phase) * motion.wave_amplitude.x
        wave_y = math.cos(self.background_elapsed * motion.wave_speed * 0.85 + motion.phase) * motion.wave_amplitude.y
        return layer.drift_offset + pygame.Vector2(wave_x, wave_y) * drift_multiplier

    def _advance_background_trajectory(self):
        self.background_trajectory_angle = self._normalized_background_angle(self.background_trajectory_angle)
        self.background_target_trajectory_angle = self.background_trajectory_angle + math.pi / 2

    def _normalized_background_angle(self, angle):
        return math.atan2(math.sin(angle), math.cos(angle))

    def _wrap_background_drift_offset(self, layer):
        if not layer.motion.wrap:
            return
        image_w, image_h = layer.image.get_size()
        layer.drift_offset.update(
            self._wrapped_offset(layer.drift_offset.x, image_w),
            self._wrapped_offset(layer.drift_offset.y, image_h),
        )

    def _smooth_background_secondary_offset(self, layer, target, seconds):
        follow = min(1.0, seconds * BACKGROUND_SECONDARY_FOLLOW_SPEED)
        layer.secondary_offset += (target - layer.secondary_offset) * follow
        return layer.secondary_offset

    def _background_trajectory_vector(self, x, y):
        return pygame.Vector2(x, y).rotate_rad(self.background_trajectory_angle)

    def _background_perpendicular_to(self, vector):
        if vector.length_squared() == 0:
            return pygame.Vector2(0, 1)
        direction = vector.normalize()
        return pygame.Vector2(-direction.y, direction.x)

    def _background_ease_pulse_y(self, cycle_position, amplitude):
        position = cycle_position % 1.0
        if position < 0.5:
            eased = self._ease_out_cubic(position * 2)
            return amplitude - amplitude * 2 * eased

        eased = self._ease_out_cubic((position - 0.5) * 2)
        return -amplitude + amplitude * 2 * eased

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
        if self.transition is not None:
            self._draw_transition()
            pygame.display.flip()
            return

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

    def _draw_transition(self):
        progress = min(1.0, self.transition.elapsed_ms / self.transition.duration_ms)
        eased = self._ease_out_cubic(progress)

        if self.transition.kind == "horizontal":
            source_x = round(-WIDTH * eased)
            target_x = round(WIDTH * (1 - eased))
            self._draw_screen(self.transition.from_screen, offset=(source_x, 0))
            self._draw_screen(self.transition.to_screen, offset=(target_x, 0))
            return

        if self.transition.kind == "vertical_setup":
            source_y = round(-HEIGHT * eased)
            target_y = round(HEIGHT * (1 - eased))
            self._draw_player_select_background()
            self._draw_player_count(offset=(0, source_y), draw_background=False)
            self._draw_name_entry(offset=(0, target_y), draw_background=False)
            return

        self._draw_screen(self.transition.to_screen)

    def _draw_screen(self, screen, offset=(0, 0)):
        if screen == AppScreen.TITLE:
            self._draw_title(offset=offset)
        elif screen == AppScreen.PLAYER_COUNT:
            self._draw_player_count(offset=offset)
        elif screen == AppScreen.NAME_ENTRY:
            self._draw_name_entry(offset=offset)
        elif screen == AppScreen.HOW_TO_PLAY:
            self._draw_how_to_play(offset=offset)
        elif screen == AppScreen.TABLE:
            self._draw_table()

    def _ease_out_cubic(self, value):
        return 1 - (1 - value) ** 3

    def _draw_title(self, offset=(0, 0)):
        offset_x, offset_y = offset
        self.screen.blit(self.title_assets["bg"], (offset_x, offset_y))
        self.screen.blit(self.title_assets["cards"], (offset_x, offset_y))
        self._draw_title_letters(offset=offset)
        self.screen.blit(self.title_assets["folder"], (offset_x, offset_y))
        self.buttons["single"].draw(self.screen, self.font_md, offset=offset)
        self.buttons["multi"].draw(self.screen, self.font_md, offset=offset)
        self.buttons["how_to"].draw(self.screen, self.font_md, offset=offset)
        self.screen.blit(self.title_assets["texas"], (20 + offset_x, 70 + offset_y))
        self.screen.blit(self.title_assets["holdem"], (140 + offset_x, 155 + offset_y))

    def _draw_title_letters(self, offset=(0, 0)):
        offset_x, offset_y = offset
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
            self.screen.blit(letter, (start_x + x_offset + offset_x, y + offset_y))
            x_offset += letter.get_width() - 40

    def _draw_player_count(self, offset=(0, 0), draw_background=True):
        offset_x, offset_y = offset
        if draw_background:
            self._draw_player_select_background(offset=(offset_x, 0))
        self.buttons["back"].draw(self.screen, self.font_sm, offset=offset)
        if self.select_assets["title"] is not None:
            title_image = self.select_assets["title"]
            title_rect = title_image.get_rect(midtop=(WIDTH // 2, 0))
            title_rect.move_ip(offset_x, offset_y)
            self.screen.blit(title_image, title_rect)
        else:
            prompt = self.font_md.render("Choose number of players", True, WHITE)
            self.screen.blit(prompt, prompt.get_rect(center=(WIDTH // 2 + offset_x, 90 + offset_y)))
        for count in PLAYER_COUNT_OPTIONS:
            self.buttons[f"players_{count}"].draw(self.screen, self.font_lg, offset=offset)
        self.buttons["players_funny"].draw(self.screen, self.font_lg, offset=offset)

    def _draw_name_entry(self, offset=(0, 0), draw_background=True):
        offset_x, offset_y = offset
        if draw_background:
            self._draw_player_select_background(offset=(offset_x, 0))
        self.buttons["back"].draw(self.screen, self.font_sm, offset=offset)
        if self.select_assets["enter_name"] is not None:
            title = self.select_assets["enter_name"]
            self.screen.blit(title, title.get_rect(center=(WIDTH // 2 + offset_x, 150 + offset_y)))
        else:
            title = self.font_xl.render("NAME ENTRY", True, GOLD)
            self.screen.blit(title, title.get_rect(center=(WIDTH // 2 + offset_x, 130 + offset_y)))
        prompt = self.font_md.render(self.flow.current_name_prompt, True, WHITE)
        self.screen.blit(prompt, prompt.get_rect(center=(WIDTH // 2 + offset_x, 275 + offset_y)))
        self._draw_entered_name_boxes(offset=offset)
        self.name_input.draw(self.screen, self.font_md, error=bool(self.flow.name_error), offset=offset)
        self.buttons["confirm_name"].draw(self.screen, self.font_md, offset=offset)
        if self.flow.name_error:
            error = self.font_sm.render(self.flow.name_error, True, RED)
            self.screen.blit(error, error.get_rect(center=(WIDTH // 2 + offset_x, 735 + offset_y)))

    def _draw_player_select_background(self, offset=(0, 0)):
        offset_x, offset_y = offset
        if self.select_assets["bg"] is not None:
            self.screen.blit(self.select_assets["bg"], (offset_x, offset_y))
        else:
            self.screen.fill(BG)

    def _draw_entered_name_boxes(self, offset=(0, 0)):
        offset_x, offset_y = offset
        names = self.flow.entered_names
        if not names:
            hint = self.font_sm.render("Entered names will appear here", True, MUTED)
            self.screen.blit(hint, hint.get_rect(center=(WIDTH // 2 + offset_x, 400 + offset_y)))
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
            rect = pygame.Rect(
                start_x + col * (box_w + gap_x) + offset_x,
                start_y + row * (box_h + gap_y) + offset_y,
                box_w,
                box_h,
            )
            pygame.draw.rect(self.screen, PANEL, rect, border_radius=7)
            pygame.draw.rect(self.screen, GOLD, rect, width=2, border_radius=7)
            label = self.font_md.render(name, True, WHITE)
            self.screen.blit(label, label.get_rect(center=rect.center))

    def _draw_how_to_play(self, offset=(0, 0)):
        offset_x, offset_y = offset
        self.buttons["back"].draw(self.screen, self.font_sm, offset=offset)
        title = self.font_xl.render("HOW TO PLAY", True, GOLD)
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2 + offset_x, 180 + offset_y)))
        for index, line in enumerate(HOW_TO_PLAY_LINES):
            text = self.font_md.render(line, True, WHITE)
            self.screen.blit(text, (220 + offset_x, 280 + index * 48 + offset_y))

    def _draw_table(self):
        if self.game is None:
            return
        self._draw_game_background()
        if not self._draw_game_ui_asset("table"):
            self._draw_chamfered_table()
        self._draw_status()
        self._draw_community_cards()
        self._draw_table_players()
        self._draw_current_player_panel()
        self._draw_controls()
        self._draw_top_table_buttons()

    def _draw_game_background(self):
        screen_rect = self.screen.get_rect()
        for layer in self.game_background_layers:
            if layer.motion.wrap:
                self._draw_wrapped_background_layer(screen_rect, layer)
            else:
                self._draw_centered_layer(layer.image, layer.offset, layer.blend_flags)

    def _draw_wrapped_background_layer(self, screen_rect, layer):
        image_w, image_h = layer.image.get_size()
        offset_x = self._wrapped_offset(layer.offset.x, image_w)
        offset_y = self._wrapped_offset(layer.offset.y, image_h)

        for tile_y in (-1, 0, 1):
            for tile_x in (-1, 0, 1):
                center = (
                    WIDTH // 2 + round(offset_x + tile_x * image_w),
                    HEIGHT // 2 + round(offset_y + tile_y * image_h),
                )
                rect = layer.image.get_rect(center=center)
                if rect.colliderect(screen_rect):
                    self.screen.blit(layer.image, rect, special_flags=layer.blend_flags)

    def _wrapped_offset(self, value, span):
        return ((value + span / 2) % span) - span / 2

    def _draw_centered_layer(self, image, offset=(0, 0), special_flags=0):
        offset_x, offset_y = offset
        rect = image.get_rect(center=(WIDTH // 2 + round(offset_x), HEIGHT // 2 + round(offset_y)))
        self.screen.blit(image, rect, special_flags=special_flags)
        return rect

    def _draw_game_ui_asset(self, key):
        image = self.game_ui_assets.get(key)
        if image is None:
            return False
        offset = self._game_ui_offset(key)
        self._draw_centered_layer(image, offset)
        return True

    def _game_ui_base_offset(self, key):
        if key in ACTION_UI_LAYER_ORDER:
            return GAME_ACTION_BUTTON_BASE_OFFSET
        return pygame.Vector2()

    def _game_ui_hover_offset(self, key):
        if key in ACTION_UI_LAYER_ORDER:
            return GAME_ACTION_BUTTON_HOVER_OFFSET
        return self._game_ui_base_offset(key)

    def _game_ui_offset(self, key):
        if key not in ACTION_UI_LAYER_ORDER:
            return self._game_ui_base_offset(key)

        current = self.game_ui_offsets.setdefault(key, pygame.Vector2(self._game_ui_base_offset(key)))
        mouse_pos = pygame.mouse.get_pos()
        hovering = self._game_ui_asset_hit(key, mouse_pos, current) or self._game_ui_asset_hit(key, mouse_pos, self._game_ui_base_offset(key))
        target = self._game_ui_hover_offset(key) if hovering else self._game_ui_base_offset(key)
        current += (target - current) * GAME_ACTION_BUTTON_HOVER_SPEED
        return current

    def _game_ui_asset_hit(self, key, position, offset=None):
        image = self.game_ui_assets.get(key)
        if image is None:
            return False
        if offset is None:
            offset = self.game_ui_offsets.get(key, self._game_ui_base_offset(key))
        image_rect = image.get_rect(center=(WIDTH // 2 + round(offset.x), HEIGHT // 2 + round(offset.y)))
        hit_rect = self.game_ui_bounds.get(key, image.get_rect()).move(image_rect.topleft)
        return hit_rect.collidepoint(position)

    def _game_button_clicked(self, key, event):
        if event.type != pygame.MOUSEBUTTONUP or event.button != 1:
            return False
        if key in self.game_ui_assets:
            current_offset = self.game_ui_offsets.get(key, self._game_ui_base_offset(key))
            return (
                self._game_ui_asset_hit(key, event.pos, current_offset)
                or self._game_ui_asset_hit(key, event.pos, self._game_ui_base_offset(key))
                or self._game_ui_asset_hit(key, event.pos, self._game_ui_hover_offset(key))
            )
        return self.buttons[key].clicked(event)

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
            2: [(320, 300), (680, 52)],
            3: [(320, 300), (480, 52), (780, 52)],
            4: [(320, 300), (380, 130), (580, 52), (780, 52)],
            5: [(320, 300), (380, 130), (580, 52), (780, 52), (980, 52)],
            6: [(320, 310), (360, 150), (490, 52), (660, 52), (830, 52), (1000, 52)],
        }
        if count in anchors:
            return anchors[count][index]

        table_path = self._chamfered_rect_points(150, 56, 900, 342, 105)
        return table_path[index % len(table_path)]

    def _draw_current_player_panel(self):
        if self.game.street in ("IDLE",) or not self.game.players:
            return
        player = self.game.current_player
        if not self._draw_game_ui_asset("profile_card"):
            panel = pygame.Rect(24, 462, 390, 294)
            pygame.draw.rect(self.screen, PANEL, panel, border_radius=8)
            pygame.draw.rect(self.screen, GOLD, panel, width=2, border_radius=8)

        stack = self.font_md.render("OUT" if player.eliminated else f"{player.stack}", True, GOLD)
        status = self.font_sm.render(self._player_status(player), True, MUTED)
        self.screen.blit(stack, stack.get_rect(center=(130, 502)))
        self.screen.blit(status, status.get_rect(center=(130, 532)))

        self._draw_profile(self.game.current_player_index, (130, 625), 200, GOLD, player.name)

        name = self.font_lg.render(player.name, True, WHITE)
        self.screen.blit(name, name.get_rect(center=(130, 725)))

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
            image = self._scaled_image(self.player_profiles[index], (size, size))
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
        for index, card in enumerate(player.hand):
            x = CURRENT_HAND_START_X + index * CURRENT_HAND_X_SPACING
            y = CURRENT_HAND_Y + index * CURRENT_HAND_Y_STEP
            angle = CURRENT_HAND_CARD_ANGLES[index % len(CURRENT_HAND_CARD_ANGLES)]
            if show_cards:
                self._draw_card(card, x, y, CURRENT_HAND_CARD_SCALE, True, angle=angle)
            else:
                self._draw_card_back(x, y, CURRENT_HAND_CARD_SCALE, angle=angle)

    def _draw_controls(self):
        if self.game.street in ("IDLE", "HAND_OVER"):
            if not self._draw_game_ui_asset("new_hand"):
                self.buttons["new_hand"].draw(self.screen, self.font_sm)
            return
        current = self.game.current_player
        if current.is_bot:
            thinking = self.font_md.render("Thinking...", True, MUTED)
            self.screen.blit(thinking, thinking.get_rect(center=(1048, 615)))
            return

        legal_actions = self.game.legal_actions()
        for key in ACTION_UI_LAYER_ORDER:
            if key in ("raise", "raise_down", "raise_up") and "raise" not in legal_actions:
                continue
            if key == "fold" and "fold" not in legal_actions:
                continue
            if key == "call" and not legal_actions:
                continue
            if key not in self.game_ui_assets:
                self.buttons[key].draw(self.screen, self.font_sm)
            else:
                self._draw_game_ui_asset(key)

        if "raise" in legal_actions:
            raise_offset = self.game_ui_offsets.get("raise", self._game_ui_base_offset("raise"))
            amount = self.font_md.render(f"{self.raise_total}", True, GOLD)
            self.screen.blit(amount, amount.get_rect(center=(1048 + round(raise_offset.x), 580 + round(raise_offset.y))))

    def _draw_top_table_buttons(self):
        for key in ("quit", "hands"):
            if not self._draw_game_ui_asset(key):
                self.buttons[key].draw(self.screen, self.font_sm)

    def _draw_card(self, card: Card, x, y, scale, face_up, angle=0):
        if not face_up:
            self._draw_card_back(x, y, scale, angle=angle)
            return

        sprite = self.card_assets.get(self._card_asset_key(card))
        if sprite is not None:
            w, h = int(CARD_BASE_WIDTH * scale), int(CARD_BASE_HEIGHT * scale)
            image = self._scaled_image(sprite, (w, h))
            self._blit_card_image(image, x, y, angle)
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

    def _draw_card_back(self, x, y, scale, angle=0):
        w, h = int(CARD_BASE_WIDTH * scale), int(CARD_BASE_HEIGHT * scale)
        sprite = self._card_back_for_slot(x, y, scale)
        if sprite is not None:
            image = self._scaled_image(sprite, (w, h))
            self._blit_card_image(image, x, y, angle)
            return

        rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(self.screen, BLACK, rect.move(4, 4), border_radius=5)
        pygame.draw.rect(self.screen, RED, rect, border_radius=5)
        pygame.draw.rect(self.screen, WHITE, rect, width=2, border_radius=5)
        inset = rect.inflate(-14 * scale, -14 * scale)
        pygame.draw.rect(self.screen, (130, 26, 36), inset, width=2, border_radius=4)

    def _blit_card_image(self, image, x, y, angle=0):
        if angle == 0:
            self.screen.blit(image, (x, y))
            return

        original_rect = image.get_rect(topleft=(x, y))
        rotated = self._rotated_image(image, angle)
        self.screen.blit(rotated, rotated.get_rect(center=original_rect.center))

    def _card_back_for_slot(self, x, y, scale):
        if not self.card_back_assets:
            return None
        slot = (round(x), round(y), round(scale * 100))
        if slot not in self.card_back_assignments:
            self.card_back_assignments[slot] = self.rng.randrange(len(self.card_back_assets))
        return self.card_back_assets[self.card_back_assignments[slot]]


if __name__ == "__main__":
    PokerApp().run()
