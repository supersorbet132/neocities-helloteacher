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
PHASE_BANNER_UI_KEYS = {
    "PREFLOP": "phase_preflop",
    "FLOP": "phase_flop",
    "TURN": "phase_turn",
    "RIVER": "phase_river",
    "HAND_OVER": "phase_hand_over",
}
PHASE_BANNER_ARC_MS = 1800
PHASE_BANNER_START_OFFSET = pygame.Vector2(-40, -350)
PHASE_BANNER_BOTTOM_OFFSET = pygame.Vector2(26, 0)
PHASE_BANNER_END_OFFSET = pygame.Vector2(92, -350)
TABLE_ENTER_TRANSITION_MS = 1260
TABLE_EXIT_TRANSITION_MS = 1600
TABLE_UI_ENTRY_MS = 920
TABLE_BACKGROUND_ENTRY_MS = 1500
TABLE_TRANSITION_TRAVEL_DISTANCE = int(WIDTH * 1.5)
TABLE_EXIT_TRANSITION_TRAVEL_DISTANCE = WIDTH * 2
TABLE_BACKGROUND_READY_LAYERS = {"BG_Solid", "BG_Dots", "BG_Blend_Blue", "BG_Blend_Pink"}
TABLE_BACKGROUND_ENTRY_DISTANCE = 1350
TABLE_ENTRY_OFFSETS = {
    "table_top": pygame.Vector2(0, -HEIGHT),
    "bottom_panel": pygame.Vector2(0, HEIGHT),
    "left_buttons": pygame.Vector2(-WIDTH, 0),
    "deal_button": pygame.Vector2(0, -HEIGHT),
}
GAME_UI_BASE_OFFSETS = {
    "profile_card": pygame.Vector2(0, 0),
}
ACTION_BUTTON_SLIDE_MS = 360
CURRENT_HAND_HOVER_MS = 180
CURRENT_HAND_HOVER_OFFSET = pygame.Vector2(0, -10)
CURRENT_PLAYER_PANEL_SWITCH_MS = 360
CURRENT_PLAYER_PANEL_SWITCH_OFFSET = pygame.Vector2(0, 430)
GAME_UI_HOVER_SPEED = 0.24
GAME_UI_HOVER_OFFSETS = {
    "quit": pygame.Vector2(10, 0),
    "hands": pygame.Vector2(10, 0),
    "new_hand": pygame.Vector2(0, 10),
    "call": pygame.Vector2(0, -10),
    "raise_down": pygame.Vector2(0, -10),
    "raise_up": pygame.Vector2(0, -10),
    "raise": pygame.Vector2(0, -10),
    "fold": pygame.Vector2(0, -10),
}
SETUP_QUIT_HOVER_OFFSET = pygame.Vector2(10, 0)
SETUP_QUIT_HOVER_SPEED = GAME_UI_HOVER_SPEED
SETUP_QUIT_SLIDE_MS = 360
SETUP_QUIT_SLIDE_OFFSET = pygame.Vector2(-WIDTH, 0)
ACTION_BUTTON_OFFSETS = {
    "call": pygame.Vector2(0, 360),
    "raise_down": pygame.Vector2(0, 360),
    "raise_up": pygame.Vector2(0, 360),
    "raise": pygame.Vector2(0, 360),
    "fold": pygame.Vector2(0, 360),
    "new_hand": pygame.Vector2(0, -300),
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
    "phase_preflop": "UI_Preflop.png",
    "phase_flop": "UI_Flop.png",
    "phase_turn": "UI_Turn.png",
    "phase_river": "UI_River.png",
    "phase_hand_over": "UI_HandOver.png",
    "transition": "UI_Transition.png",
}
ACTION_UI_LAYER_ORDER = ("call", "raise_down", "raise_up", "raise", "fold")
ANIMATED_ACTION_KEYS = (*ACTION_UI_LAYER_ORDER, "new_hand")
GAME_UI_BUTTON_LAYER_ORDER = ("new_hand", *ACTION_UI_LAYER_ORDER, "quit", "hands")
GAME_ACTION_BUTTON_BASE_OFFSET = pygame.Vector2(0, 10)
GAME_UI_OUTLINE_RADIUS = 4
SCREEN_SLIDE_DURATION_MS = 520
BOT_THINK_MS_RANGE = (1000, 2000)
TITLE_BUTTON_KEYS = ("single", "multi", "how_to")
HOW_TO_ZOOM_MS = 900
HOW_TO_PANEL_SLIDE_MS = 720
HOW_TO_BACK_SLIDE_MS = SETUP_QUIT_SLIDE_MS
HOW_TO_BACKGROUND_MONITOR_RECT = pygame.Rect(400, 294, 646, 427)
HOW_TO_BACKGROUND_SCALE_MULTIPLIER = 1.0
HOW_TO_BACKGROUND_OFFSET = pygame.Vector2(0, 0)
HOW_TO_ZOOM_START_SCALE_MULTIPLIER = 1.0
HOW_TO_PANEL_START_OFFSET = pygame.Vector2(0, -HEIGHT-50)
HOW_TO_PANEL_FINAL_OFFSET = pygame.Vector2(0, 0)
HOW_TO_BACK_SLIDE_OFFSET = pygame.Vector2(-WIDTH, 0)
HOW_TO_BACK_HOVER_OFFSET = pygame.Vector2(10, 0)
HOW_TO_BACK_HOVER_SPEED = GAME_UI_HOVER_SPEED
CURSOR_PARALLAX_SMOOTHING = 0.12
TITLE_CARDS_PARALLAX_STRENGTH = pygame.Vector2(-28, -18)
HOW_TO_PANEL_PARALLAX_STRENGTH = pygame.Vector2(-22, -16)
TITLE_LETTER_WAVE_AMPLITUDE = 16
TITLE_LETTER_WAVE_SPEED = 2.4
TITLE_LETTER_WAVE_PHASE_STEP = 0.72
TITLE_WORD_HOVER_SCALE = 1.08
TITLE_WORD_HOVER_SPEED = 0.2
CURRENT_HAND_CARD_SCALE = 2.5
CURRENT_HAND_START_X = WIDTH // 2 - 310
CURRENT_HAND_Y = 450
CURRENT_HAND_X_SPACING = 200
CURRENT_HAND_Y_STEP = 25
CURRENT_HAND_CARD_ANGLES = (-5, -15)
COMMUNITY_CARD_SCALE = 1.0
COMMUNITY_CARD_ROW_CENTER = pygame.Vector2(WIDTH // 2+70, 350)
COMMUNITY_CARD_GAP = 5
COMMUNITY_CARD_X_JITTER = 8
COMMUNITY_CARD_Y_JITTER = 7
COMMUNITY_CARD_ROTATION_RANGE = (-5.0, 5.0)
COMMUNITY_CARD_REVEAL_MS = 320
COMMUNITY_CARD_REVEAL_SWING_DEGREES = 9.0

BG = (17, 19, 24)
PANEL = (30, 34, 42)
PANEL_LIGHT = (45, 51, 62)
WHITE = (245, 245, 240)
MUTED = (170, 176, 186)
BLACK = (10, 10, 12)
GOLD = (232, 190, 82)
RED = (194, 55, 58)
BLUE = (62, 110, 190)
GREEN = (48, 150, 92)

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
class PhaseBannerAnimation:
    street: str
    elapsed_ms: int = 0


@dataclass
class CommunityCardSlot:
    center: pygame.Vector2
    angle: float


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
        self.silhouette_cache = {}
        self.outline_cache = {}
        self.current_scale = 1.0
        self.base_scale = 1.0
        self.hover_scale = 1.08
        self.hover_speed = 0.2

    def draw(self, surface, font, offset=(0, 0), hovered=None, pressed=False, outline=False, outline_radius=4):
        mouse = pygame.mouse.get_pos()
        offset_x, offset_y = offset
        draw_rect = self.rect.move(offset_x, offset_y)
        is_hovered = draw_rect.collidepoint(mouse) if hovered is None else hovered
        if self.image is not None:
            target_scale = self.hover_scale if is_hovered else self.base_scale
            self.current_scale += (target_scale - self.current_scale) * self.hover_speed
            image_size = (
                max(1, round(self.image.get_width() * self.current_scale)),
                max(1, round(self.image.get_height() * self.current_scale)),
            )
            if image_size not in self.scaled_image_cache:
                self.scaled_image_cache[image_size] = pygame.transform.smoothscale(self.image, image_size)
            image = self.scaled_image_cache[image_size]
            image_rect = image.get_rect(center=draw_rect.center)
            if outline and is_hovered and not pressed:
                outline_image = self._outline_surface(image, outline_radius)
                surface.blit(outline_image, image_rect.move(-outline_radius, -outline_radius))
            if pressed:
                surface.blit(self._silhouette_surface(image), image_rect)
            else:
                surface.blit(image, image_rect)
            return

        if pressed:
            color = WHITE
            text_color = BLACK
        else:
            color = tuple(min(255, channel + 24) for channel in self.color) if is_hovered else self.color
            text_color = WHITE
        pygame.draw.rect(surface, color, draw_rect, border_radius=7)
        pygame.draw.rect(surface, WHITE, draw_rect, width=2, border_radius=7)
        label = font.render(self.text, True, text_color)
        surface.blit(label, label.get_rect(center=draw_rect.center))

    def _silhouette_surface(self, image):
        cache_key = id(image)
        if cache_key not in self.silhouette_cache:
            mask = pygame.mask.from_surface(image, 16)
            self.silhouette_cache[cache_key] = mask.to_surface(
                setcolor=(255, 255, 255, 255),
                unsetcolor=(0, 0, 0, 0),
            ).convert_alpha()
        return self.silhouette_cache[cache_key]

    def _outline_surface(self, image, radius):
        cache_key = (id(image), radius)
        if cache_key not in self.outline_cache:
            silhouette = self._silhouette_surface(image)
            outline = pygame.Surface(
                (image.get_width() + radius * 2, image.get_height() + radius * 2),
                pygame.SRCALPHA,
            )
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    if dx == 0 and dy == 0:
                        continue
                    if dx * dx + dy * dy <= radius * radius:
                        outline.blit(silhouette, (dx + radius, dy + radius))
            self.outline_cache[cache_key] = outline.convert_alpha()
        return self.outline_cache[cache_key]

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
        self.app_time_ms = 0
        self.rng = random.Random()
        self.flow = SetupController(single_player_total=4)
        self.game: PokerGame | None = None
        self.player_profiles = []
        self.card_back_assignments = {}
        self.scaled_image_cache = {}
        self.raise_total = BIG_BLIND * 2
        self.bot_action_due = 0
        self.table_scene_age_ms = TABLE_UI_ENTRY_MS
        self.action_button_progress = {key: 0.0 for key in ANIMATED_ACTION_KEYS}
        self.game_ui_hover_progress = {key: 0.0 for key in GAME_UI_HOVER_OFFSETS}
        self.hovered_game_ui_key = None
        self.pressed_game_ui_key = None
        self.released_game_ui_key = None
        self.game_ui_outline_cache = {}
        self.game_ui_silhouette_cache = {}
        self.title_hover_progress = {"texas": 0.0, "holdem": 0.0}
        self.title_cards_parallax_offset = pygame.Vector2()
        self.pressed_title_button_key = None
        self.pressed_button_action = None
        self.pressed_setup_quit = False
        self.setup_quit_hovered = False
        self.how_to_state = None
        self.how_to_elapsed_ms = 0
        self.how_to_source_screen = AppScreen.TITLE
        self.how_to_source_surface = None
        self.how_to_scene_surface = None
        self.how_to_back_progress = 0.0
        self.how_to_back_hover_progress = 0.0
        self.how_to_back_hovered = False
        self.how_to_back_pressed = False
        self.how_to_panel_parallax_offset = pygame.Vector2()
        self.current_player_panel_progress = 1.0
        self.current_player_panel_phase = "idle"
        self.displayed_current_player_index = None
        self.displayed_current_hand_signature = None
        self.pending_current_player_index = None
        self.setup_quit_progress = 0.0
        self.setup_quit_hover_progress = 0.0
        self.current_hand_hover_progress = [0.0, 0.0]
        self.pending_table_exit = False
        self.pending_setup_back = False
        self.name_input = TextInput((450, 520, 300, 54))
        self.title_assets = self._load_title_assets()
        self.select_assets = self._load_player_select_assets()
        select_quit = self.select_assets.get("quit")
        self.setup_quit_bounds = (
            select_quit.get_bounding_rect(min_alpha=16)
            if select_quit is not None
            else pygame.Rect(40, 40, 120, 44)
        )
        self.how_to_back_bounds = self.title_assets["how_to_back"].get_bounding_rect(min_alpha=16)
        self.profile_assets = self._load_profile_assets()
        self.card_assets = self._load_card_assets()
        self.card_back_assets = self._load_card_back_assets()
        self.community_card_slots = []
        self.community_cards_seen = 0
        self.community_card_reveal_ms = {}
        self.game_background_layers = self._load_game_background_layers()
        self.background_elapsed = 0.0
        self.background_intensity = 0.35
        self.background_target_intensity = 0.35
        self.background_trajectory_angle = 0.0
        self.background_target_trajectory_angle = 0.0
        self.background_stage = None
        self.phase_banner_seen_street = None
        self.phase_banner_animation: PhaseBannerAnimation | None = None
        self.game_ui_assets = self._load_game_ui_assets()
        self.game_ui_bounds = {
            key: image.get_bounding_rect(min_alpha=16)
            for key, image in self.game_ui_assets.items()
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
            "how_to_panel": self._load_image(title_dir, "HowToPlay.png"),
            "how_to_background": self._load_image(title_dir, "HowToPlay_Background.png"),
            "how_to_back": self._load_image(title_dir, "BackButton.png"),
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
            "quit": self._load_optional_image(select_dir, "PlayerSelect_Quit.png")
            or self._load_optional_image(UI_DIR, "UI_Quit.png"),
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
        if self.pending_setup_back:
            return
        screen = self.flow.screen
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if screen in (AppScreen.PLAYER_COUNT, AppScreen.NAME_ENTRY) and self._setup_quit_button_hit(event.pos):
                self.pressed_setup_quit = True
                return
            self.pressed_button_action = self._screen_button_action_at(screen, event.pos)
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
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.released_game_ui_key = None
            self.pressed_button_action = None
            self.pressed_setup_quit = False

    def _screen_button_action_at(self, screen, position):
        if screen == AppScreen.PLAYER_COUNT:
            for key in ("players_funny", *(f"players_{count}" for count in reversed(PLAYER_COUNT_OPTIONS))):
                button = self.buttons[key]
                if button.rect.collidepoint(position):
                    return button.action
        elif screen == AppScreen.NAME_ENTRY:
            button = self.buttons["confirm_name"]
            if button.rect.collidepoint(position):
                return button.action
        elif screen == AppScreen.HOW_TO_PLAY:
            button = self.buttons["back"]
            if button.rect.collidepoint(position):
                return button.action
        return None

    def _handle_title_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.pressed_title_button_key = self._title_button_at(event.pos)
            return
        if event.type != pygame.MOUSEBUTTONUP or event.button != 1:
            return

        clicked_key = self.pressed_title_button_key
        self.pressed_title_button_key = None
        if clicked_key != self._title_button_at(event.pos):
            return

        if clicked_key == "single":
            from_screen = self.flow.screen
            self.flow.choose_single_player()
            self.name_input.clear()
            self._start_transition(from_screen, self.flow.screen, "horizontal")
        elif clicked_key == "multi":
            from_screen = self.flow.screen
            self.flow.choose_multiplayer()
            self._start_transition(from_screen, self.flow.screen, "horizontal")
        elif clicked_key == "how_to":
            self._start_how_to_open(AppScreen.TITLE)

    def _title_button_at(self, position):
        for key in reversed(TITLE_BUTTON_KEYS):
            if self.buttons[key].rect.collidepoint(position):
                return key
        return None

    def _start_how_to_open(self, source_screen):
        self.how_to_source_screen = source_screen
        self.how_to_source_surface = self._render_how_to_source_surface(source_screen)
        self.how_to_scene_surface = self._build_how_to_scene_surface(self.how_to_source_surface)
        self.how_to_state = "opening_zoom"
        self.how_to_elapsed_ms = 0
        self.how_to_back_progress = 0.0
        self.how_to_back_hover_progress = 0.0
        self.how_to_back_hovered = False
        self.how_to_back_pressed = False
        self.pressed_title_button_key = None
        self.pressed_game_ui_key = None
        self.released_game_ui_key = None
        self.flow.show_how_to_play(return_to=source_screen)

    def _handle_custom_how_to_event(self, event):
        if self.how_to_state not in ("open", "closing_back"):
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.how_to_back_pressed = self._how_to_back_button_hit(event.pos)
            return
        if event.type != pygame.MOUSEBUTTONUP or event.button != 1:
            return
        should_close = self.how_to_back_pressed and self._how_to_back_button_hit(event.pos)
        self.how_to_back_pressed = False
        if should_close and self.how_to_state == "open":
            self._start_how_to_close()

    def _start_how_to_close(self):
        self.how_to_state = "closing_back"
        self.how_to_elapsed_ms = 0
        self.how_to_back_pressed = False
        self.how_to_back_hovered = False

    def _handle_player_count_event(self, event):
        if self._setup_quit_button_clicked(event):
            self._start_setup_back_transition()
            return
        for count in PLAYER_COUNT_OPTIONS:
            if self.buttons[f"players_{count}"].clicked(event):
                from_screen = self.flow.screen
                self.flow.choose_player_count(count)
                self.name_input.clear()
                self._start_transition(from_screen, self.flow.screen, "vertical_setup")
                return

    def _handle_name_entry_event(self, event):
        from_screen = self.flow.screen
        submitted = self.name_input.handle_event(event)
        if self._setup_quit_button_clicked(event):
            self._start_setup_back_transition()
            return
        if self.buttons["confirm_name"].clicked(event):
            submitted = self.name_input.text
        if submitted is not None:
            setup = self.flow.submit_name(submitted)
            if not self.flow.name_error:
                self.name_input.clear()
            if setup is not None:
                self._create_game(setup.names, setup.bot_indices)
                self._start_table_entry_transition(from_screen)

    def _handle_how_to_play_event(self, event):
        if self.how_to_state is not None:
            self._handle_custom_how_to_event(event)
            return
        if self.buttons["back"].clicked(event):
            self.flow.leave_how_to_play()

    def _handle_table_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.pressed_game_ui_key = self._top_game_ui_key_at(event.pos)
            return
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.released_game_ui_key = self.pressed_game_ui_key
            self.pressed_game_ui_key = None

        if self._game_button_clicked("quit", event):
            self._start_table_exit_transition()
            return
        if self._game_button_clicked("hands", event):
            self._start_how_to_open(AppScreen.TABLE)
            return
        if self.game is None:
            return
        if self.game.street in ("IDLE", "HAND_OVER"):
            if self._game_button_clicked("new_hand", event):
                self.game.start_hand()
                self._randomize_community_card_slots()
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
        self._randomize_community_card_slots()
        self.phase_banner_seen_street = self.game.street
        self.phase_banner_animation = None
        self._reset_current_player_panel_state(visible=True)
        self._sync_raise_total()

    def _start_table_entry_transition(self, from_screen):
        self.pending_table_exit = False
        self.table_scene_age_ms = 0
        self.action_button_progress = {key: 0.0 for key in ANIMATED_ACTION_KEYS}
        self._start_transition(from_screen, AppScreen.TABLE, "table_enter", TABLE_ENTER_TRANSITION_MS)

    def _start_setup_back_transition(self):
        if self.pending_setup_back:
            return
        self.pending_setup_back = True
        self.setup_quit_hover_progress = 0.0

    def _start_table_exit_transition(self):
        if self.game is None:
            self.flow.back_to_title()
            return
        self.pending_table_exit = True
        self._start_transition(AppScreen.TABLE, AppScreen.TITLE, "table_exit", TABLE_EXIT_TRANSITION_MS)

    def _choose_player_profiles(self, count):
        if not self.profile_assets:
            return []
        if count <= len(self.profile_assets):
            return self.rng.sample(self.profile_assets, count)
        return [self.rng.choice(self.profile_assets) for _ in range(count)]

    def _start_transition(self, from_screen, to_screen, kind, duration_ms=None):
        self.transition = ScreenTransition(
            from_screen,
            to_screen,
            kind,
            duration_ms=duration_ms or SCREEN_SLIDE_DURATION_MS,
        )

    def _finish_transition(self):
        if self.transition is not None and self.transition.kind == "table_exit":
            self.flow.back_to_title()
            self.game = None
            self.pending_table_exit = False
            self.phase_banner_seen_street = None
            self.phase_banner_animation = None
            self._reset_table_animation_state()
        self.transition = None

    def _reset_table_animation_state(self):
        self.table_scene_age_ms = TABLE_UI_ENTRY_MS
        self.action_button_progress = {key: 0.0 for key in ANIMATED_ACTION_KEYS}
        self.game_ui_hover_progress = {key: 0.0 for key in GAME_UI_HOVER_OFFSETS}
        self.hovered_game_ui_key = None
        self.pressed_game_ui_key = None
        self.released_game_ui_key = None
        self._reset_current_player_panel_state(visible=True)
        self.current_hand_hover_progress = [0.0, 0.0]
        self.community_cards_seen = 0
        self.community_card_reveal_ms = {}

    def _reset_current_player_panel_state(self, visible=True):
        if self.game is not None and self.game.players:
            self.displayed_current_player_index = self.game.current_player_index
            self.displayed_current_hand_signature = self._current_player_signature(self.displayed_current_player_index)
        else:
            self.displayed_current_player_index = None
            self.displayed_current_hand_signature = None
        self.pending_current_player_index = None
        self.current_player_panel_progress = 1.0 if visible else 0.0
        self.current_player_panel_phase = "idle" if visible else "in"

    def _update(self, dt):
        self.app_time_ms += dt
        if self.transition is not None:
            self.transition.elapsed_ms += dt
            if self.transition.kind in ("table_enter", "table_exit") and self.game is not None:
                self._update_table_scene(dt, allow_bot_actions=False)
            if self.transition.elapsed_ms >= self.transition.duration_ms:
                self._finish_transition()
            return

        if self.flow.screen == AppScreen.HOW_TO_PLAY and self.how_to_state is not None:
            self._update_how_to_animation(dt)
            return

        self._update_setup_quit_animation(dt)
        if self.pending_setup_back and self.setup_quit_progress <= 0:
            self._finish_setup_back_transition()
            return

        if self.flow.screen != AppScreen.TABLE or self.game is None:
            return
        self._update_table_scene(dt, allow_bot_actions=True)

    def _update_setup_quit_animation(self, dt):
        target = 1.0 if self._setup_screen_has_quit_button() and not self.pending_setup_back else 0.0
        self.setup_quit_progress = self._approach_value(
            self.setup_quit_progress,
            target,
            dt / SETUP_QUIT_SLIDE_MS,
        )
        if target == 0.0:
            self.setup_quit_hover_progress += (0.0 - self.setup_quit_hover_progress) * SETUP_QUIT_HOVER_SPEED

    def _setup_screen_has_quit_button(self):
        return self.flow.screen in (AppScreen.PLAYER_COUNT, AppScreen.NAME_ENTRY)

    def _finish_setup_back_transition(self):
        from_screen = self.flow.screen
        self.flow.back_to_title()
        self.name_input.clear()
        self.pending_setup_back = False
        self.setup_quit_progress = 0.0
        self.setup_quit_hover_progress = 0.0
        self._start_transition(from_screen, self.flow.screen, "horizontal_reverse")

    def _update_how_to_animation(self, dt):
        self.how_to_elapsed_ms += dt

        if self.how_to_state == "opening_zoom":
            if self.how_to_elapsed_ms >= HOW_TO_ZOOM_MS:
                self._set_how_to_state("opening_panel")
            return

        if self.how_to_state == "opening_panel":
            if self.how_to_elapsed_ms >= HOW_TO_PANEL_SLIDE_MS:
                self._set_how_to_state("opening_back")
            return

        if self.how_to_state == "opening_back":
            progress = min(1.0, self.how_to_elapsed_ms / HOW_TO_BACK_SLIDE_MS)
            self.how_to_back_progress = self._ease_out_cubic(progress)
            if progress >= 1.0:
                self._set_how_to_state("open")
            return

        if self.how_to_state == "open":
            self.how_to_back_progress = 1.0
            self._update_how_to_back_hover()
            return

        if self.how_to_state == "closing_back":
            progress = min(1.0, self.how_to_elapsed_ms / HOW_TO_BACK_SLIDE_MS)
            self.how_to_back_progress = 1.0 - self._ease_out_cubic(progress)
            self.how_to_back_hover_progress += (0.0 - self.how_to_back_hover_progress) * HOW_TO_BACK_HOVER_SPEED
            if progress >= 1.0:
                self._set_how_to_state("closing_panel")
            return

        if self.how_to_state == "closing_panel":
            if self.how_to_elapsed_ms >= HOW_TO_PANEL_SLIDE_MS:
                self._set_how_to_state("closing_zoom")
            return

        if self.how_to_state == "closing_zoom":
            if self.how_to_elapsed_ms >= HOW_TO_ZOOM_MS:
                self._finish_how_to_close()

    def _set_how_to_state(self, state):
        self.how_to_state = state
        self.how_to_elapsed_ms = 0
        if state == "open":
            self.how_to_back_progress = 1.0

    def _finish_how_to_close(self):
        self.how_to_state = None
        self.how_to_elapsed_ms = 0
        self.how_to_source_surface = None
        self.how_to_scene_surface = None
        self.how_to_back_progress = 0.0
        self.how_to_back_hover_progress = 0.0
        self.how_to_back_pressed = False
        self.how_to_back_hovered = False
        self.flow.leave_how_to_play()

    def _update_table_scene(self, dt, allow_bot_actions=True):
        self.table_scene_age_ms = min(
            self.table_scene_age_ms + dt,
            max(TABLE_BACKGROUND_ENTRY_MS, TABLE_UI_ENTRY_MS),
        )
        self._update_game_background(dt)
        self._sync_phase_banner()
        self._update_phase_banner(dt)
        self._update_community_card_reveals(dt)
        self._update_action_button_visibility(dt)
        self._update_current_player_panel_switch(dt)
        self._update_game_ui_hover_states(dt)
        self._update_current_hand_hover(dt)
        if not allow_bot_actions:
            return
        if self.game.street in ("PREFLOP", "FLOP", "TURN", "RIVER") and self.game.current_player.is_bot:
            now = pygame.time.get_ticks()
            if self.bot_action_due == 0:
                self.bot_action_due = now + self.rng.randint(*BOT_THINK_MS_RANGE)
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

    def _sync_phase_banner(self):
        if self.game is None:
            self.phase_banner_seen_street = None
            self.phase_banner_animation = None
            return

        street = self.game.street
        if street == self.phase_banner_seen_street:
            return

        if street in PHASE_BANNER_UI_KEYS:
            if self._phase_banner_should_wait_for_human_turn(street):
                return
            self.phase_banner_seen_street = street
            self.phase_banner_animation = PhaseBannerAnimation(street)
        elif street == "IDLE":
            self.phase_banner_seen_street = street
            self.phase_banner_animation = None
        else:
            self.phase_banner_seen_street = street

    def _phase_banner_should_wait_for_human_turn(self, street):
        if self.game is None or street not in ("PREFLOP", "FLOP", "TURN", "RIVER"):
            return False
        if not any(not player.is_bot for player in self.game.players):
            return False
        return self.game.current_player.is_bot

    def _update_phase_banner(self, dt):
        if self.phase_banner_animation is None:
            return

        self.phase_banner_animation.elapsed_ms += dt
        if self.phase_banner_animation.elapsed_ms >= self._phase_banner_total_ms():
            self.phase_banner_animation = None

    def _phase_banner_total_ms(self):
        return PHASE_BANNER_ARC_MS

    def _randomize_community_card_slots(self):
        card_width = CARD_BASE_WIDTH * COMMUNITY_CARD_SCALE
        total_width = card_width * 5 + COMMUNITY_CARD_GAP * 4
        first_center_x = COMMUNITY_CARD_ROW_CENTER.x - total_width / 2 + card_width / 2
        self.community_card_slots = []

        for index in range(5):
            base_center = pygame.Vector2(
                first_center_x + index * (card_width + COMMUNITY_CARD_GAP),
                COMMUNITY_CARD_ROW_CENTER.y,
            )
            jitter = pygame.Vector2(
                self.rng.uniform(-COMMUNITY_CARD_X_JITTER, COMMUNITY_CARD_X_JITTER),
                self.rng.uniform(-COMMUNITY_CARD_Y_JITTER, COMMUNITY_CARD_Y_JITTER),
            )
            angle = self.rng.uniform(*COMMUNITY_CARD_ROTATION_RANGE)
            self.community_card_slots.append(CommunityCardSlot(base_center + jitter, angle))

        self.community_cards_seen = 0
        self.community_card_reveal_ms = {}
        self.card_back_assignments.clear()

    def _update_community_card_reveals(self, dt):
        if self.game is None:
            self.community_cards_seen = 0
            self.community_card_reveal_ms = {}
            return

        visible_count = len(self.game.community_cards)
        if visible_count < self.community_cards_seen:
            self.community_card_reveal_ms = {}
            self.community_cards_seen = visible_count

        for index in range(self.community_cards_seen, visible_count):
            self.community_card_reveal_ms[index] = 0
        self.community_cards_seen = visible_count

        for index in list(self.community_card_reveal_ms):
            self.community_card_reveal_ms[index] += dt
            if self.community_card_reveal_ms[index] >= COMMUNITY_CARD_REVEAL_MS:
                del self.community_card_reveal_ms[index]

    def _update_action_button_visibility(self, dt):
        for key in ANIMATED_ACTION_KEYS:
            target = 1.0 if self._action_key_is_actionable(key) else 0.0
            current = self.action_button_progress.get(key, 0.0)
            self.action_button_progress[key] = self._approach_value(
                current,
                target,
                dt / ACTION_BUTTON_SLIDE_MS,
            )

    def _update_current_player_panel_switch(self, dt):
        if self.game is None or not self.game.players:
            self._reset_current_player_panel_state(visible=True)
            return

        actual_index = self.game.current_player_index
        if self.displayed_current_player_index is None:
            self._reset_current_player_panel_state(visible=True)
            return

        if self.current_player_panel_phase == "out":
            self.pending_current_player_index = actual_index
            self.current_player_panel_progress = self._approach_value(
                self.current_player_panel_progress,
                0.0,
                dt / CURRENT_PLAYER_PANEL_SWITCH_MS,
            )
            if self.current_player_panel_progress <= 0:
                self.displayed_current_player_index = self.pending_current_player_index
                self.displayed_current_hand_signature = self._current_player_signature(self.displayed_current_player_index)
                self.pending_current_player_index = None
                self.current_player_panel_phase = "in"
                self.current_player_panel_progress = 0.0
                self.current_hand_hover_progress = [0.0, 0.0]
            return

        if self.current_player_panel_phase == "in":
            if actual_index != self.displayed_current_player_index:
                self.pending_current_player_index = actual_index
                self.current_player_panel_phase = "out"
                return

            self.current_player_panel_progress = self._approach_value(
                self.current_player_panel_progress,
                1.0,
                dt / CURRENT_PLAYER_PANEL_SWITCH_MS,
            )
            if self.current_player_panel_progress >= 1:
                self.current_player_panel_phase = "idle"
                self.displayed_current_hand_signature = self._current_player_signature(self.displayed_current_player_index)
            return

        if actual_index != self.displayed_current_player_index:
            self.pending_current_player_index = actual_index
            self.current_player_panel_phase = "out"
            self.current_player_panel_progress = 1.0
            self.current_hand_hover_progress = [0.0, 0.0]
            return

        actual_signature = self._current_player_signature(actual_index)
        if actual_signature != self.displayed_current_hand_signature:
            self.displayed_current_hand_signature = actual_signature
            self.current_player_panel_phase = "in"
            self.current_player_panel_progress = 0.0
            count = len(self.game.players[actual_index].hand)
            self.current_hand_hover_progress = [0.0 for _ in range(max(2, count))]

    def _current_player_signature(self, index):
        if self.game is None or not self.game.players or index is None:
            return None
        if index < 0 or index >= len(self.game.players):
            return None
        player = self.game.players[index]
        return tuple((card.rank, card.suit) for card in player.hand)

    def _current_player_panel_offset(self):
        eased = self._ease_out_cubic(self.current_player_panel_progress)
        return CURRENT_PLAYER_PANEL_SWITCH_OFFSET * (1 - eased)

    def _displayed_current_player_index(self):
        if self.game is None or not self.game.players:
            return None
        if self.displayed_current_player_index is None:
            return self.game.current_player_index
        return max(0, min(len(self.game.players) - 1, self.displayed_current_player_index))

    def _update_game_ui_hover_states(self, dt):
        hovered_key = self._top_game_ui_key_at(pygame.mouse.get_pos())
        self.hovered_game_ui_key = hovered_key
        for key in GAME_UI_BUTTON_LAYER_ORDER:
            current = self.game_ui_hover_progress.setdefault(key, 0.0)
            target = 1.0 if key == hovered_key else 0.0
            current += (target - current) * GAME_UI_HOVER_SPEED
            self.game_ui_hover_progress[key] = current

    def _update_current_hand_hover(self, dt):
        count = len(self.game.current_player.hand) if self.game is not None and self.game.players else 0
        self._ensure_current_hand_hover_progress(count)
        hovered_index = self._current_hand_hovered_index()
        for index in range(len(self.current_hand_hover_progress)):
            target = 1.0 if index == hovered_index else 0.0
            self.current_hand_hover_progress[index] = self._approach_value(
                self.current_hand_hover_progress[index],
                target,
                dt / CURRENT_HAND_HOVER_MS,
            )

    def _ensure_current_hand_hover_progress(self, count):
        while len(self.current_hand_hover_progress) < count:
            self.current_hand_hover_progress.append(0.0)

    def _current_hand_hovered_index(self):
        if self.game is None or not self.game.players:
            return None
        if self._displayed_current_player_index() != self.game.current_player_index:
            return None
        if self.current_player_panel_progress < 0.98:
            return None
        player = self.game.current_player
        if not player.hand or player.folded:
            return None

        mouse_pos = pygame.mouse.get_pos()
        panel_offset = self._table_entry_offset("bottom_panel") + self._current_player_panel_offset()
        width = CARD_BASE_WIDTH * CURRENT_HAND_CARD_SCALE
        height = CARD_BASE_HEIGHT * CURRENT_HAND_CARD_SCALE

        for index in reversed(range(len(player.hand))):
            base_x = CURRENT_HAND_START_X + index * CURRENT_HAND_X_SPACING + panel_offset.x
            base_y = CURRENT_HAND_Y + index * CURRENT_HAND_Y_STEP + panel_offset.y
            hover_progress = self.current_hand_hover_progress[index] if index < len(self.current_hand_hover_progress) else 0.0
            current_hover_offset = CURRENT_HAND_HOVER_OFFSET * self._ease_out_cubic(hover_progress)
            for hover_offset in (pygame.Vector2(), current_hover_offset, CURRENT_HAND_HOVER_OFFSET):
                rect = pygame.Rect(
                    round(base_x + hover_offset.x),
                    round(base_y + hover_offset.y),
                    round(width),
                    round(height),
                ).inflate(18, 18)
                if rect.collidepoint(mouse_pos):
                    return index
        return None

    def _action_key_is_actionable(self, key):
        if self.game is None:
            return False
        if key == "new_hand":
            return self.game.street in ("IDLE", "HAND_OVER")
        if self.game.street not in ("PREFLOP", "FLOP", "TURN", "RIVER"):
            return False
        if self.game.current_player.is_bot:
            return False

        legal_actions = self.game.legal_actions()
        if key == "call":
            return bool(legal_actions)
        if key in ("raise", "raise_down", "raise_up"):
            return "raise" in legal_actions
        if key == "fold":
            return "fold" in legal_actions
        return False

    def _approach_value(self, current, target, amount):
        amount = max(0.0, min(1.0, amount))
        if current < target:
            return min(target, current + amount)
        if current > target:
            return max(target, current - amount)
        return current

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

        if self.transition.kind == "table_enter":
            self._draw_table()
            travel = self._table_transition_travel_distance()
            strip_progress = self._ease_in_out_cubic(progress)
            strip_x = -travel * strip_progress
            self._draw_screen(self.transition.from_screen, offset=(round(strip_x), 0))
            self._draw_table_transition_cover(strip_x + WIDTH)
            return

        if self.transition.kind == "table_exit":
            self._draw_table()
            cover_width = self._table_transition_cover_width()
            travel = self._table_exit_transition_travel_distance()
            strip_progress = self._ease_in_out_cubic(progress)
            transition_x = -cover_width + travel * strip_progress
            self._draw_title(offset=(round(transition_x - WIDTH * 2), 0))
            self._draw_player_select_background(offset=(round(transition_x - WIDTH), 0))
            self._draw_table_transition_cover(transition_x)
            return

        if self.transition.kind == "horizontal":
            source_x = round(-WIDTH * eased)
            target_x = round(WIDTH * (1 - eased))
            self._draw_screen(self.transition.from_screen, offset=(source_x, 0))
            self._draw_screen(self.transition.to_screen, offset=(target_x, 0))
            return

        if self.transition.kind == "horizontal_reverse":
            source_x = round(WIDTH * eased)
            target_x = round(-WIDTH * (1 - eased))
            self._draw_screen(self.transition.from_screen, offset=(source_x, 0))
            self._draw_screen(self.transition.to_screen, offset=(target_x, 0))
            return

        if self.transition.kind == "vertical_setup":
            source_y = round(-HEIGHT * eased)
            target_y = round(HEIGHT * (1 - eased))
            self._draw_player_select_background()
            self._draw_player_count(offset=(0, source_y), draw_background=False, draw_quit=False)
            self._draw_name_entry(offset=(0, target_y), draw_background=False, draw_quit=False)
            self._draw_setup_quit_button()
            return

        self._draw_screen(self.transition.to_screen)

    def _table_transition_cover_width(self):
        image = self.game_ui_assets.get("transition")
        return image.get_width() if image is not None else WIDTH

    def _table_transition_travel_distance(self):
        return max(
            TABLE_TRANSITION_TRAVEL_DISTANCE,
            WIDTH + self._table_transition_cover_width(),
        )

    def _table_exit_transition_travel_distance(self):
        return TABLE_EXIT_TRANSITION_TRAVEL_DISTANCE + self._table_transition_cover_width()

    def _draw_table_transition_cover(self, x):
        image = self.game_ui_assets.get("transition")
        if image is None:
            return
        self.screen.blit(image, (round(x), 0))

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

    def _ease_in_out_cubic(self, value):
        if value < 0.5:
            return 4 * value**3
        return 1 - (-2 * value + 2) ** 3 / 2

    def _cursor_parallax_target(self, strength, mouse_pos=None):
        mouse = pygame.Vector2(pygame.mouse.get_pos() if mouse_pos is None else mouse_pos)
        center = pygame.Vector2(WIDTH / 2, HEIGHT / 2)
        half_size = pygame.Vector2(WIDTH / 2, HEIGHT / 2)
        normalized = pygame.Vector2(
            max(-1.0, min(1.0, (mouse.x - center.x) / half_size.x)),
            max(-1.0, min(1.0, (mouse.y - center.y) / half_size.y)),
        )
        return pygame.Vector2(strength.x * normalized.x, strength.y * normalized.y)

    def _update_cursor_parallax(self, current, strength):
        target = self._cursor_parallax_target(strength)
        current += (target - current) * CURSOR_PARALLAX_SMOOTHING
        return current

    def _table_ui_entry_progress(self):
        progress = max(0.0, min(1.0, self.table_scene_age_ms / TABLE_UI_ENTRY_MS))
        return self._ease_out_cubic(progress)

    def _table_background_entry_progress(self):
        progress = max(0.0, min(1.0, self.table_scene_age_ms / TABLE_BACKGROUND_ENTRY_MS))
        return self._ease_out_cubic(progress)

    def _table_entry_offset(self, group):
        start_offset = TABLE_ENTRY_OFFSETS[group]
        return start_offset * (1 - self._table_ui_entry_progress())

    def _draw_title(self, offset=(0, 0)):
        offset_x, offset_y = offset
        self.screen.blit(self.title_assets["bg"], (offset_x, offset_y))
        cards_parallax = self._update_cursor_parallax(
            self.title_cards_parallax_offset,
            TITLE_CARDS_PARALLAX_STRENGTH,
        )
        self.screen.blit(
            self.title_assets["cards"],
            (
                offset_x - 130 + round(cards_parallax.x),
                offset_y - 100 + round(cards_parallax.y),
            ),
        )
        self._draw_title_letters(offset=offset)
        self.screen.blit(self.title_assets["folder"], (offset_x, offset_y))
        for key in TITLE_BUTTON_KEYS:
            self._draw_title_button(key, offset=offset)
        self._draw_title_hover_asset("texas", (20, 70), offset)
        self._draw_title_hover_asset("holdem", (140, 155), offset)

    def _draw_title_button(self, key, offset=(0, 0)):
        button = self.buttons[key]
        draw_rect = button.rect.move(offset)
        hovered = draw_rect.collidepoint(pygame.mouse.get_pos())
        pressed = offset == (0, 0) and self.pressed_title_button_key == key
        button.draw(
            self.screen,
            self.font_md,
            offset=offset,
            hovered=hovered,
            pressed=pressed,
            outline=True,
            outline_radius=GAME_UI_OUTLINE_RADIUS,
        )

    def _draw_title_letters(self, offset=(0, 0)):
        offset_x, offset_y = offset
        start_x = 8
        y_base = 275
        x_offset = 0
        for index, char in enumerate("POKER"):
            letter = self.title_assets["letters"][char]
            y = y_base
            if char == "O":
                y += 120
                x_offset -= 80
            if char == "R":
                y -= 20
                x_offset += 20
            wave = math.sin(
                self.app_time_ms / 1000 * TITLE_LETTER_WAVE_SPEED
                + index * TITLE_LETTER_WAVE_PHASE_STEP
            ) * TITLE_LETTER_WAVE_AMPLITUDE
            self.screen.blit(letter, (start_x + x_offset + offset_x, y + offset_y + round(wave)))
            x_offset += letter.get_width() - 40

    def _draw_title_hover_asset(self, key, topleft, offset=(0, 0)):
        image = self.title_assets[key]
        offset_x, offset_y = offset
        base_rect = image.get_rect(topleft=(topleft[0] + offset_x, topleft[1] + offset_y))
        target = 1.0 if base_rect.collidepoint(pygame.mouse.get_pos()) else 0.0
        current = self.title_hover_progress.get(key, 0.0)
        current += (target - current) * TITLE_WORD_HOVER_SPEED
        self.title_hover_progress[key] = current
        scale = 1 + (TITLE_WORD_HOVER_SCALE - 1) * self._ease_out_cubic(current)
        if abs(scale - 1.0) < 0.001:
            self.screen.blit(image, base_rect)
            return

        size = (
            max(1, round(image.get_width() * scale)),
            max(1, round(image.get_height() * scale)),
        )
        scaled = self._scaled_image(image, size)
        self.screen.blit(scaled, scaled.get_rect(center=base_rect.center))

    def _draw_player_count(self, offset=(0, 0), draw_background=True, draw_quit=True):
        offset_x, offset_y = offset
        if draw_background:
            self._draw_player_select_background(offset=(offset_x, 0))
        if draw_quit:
            self._draw_setup_quit_button(offset=offset)
        if self.select_assets["title"] is not None:
            title_image = self.select_assets["title"]
            title_rect = title_image.get_rect(midtop=(WIDTH // 2, 0))
            title_rect.move_ip(offset_x, offset_y)
            self.screen.blit(title_image, title_rect)
        else:
            prompt = self.font_md.render("Choose number of players", True, WHITE)
            self.screen.blit(prompt, prompt.get_rect(center=(WIDTH // 2 + offset_x, 90 + offset_y)))
        for count in PLAYER_COUNT_OPTIONS:
            self._draw_standard_button(f"players_{count}", self.font_lg, offset=offset)
        self._draw_standard_button("players_funny", self.font_lg, offset=offset)

    def _draw_name_entry(self, offset=(0, 0), draw_background=True, draw_quit=True):
        offset_x, offset_y = offset
        if draw_background:
            self._draw_player_select_background(offset=(offset_x, 0))
        if draw_quit:
            self._draw_setup_quit_button(offset=offset)
        if self.select_assets["enter_name"] is not None:
            title = self.select_assets["enter_name"]
            self.screen.blit(title, title.get_rect(center=(WIDTH // 2 + offset_x, 150 + offset_y)))
        self._draw_entered_name_boxes(offset=offset)
        self.name_input.draw(self.screen, self.font_md, error=bool(self.flow.name_error), offset=offset)
        self._draw_standard_button("confirm_name", self.font_md, offset=offset)
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

    def _draw_setup_quit_button(self, offset=(0, 0)):
        if self.setup_quit_progress <= 0.001:
            return

        draw_offset = pygame.Vector2(offset) + self._setup_quit_slide_offset()
        image = self.select_assets.get("quit")
        if image is None:
            self._draw_standard_button("back", self.font_sm, offset=draw_offset)
            return

        hover_offset = self._setup_quit_hover_motion(draw_offset)
        self._draw_game_ui_button_sprite(
            image,
            draw_offset + hover_offset,
            hovered=self.setup_quit_hovered,
            pressed=self.pressed_setup_quit,
        )

    def _draw_standard_button(self, key, font, offset=(0, 0)):
        button = self.buttons[key]
        draw_rect = button.rect.move(offset)
        hovered = draw_rect.collidepoint(pygame.mouse.get_pos())
        pressed = self.pressed_button_action == button.action
        button.draw(
            self.screen,
            font,
            offset=offset,
            hovered=hovered,
            pressed=pressed,
            outline=True,
            outline_radius=GAME_UI_OUTLINE_RADIUS,
        )

    def _setup_quit_slide_offset(self):
        eased = self._ease_out_cubic(self.setup_quit_progress)
        return SETUP_QUIT_SLIDE_OFFSET * (1 - eased)

    def _setup_quit_hover_motion(self, base_offset):
        current_hover = SETUP_QUIT_HOVER_OFFSET * self._ease_out_cubic(self.setup_quit_hover_progress)
        mouse_pos = pygame.mouse.get_pos()
        hovering = False
        if self.setup_quit_progress >= 0.98 and not self.pending_setup_back:
            hovering = (
                self._setup_quit_asset_hit(mouse_pos, base_offset)
                or self._setup_quit_asset_hit(mouse_pos, base_offset + current_hover)
            )
        self.setup_quit_hovered = hovering
        target = 1.0 if hovering else 0.0
        self.setup_quit_hover_progress += (
            target - self.setup_quit_hover_progress
        ) * SETUP_QUIT_HOVER_SPEED
        return SETUP_QUIT_HOVER_OFFSET * self._ease_out_cubic(self.setup_quit_hover_progress)

    def _setup_quit_button_clicked(self, event):
        if event.type != pygame.MOUSEBUTTONUP or event.button != 1:
            return False
        if self.pending_setup_back or self.setup_quit_progress < 0.98:
            return False
        if not self.pressed_setup_quit:
            return False

        slide_offset = self._setup_quit_slide_offset()
        if self.select_assets.get("quit") is None:
            return self.buttons["back"].clicked(event, offset=slide_offset)

        current_hover = SETUP_QUIT_HOVER_OFFSET * self._ease_out_cubic(self.setup_quit_hover_progress)
        return (
            self._setup_quit_asset_hit(event.pos, slide_offset)
            or self._setup_quit_asset_hit(event.pos, slide_offset + current_hover)
        )

    def _setup_quit_button_hit(self, position):
        if self.pending_setup_back or self.setup_quit_progress < 0.98:
            return False

        slide_offset = self._setup_quit_slide_offset()
        if self.select_assets.get("quit") is None:
            return self.buttons["back"].rect.move(round(slide_offset.x), round(slide_offset.y)).collidepoint(position)

        current_hover = SETUP_QUIT_HOVER_OFFSET * self._ease_out_cubic(self.setup_quit_hover_progress)
        return (
            self._setup_quit_asset_hit(position, slide_offset)
            or self._setup_quit_asset_hit(position, slide_offset + current_hover)
        )

    def _setup_quit_asset_hit(self, position, offset):
        image = self.select_assets.get("quit")
        if image is None:
            return False

        image_rect = image.get_rect(center=(WIDTH // 2 + round(offset.x), HEIGHT // 2 + round(offset.y)))
        hit_rect = self.setup_quit_bounds.move(image_rect.topleft)
        return hit_rect.collidepoint(position)

    def _draw_how_to_play(self, offset=(0, 0)):
        if self.how_to_state is not None:
            self._draw_custom_how_to_play()
            return

        offset_x, offset_y = offset
        self._draw_standard_button("back", self.font_sm, offset=offset)
        title = self.font_xl.render("HOW TO PLAY", True, GOLD)
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2 + offset_x, 180 + offset_y)))
        for index, line in enumerate(HOW_TO_PLAY_LINES):
            text = self.font_md.render(line, True, WHITE)
            self.screen.blit(text, (220 + offset_x, 280 + index * 48 + offset_y))

    def _draw_custom_how_to_play(self):
        if self.how_to_scene_surface is None:
            source_surface = self.how_to_source_surface or self._render_how_to_source_surface(self.how_to_source_screen)
            self.how_to_scene_surface = self._build_how_to_scene_surface(source_surface)

        self._draw_how_to_zoom_scene(self._how_to_zoom_progress())
        panel_progress = self._how_to_panel_progress()
        if panel_progress > 0:
            panel_offset = HOW_TO_PANEL_START_OFFSET.lerp(HOW_TO_PANEL_FINAL_OFFSET, panel_progress)
            panel_parallax = self._update_cursor_parallax(
                self.how_to_panel_parallax_offset,
                HOW_TO_PANEL_PARALLAX_STRENGTH,
            )
            panel_offset += panel_parallax * panel_progress
            self._draw_centered_layer(self.title_assets["how_to_panel"], panel_offset)

        if self.how_to_back_progress > 0:
            self._draw_how_to_back_button()

    def _render_how_to_source_surface(self, source_screen):
        source_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        original_screen = self.screen
        try:
            self.screen = source_surface
            if source_screen == AppScreen.TABLE and self.game is not None:
                self._draw_table()
            else:
                self._draw_title()
        finally:
            self.screen = original_screen
        return source_surface

    def _build_how_to_scene_surface(self, source_surface):
        scene = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        background = self.title_assets["how_to_background"]
        background_rect, monitor_rect = self._how_to_background_layout()
        source_view = pygame.transform.smoothscale(source_surface, monitor_rect.size)
        background_view = pygame.transform.smoothscale(background, background_rect.size)
        scene.blit(source_view, monitor_rect)
        scene.blit(background_view, background_rect)
        return scene

    def _how_to_background_layout(self):
        background = self.title_assets["how_to_background"]
        scale = max(WIDTH / background.get_width(), HEIGHT / background.get_height())
        scale *= HOW_TO_BACKGROUND_SCALE_MULTIPLIER
        size = (
            max(1, round(background.get_width() * scale)),
            max(1, round(background.get_height() * scale)),
        )
        rect = pygame.Rect(0, 0, *size)
        rect.center = (
            WIDTH // 2 + round(HOW_TO_BACKGROUND_OFFSET.x),
            HEIGHT // 2 + round(HOW_TO_BACKGROUND_OFFSET.y),
        )

        source_monitor = HOW_TO_BACKGROUND_MONITOR_RECT
        monitor_rect = pygame.Rect(
            round(rect.x + source_monitor.x * scale),
            round(rect.y + source_monitor.y * scale),
            round(source_monitor.width * scale),
            round(source_monitor.height * scale),
        )
        return rect, monitor_rect

    def _how_to_zoom_progress(self):
        if self.how_to_state == "opening_zoom":
            progress = min(1.0, self.how_to_elapsed_ms / HOW_TO_ZOOM_MS)
            return self._ease_in_out_cubic(progress)
        if self.how_to_state == "closing_zoom":
            progress = min(1.0, self.how_to_elapsed_ms / HOW_TO_ZOOM_MS)
            return 1.0 - self._ease_in_out_cubic(progress)
        if self.how_to_state in ("opening_panel", "opening_back", "open", "closing_back", "closing_panel"):
            return 1.0
        return 0.0

    def _how_to_panel_progress(self):
        if self.how_to_state == "opening_panel":
            progress = min(1.0, self.how_to_elapsed_ms / HOW_TO_PANEL_SLIDE_MS)
            return self._ease_in_out_cubic(progress)
        if self.how_to_state in ("opening_back", "open", "closing_back"):
            return 1.0
        if self.how_to_state == "closing_panel":
            progress = min(1.0, self.how_to_elapsed_ms / HOW_TO_PANEL_SLIDE_MS)
            return 1.0 - self._ease_in_out_cubic(progress)
        return 0.0

    def _draw_how_to_zoom_scene(self, zoom_progress):
        scene = self.how_to_scene_surface
        _, monitor_rect = self._how_to_background_layout()
        start_scale = max(WIDTH / monitor_rect.width, HEIGHT / monitor_rect.height)
        start_scale *= HOW_TO_ZOOM_START_SCALE_MULTIPLIER
        scale = start_scale + (1.0 - start_scale) * zoom_progress
        size = (max(1, round(WIDTH * scale)), max(1, round(HEIGHT * scale)))
        scaled_scene = pygame.transform.smoothscale(scene, size)

        monitor_center = pygame.Vector2(monitor_rect.center)
        anchor = pygame.Vector2(WIDTH / 2, HEIGHT / 2).lerp(monitor_center, zoom_progress)
        top_left = anchor - monitor_center * scale
        self.screen.blit(scaled_scene, (round(top_left.x), round(top_left.y)))

    def _draw_how_to_back_button(self):
        image = self.title_assets["how_to_back"]
        offset = self._how_to_back_offset()
        self._draw_game_ui_button_sprite(
            image,
            offset,
            hovered=self.how_to_back_hovered,
            pressed=self.how_to_back_pressed,
        )

    def _how_to_back_offset(self):
        slide_offset = HOW_TO_BACK_SLIDE_OFFSET * (1 - self.how_to_back_progress)
        hover_offset = HOW_TO_BACK_HOVER_OFFSET * self._ease_out_cubic(self.how_to_back_hover_progress)
        return slide_offset + hover_offset

    def _update_how_to_back_hover(self):
        current_hover = HOW_TO_BACK_HOVER_OFFSET * self._ease_out_cubic(self.how_to_back_hover_progress)
        base_offset = HOW_TO_BACK_SLIDE_OFFSET * (1 - self.how_to_back_progress)
        mouse_pos = pygame.mouse.get_pos()
        hovering = (
            self.how_to_back_progress >= 0.98
            and (
                self._how_to_back_asset_hit(mouse_pos, base_offset)
                or self._how_to_back_asset_hit(mouse_pos, base_offset + current_hover)
            )
        )
        self.how_to_back_hovered = hovering
        target = 1.0 if hovering else 0.0
        self.how_to_back_hover_progress += (target - self.how_to_back_hover_progress) * HOW_TO_BACK_HOVER_SPEED

    def _how_to_back_button_hit(self, position):
        if self.how_to_back_progress < 0.98:
            return False
        return self._how_to_back_asset_hit(position, self._how_to_back_offset())

    def _how_to_back_asset_hit(self, position, offset):
        image = self.title_assets["how_to_back"]
        image_rect = image.get_rect(center=(WIDTH // 2 + round(offset.x), HEIGHT // 2 + round(offset.y)))
        return self.how_to_back_bounds.move(image_rect.topleft).collidepoint(position)

    def _draw_table(self):
        if self.game is None:
            return
        self._draw_game_background()
        self._draw_game_ui_asset("table")
        self._draw_status()
        self._draw_community_cards()
        self._draw_table_players()
        self._draw_current_player_panel()
        self._draw_controls()
        self._draw_top_table_buttons()
        self._draw_phase_banner()

    def _draw_game_background(self):
        screen_rect = self.screen.get_rect()
        for layer in self.game_background_layers:
            entry_offset = self._background_layer_entry_offset(layer)
            if layer.motion.wrap:
                self._draw_wrapped_background_layer(screen_rect, layer, entry_offset)
            else:
                self._draw_centered_layer(layer.image, layer.offset + entry_offset, layer.blend_flags)

    def _draw_wrapped_background_layer(self, screen_rect, layer, entry_offset=None):
        entry_offset = entry_offset or pygame.Vector2()
        image_w, image_h = layer.image.get_size()
        offset_x = layer.offset.x + entry_offset.x
        offset_y = layer.offset.y + entry_offset.y

        for tile_y in (-1, 0, 1):
            for tile_x in (-1, 0, 1):
                center = (
                    WIDTH // 2 + round(offset_x + tile_x * image_w),
                    HEIGHT // 2 + round(offset_y + tile_y * image_h),
                )
                rect = layer.image.get_rect(center=center)
                if rect.colliderect(screen_rect):
                    self.screen.blit(layer.image, rect, special_flags=layer.blend_flags)

    def _background_layer_entry_offset(self, layer):
        if layer.name in TABLE_BACKGROUND_READY_LAYERS:
            return pygame.Vector2()

        progress = self._table_background_entry_progress()
        if progress >= 1.0:
            return pygame.Vector2()

        direction = pygame.Vector2(layer.motion.velocity)
        if direction.length_squared() == 0:
            direction = pygame.Vector2(0, 1)
        else:
            direction = self._background_trajectory_vector(direction.x, direction.y).normalize()
        return -direction * TABLE_BACKGROUND_ENTRY_DISTANCE * (1 - progress)

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
        if self._game_ui_key_is_button(key):
            self._draw_game_ui_button_sprite(
                image,
                offset,
                hovered=key == self.hovered_game_ui_key,
                pressed=key == self.pressed_game_ui_key,
            )
        else:
            self._draw_centered_layer(image, offset)
        return True

    def _draw_game_ui_button_sprite(self, image, offset, hovered=False, pressed=False):
        rect = image.get_rect(center=(WIDTH // 2 + round(offset.x), HEIGHT // 2 + round(offset.y)))
        if hovered and not pressed:
            outline = self._game_ui_outline_surface(image, GAME_UI_OUTLINE_RADIUS)
            self.screen.blit(outline, rect.move(-GAME_UI_OUTLINE_RADIUS, -GAME_UI_OUTLINE_RADIUS))

        if pressed:
            self.screen.blit(self._game_ui_silhouette_surface(image), rect)
        else:
            self.screen.blit(image, rect)
        return rect

    def _game_ui_silhouette_surface(self, image):
        cache_key = ("silhouette", id(image))
        if cache_key not in self.game_ui_silhouette_cache:
            mask = pygame.mask.from_surface(image, 16)
            self.game_ui_silhouette_cache[cache_key] = mask.to_surface(
                setcolor=(255, 255, 255, 255),
                unsetcolor=(0, 0, 0, 0),
            ).convert_alpha()
        return self.game_ui_silhouette_cache[cache_key]

    def _game_ui_outline_surface(self, image, radius):
        cache_key = ("outline", id(image), radius)
        if cache_key not in self.game_ui_outline_cache:
            silhouette = self._game_ui_silhouette_surface(image)
            outline = pygame.Surface(
                (image.get_width() + radius * 2, image.get_height() + radius * 2),
                pygame.SRCALPHA,
            )
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    if dx == 0 and dy == 0:
                        continue
                    if dx * dx + dy * dy <= radius * radius:
                        outline.blit(silhouette, (dx + radius, dy + radius))
            self.game_ui_outline_cache[cache_key] = outline.convert_alpha()
        return self.game_ui_outline_cache[cache_key]

    def _game_ui_base_offset(self, key):
        if key in GAME_UI_BASE_OFFSETS:
            return pygame.Vector2(GAME_UI_BASE_OFFSETS[key])
        if key in ACTION_UI_LAYER_ORDER:
            return pygame.Vector2(GAME_ACTION_BUTTON_BASE_OFFSET)
        return pygame.Vector2()

    def _game_ui_offset(self, key):
        resting_offset = self._game_ui_resting_offset(key)
        hover_offset = GAME_UI_HOVER_OFFSETS.get(key)
        if hover_offset is None:
            return resting_offset

        progress = self.game_ui_hover_progress.get(key, 0.0)
        return resting_offset + hover_offset * self._ease_out_cubic(progress)

    def _game_ui_resting_offset(self, key):
        offset = self._game_ui_base_offset(key) + self._game_ui_entry_offset(key)
        if key in ACTION_BUTTON_OFFSETS:
            offset += self._action_button_slide_offset(key)
        return offset

    def _game_ui_entry_offset(self, key):
        if key == "table":
            return self._table_entry_offset("table_top")
        if key == "profile_card":
            return self._table_entry_offset("bottom_panel") + self._current_player_panel_offset()
        if key in ("quit", "hands"):
            return self._table_entry_offset("left_buttons")
        if key == "new_hand":
            return self._table_entry_offset("deal_button")
        if key in ACTION_UI_LAYER_ORDER:
            return self._table_entry_offset("bottom_panel")
        return pygame.Vector2()

    def _action_button_slide_offset(self, key):
        if key not in ACTION_BUTTON_OFFSETS:
            return pygame.Vector2()
        progress = self.action_button_progress.get(key, 0.0)
        eased = self._ease_out_cubic(progress)
        return ACTION_BUTTON_OFFSETS[key] * (1 - eased)

    def _game_ui_asset_hit(self, key, position, offset=None):
        image = self.game_ui_assets.get(key)
        if image is None:
            return False
        if offset is None:
            offset = self._game_ui_offset(key)
        image_rect = image.get_rect(center=(WIDTH // 2 + round(offset.x), HEIGHT // 2 + round(offset.y)))
        hit_rect = self.game_ui_bounds.get(key, image.get_rect()).move(image_rect.topleft)
        return hit_rect.collidepoint(position)

    def _game_button_clicked(self, key, event):
        if event.type != pygame.MOUSEBUTTONUP or event.button != 1:
            return False
        if key in self.game_ui_assets:
            if self.released_game_ui_key is not None and self.released_game_ui_key != key:
                return False
            return self._top_game_ui_key_at(event.pos) == key
        return self.buttons[key].clicked(event)

    def _game_ui_key_is_button(self, key):
        return key in GAME_UI_BUTTON_LAYER_ORDER

    def _game_ui_key_is_interactable(self, key):
        if self.game is None or key not in self.game_ui_assets:
            return False
        if key in ANIMATED_ACTION_KEYS:
            return self.action_button_progress.get(key, 0.0) >= 0.85 and self._action_key_is_actionable(key)
        return key in ("quit", "hands")

    def _top_game_ui_key_at(self, position):
        for key in reversed(GAME_UI_BUTTON_LAYER_ORDER):
            if not self._game_ui_key_is_interactable(key):
                continue
            if (
                self._game_ui_asset_hit(key, position, self._game_ui_resting_offset(key))
                or self._game_ui_asset_hit(key, position, self._game_ui_offset(key))
            ):
                return key
        return None

    def _draw_status(self):
        pot_text = self.font_md.render(f"POT {self.game.pot}", True, GOLD)
        self.screen.blit(pot_text, pot_text.get_rect(center=(WIDTH // 2, 172)))

    def _draw_phase_banner(self):
        animation = self.phase_banner_animation
        if animation is None:
            return

        key = PHASE_BANNER_UI_KEYS.get(animation.street)
        image = self.game_ui_assets.get(key)
        if image is None:
            return

        self._draw_centered_layer(image, self._phase_banner_offset(animation.elapsed_ms))

    def _phase_banner_offset(self, elapsed_ms):
        progress = max(0.0, min(1.0, elapsed_ms / PHASE_BANNER_ARC_MS))
        x_progress = progress + 0.08 * math.sin(math.tau * progress)
        arc_height = 4 * progress * (1 - progress)
        x = PHASE_BANNER_START_OFFSET.x + (PHASE_BANNER_END_OFFSET.x - PHASE_BANNER_START_OFFSET.x) * x_progress
        y = PHASE_BANNER_START_OFFSET.y + (PHASE_BANNER_BOTTOM_OFFSET.y - PHASE_BANNER_START_OFFSET.y) * arc_height
        return pygame.Vector2(x, y)

    def _draw_community_cards(self):
        table_offset = self._table_entry_offset("table_top")
        for index in range(5):
            x, y = self._community_card_topleft(index)
            x += table_offset.x
            y += table_offset.y
            angle = self._community_card_angle(index)
            if index < len(self.game.community_cards):
                self._draw_card(self.game.community_cards[index], x, y, COMMUNITY_CARD_SCALE, True, angle)
            else:
                self._draw_card_back(x, y, COMMUNITY_CARD_SCALE, angle, slot_key=("community", index))

    def _community_card_topleft(self, index):
        slot = self._community_card_slot(index)
        width = CARD_BASE_WIDTH * COMMUNITY_CARD_SCALE
        height = CARD_BASE_HEIGHT * COMMUNITY_CARD_SCALE
        return slot.center.x - width / 2, slot.center.y - height / 2

    def _community_card_angle(self, index):
        slot = self._community_card_slot(index)
        reveal_ms = self.community_card_reveal_ms.get(index)
        if reveal_ms is None:
            return slot.angle

        progress = max(0.0, min(1.0, reveal_ms / COMMUNITY_CARD_REVEAL_MS))
        swing_direction = -1 if index % 2 == 0 else 1
        swing = math.sin(math.pi * progress) * COMMUNITY_CARD_REVEAL_SWING_DEGREES * swing_direction
        return slot.angle + swing

    def _community_card_slot(self, index):
        if len(self.community_card_slots) < 5:
            self._randomize_community_card_slots()
        return self.community_card_slots[index]

    def _draw_table_players(self):
        count = len(self.game.players)
        table_offset = self._table_entry_offset("table_top")
        for index, player in enumerate(self.game.players):
            px, py = self._table_player_position(index, count)
            px += table_offset.x
            py += table_offset.y
            is_turn = index == self.game.current_player_index and self.game.street in ("PREFLOP", "FLOP", "TURN", "RIVER")
            border = GOLD if is_turn else (RED if player.eliminated else WHITE)
            self._draw_profile(index, (px, py), 84, border)
            name = self.font_sm.render(player.name, True, BLACK)
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

        fallback = anchors[max(anchors)]
        return fallback[index % len(fallback)]

    def _draw_current_player_panel(self):
        if not self.game.players:
            return
        player_index = self._displayed_current_player_index()
        if player_index is None:
            return
        player = self.game.players[player_index]
        panel_offset = self._table_entry_offset("bottom_panel") + self._current_player_panel_offset()
        if not self._draw_game_ui_asset("profile_card"):
            panel = pygame.Rect(24 + round(panel_offset.x), 462 + round(panel_offset.y), 390, 294)
            pygame.draw.rect(self.screen, PANEL, panel, border_radius=8)
            pygame.draw.rect(self.screen, GOLD, panel, width=2, border_radius=8)

        stack = self.font_md.render("OUT" if player.eliminated else f"{player.stack}", True, GOLD)
        status = self.font_sm.render(self._player_status(player), True, MUTED)
        self.screen.blit(stack, stack.get_rect(center=(130 + panel_offset.x, 502 + panel_offset.y)))
        self.screen.blit(status, status.get_rect(center=(130 + panel_offset.x, 532 + panel_offset.y)))

        self._draw_profile(
            player_index,
            (130 + panel_offset.x, 625 + panel_offset.y),
            200,
            GOLD,
            player.name,
        )

        name = self.font_lg.render(player.name, True, BLACK)
        self.screen.blit(name, name.get_rect(center=(150 + panel_offset.x, 750 + panel_offset.y)))

        self._draw_current_player_hand(player, panel_offset)

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

    def _draw_current_player_hand(self, player, offset=(0, 0)):
        if not player.hand or player.folded:
            return
        offset = pygame.Vector2(offset)
        self._ensure_current_hand_hover_progress(len(player.hand))
        show_cards = self.game.street == "HAND_OVER" or not player.is_bot
        for index, card in enumerate(player.hand):
            card_offset = offset + CURRENT_HAND_HOVER_OFFSET * self._ease_out_cubic(self.current_hand_hover_progress[index])
            x = CURRENT_HAND_START_X + index * CURRENT_HAND_X_SPACING + card_offset.x
            y = CURRENT_HAND_Y + index * CURRENT_HAND_Y_STEP + card_offset.y
            angle = CURRENT_HAND_CARD_ANGLES[index % len(CURRENT_HAND_CARD_ANGLES)]
            if show_cards:
                self._draw_card(card, x, y, CURRENT_HAND_CARD_SCALE, True, angle=angle)
            else:
                slot_key = ("current_hand", self._displayed_current_player_index(), index, self._current_player_signature(self._displayed_current_player_index()))
                self._draw_card_back(x, y, CURRENT_HAND_CARD_SCALE, angle=angle, slot_key=slot_key)

    def _draw_controls(self):
        if self.action_button_progress.get("new_hand", 0.0) > 0.01:
            if not self._draw_game_ui_asset("new_hand"):
                self.buttons["new_hand"].draw(self.screen, self.font_sm)

        if self.game.street in ("IDLE", "HAND_OVER"):
            return
        current = self.game.current_player
        if current.is_bot:
            thinking = self.font_md.render("Thinking...", True, MUTED)
            self.screen.blit(thinking, thinking.get_rect(center=(1048, 615)))

        for key in ACTION_UI_LAYER_ORDER:
            if self.action_button_progress.get(key, 0.0) <= 0.01:
                continue
            if key not in self.game_ui_assets:
                self.buttons[key].draw(self.screen, self.font_sm)
            else:
                self._draw_game_ui_asset(key)

        if self.action_button_progress.get("raise", 0.0) > 0.01:
            raise_offset = self._game_ui_offset("raise")
            amount = self.font_lg.render(f"{self.raise_total}", True, BLACK)
            self.screen.blit(amount, amount.get_rect(center=(970 + round(raise_offset.x), 620 + round(raise_offset.y))))

    def _draw_top_table_buttons(self):
        for key in ("quit", "hands"):
            if not self._draw_game_ui_asset(key):
                self.buttons[key].draw(self.screen, self.font_sm)

    def _draw_card(self, card: Card, x, y, scale, face_up, angle=0, slot_key=None):
        if not face_up:
            self._draw_card_back(x, y, scale, angle=angle, slot_key=slot_key)
            return

        sprite = self.card_assets.get(self._card_asset_key(card))
        if sprite is None:
            return
        w, h = int(CARD_BASE_WIDTH * scale), int(CARD_BASE_HEIGHT * scale)
        image = self._scaled_image(sprite, (w, h))
        self._blit_card_image(image, x, y, angle)

    def _card_asset_key(self, card):
        return f"{card.rank}_{card.suit[0]}"

    def _draw_card_back(self, x, y, scale, angle=0, slot_key=None):
        w, h = int(CARD_BASE_WIDTH * scale), int(CARD_BASE_HEIGHT * scale)
        sprite = self._card_back_for_slot(x, y, scale, slot_key)
        if sprite is None:
            return
        image = self._scaled_image(sprite, (w, h))
        self._blit_card_image(image, x, y, angle)

    def _blit_card_image(self, image, x, y, angle=0):
        if angle == 0:
            self.screen.blit(image, (x, y))
            return

        original_rect = image.get_rect(topleft=(x, y))
        rotated = self._rotated_image(image, angle)
        self.screen.blit(rotated, rotated.get_rect(center=original_rect.center))

    def _card_back_for_slot(self, x, y, scale, slot_key=None):
        if not self.card_back_assets:
            return None
        slot = slot_key if slot_key is not None else ("position", round(x), round(y), round(scale * 100))
        if slot not in self.card_back_assignments:
            self.card_back_assignments[slot] = self.rng.randrange(len(self.card_back_assets))
        return self.card_back_assets[self.card_back_assignments[slot]]


if __name__ == "__main__":
    PokerApp().run()
