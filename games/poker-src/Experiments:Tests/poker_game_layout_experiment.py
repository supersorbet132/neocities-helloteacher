import math
import random
import sys

import pygame

from poker_flow import AppScreen, SetupController
from poker_rules import Card, PokerGame, evaluate_hand


WIDTH, HEIGHT = 1200, 800
FPS = 60
STARTING_STACK = 1000
SMALL_BLIND = 10
BIG_BLIND = 20
PLAYER_COUNT_OPTIONS = (2, 3, 4, 5, 6)

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
    def __init__(self, text, rect, color, action):
        self.text = text
        self.rect = pygame.Rect(rect)
        self.color = color
        self.action = action

    def draw(self, surface, font):
        mouse = pygame.mouse.get_pos()
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
        self.font_xl = pygame.font.SysFont("arial", 56, bold=True)
        self.font_lg = pygame.font.SysFont("arial", 34, bold=True)
        self.font_md = pygame.font.SysFont("arial", 23, bold=True)
        self.font_sm = pygame.font.SysFont("arial", 17, bold=True)
        self.rng = random.Random()
        self.flow = SetupController(single_player_total=4)
        self.game: PokerGame | None = None
        self.raise_total = BIG_BLIND * 2
        self.bot_action_due = 0
        self.name_input = TextInput((450, 590, 300, 54))
        self.buttons = self._make_buttons()

    def _make_buttons(self):
        buttons = {
            "single": Button("SINGLE PLAYER", (760, 180, 280, 58), GREEN, "single"),
            "multi": Button("MULTIPLAYER", (760, 275, 280, 58), BLUE, "multi"),
            "how_to": Button("HOW TO PLAY", (760, 370, 280, 58), PANEL_LIGHT, "how_to"),
            "back": Button("BACK", (40, 40, 120, 44), RED, "back"),
            "confirm_name": Button("CONFIRM", (480, 665, 240, 54), GREEN, "confirm_name"),
            "new_hand": Button("DEAL HAND", (970, 30, 190, 54), GOLD, "new_hand"),
            "call": Button("CHECK / CALL", (950, 540, 200, 48), BLUE, "call"),
            "raise": Button("RAISE", (950, 605, 200, 48), BLUE, "raise"),
            "fold": Button("FOLD", (950, 670, 200, 48), RED, "fold"),
            "raise_down": Button("-10", (880, 605, 58, 48), PANEL_LIGHT, "raise_down"),
            "raise_up": Button("+10", (1162, 605, 58, 48), PANEL_LIGHT, "raise_up"),
            "hands": Button("HANDS", (20, 70, 110, 40), PANEL_LIGHT, "hands"),
            "quit": Button("QUIT", (20, 20, 110, 40), RED, "quit"),
        }
        for index, count in enumerate(PLAYER_COUNT_OPTIONS):
            x = 260 + index * 140
            buttons[f"players_{count}"] = Button(str(count), (x, 390, 90, 70), BLUE, f"players_{count}")
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
        self._sync_raise_total()

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
        title = self.font_xl.render("TEXAS HOLD'EM", True, GOLD)
        self.screen.blit(title, title.get_rect(center=(380, 260)))
        subtitle = self.font_md.render("Rules-first architecture. Personality later.", True, MUTED)
        self.screen.blit(subtitle, subtitle.get_rect(center=(380, 320)))
        self.buttons["single"].draw(self.screen, self.font_md)
        self.buttons["multi"].draw(self.screen, self.font_md)
        self.buttons["how_to"].draw(self.screen, self.font_md)

    def _draw_player_count(self):
        self.buttons["back"].draw(self.screen, self.font_sm)
        title = self.font_xl.render("MULTIPLAYER", True, GOLD)
        prompt = self.font_md.render("Choose number of players", True, WHITE)
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, 235)))
        self.screen.blit(prompt, prompt.get_rect(center=(WIDTH // 2, 305)))
        for count in PLAYER_COUNT_OPTIONS:
            self.buttons[f"players_{count}"].draw(self.screen, self.font_lg)

    def _draw_name_entry(self):
        self.buttons["back"].draw(self.screen, self.font_sm)
        title = self.font_xl.render("NAME ENTRY", True, GOLD)
        prompt = self.font_md.render(self.flow.current_name_prompt, True, WHITE)
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, 130)))
        self.screen.blit(prompt, prompt.get_rect(center=(WIDTH // 2, 225)))
        self._draw_entered_name_boxes()
        self.name_input.draw(self.screen, self.font_md, error=bool(self.flow.name_error))
        self.buttons["confirm_name"].draw(self.screen, self.font_md)
        if self.flow.name_error:
            error = self.font_sm.render(self.flow.name_error, True, RED)
            self.screen.blit(error, error.get_rect(center=(WIDTH // 2, 735)))

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
        pygame.draw.ellipse(self.screen, RIM, (110, 20, 980, 420))
        pygame.draw.ellipse(self.screen, FELT, (145, 45, 910, 370))
        pygame.draw.ellipse(self.screen, FELT_DARK, (195, 90, 810, 280), width=4)
        self._draw_status()
        self._draw_community_cards()
        self._draw_table_players()
        self._draw_current_player_panel()
        self._draw_controls()
        self.buttons["quit"].draw(self.screen, self.font_sm)
        self.buttons["hands"].draw(self.screen, self.font_sm)

    def _draw_status(self):
        street = "READY" if self.game.street == "IDLE" else self.game.street.replace("_", " ")
        street_text = self.font_lg.render(street, True, WHITE)
        pot_text = self.font_md.render(f"POT ${self.game.pot}", True, GOLD)
        msg_text = self.font_sm.render(self.game.message, True, MUTED)
        self.screen.blit(street_text, street_text.get_rect(center=(WIDTH // 2, 130)))
        self.screen.blit(pot_text, pot_text.get_rect(center=(WIDTH // 2, 168)))
        self.screen.blit(msg_text, msg_text.get_rect(center=(WIDTH // 2, 198)))

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
        center_x, center_y = 600, 215
        rx, ry = 430, 185
        for index, player in enumerate(self.game.players):
            angle = math.radians(90 + index * 360 / count)
            px = int(center_x + rx * math.cos(angle))
            py = int(center_y + ry * math.sin(angle))
            is_turn = index == self.game.current_player_index and self.game.street in ("PREFLOP", "FLOP", "TURN", "RIVER")
            border = GOLD if is_turn else (RED if player.eliminated else WHITE)
            pygame.draw.circle(self.screen, PANEL, (px, py), 42)
            pygame.draw.circle(self.screen, border, (px, py), 42, width=3)
            name = self.font_sm.render(player.name, True, WHITE)
            stack = self.font_sm.render("OUT" if player.eliminated else f"${player.stack}", True, GOLD)
            action = self.font_sm.render(player.last_action, True, MUTED)
            self.screen.blit(name, name.get_rect(center=(px, py - 15)))
            self.screen.blit(stack, stack.get_rect(center=(px, py + 8)))
            self.screen.blit(action, action.get_rect(center=(px, py + 31)))
            show_cards = self.game.street == "HAND_OVER" or (index == 0 and not player.is_bot)
            card_x = px - 45
            card_y = py + 48 if py < 210 else py - 108
            for card_index, card in enumerate(player.hand):
                if player.folded:
                    continue
                if show_cards:
                    self._draw_card(card, card_x + card_index * 42, card_y, 0.5, True)
                else:
                    self._draw_card_back(card_x + card_index * 42, card_y, 0.5)
            if self.game.street == "HAND_OVER" and player.hand and not player.folded:
                score = evaluate_hand(player.hand + self.game.community_cards)
                label = self.font_sm.render(score.name, True, GOLD)
                self.screen.blit(label, label.get_rect(center=(px, card_y + 82)))

    def _draw_current_player_panel(self):
        if self.game.street in ("IDLE",) or not self.game.players:
            return
        player = self.game.current_player
        panel = pygame.Rect(35, 505, 330, 235)
        pygame.draw.rect(self.screen, PANEL, panel, border_radius=8)
        pygame.draw.rect(self.screen, GOLD, panel, width=2, border_radius=8)
        pygame.draw.circle(self.screen, PANEL_LIGHT, (105, 595), 54)
        pygame.draw.circle(self.screen, GOLD, (105, 595), 54, width=3)
        initials = "".join(part[0] for part in player.name.split()[:2]).upper() or "P"
        initials_label = self.font_lg.render(initials, True, WHITE)
        self.screen.blit(initials_label, initials_label.get_rect(center=(105, 595)))

        name = self.font_lg.render(player.name, True, WHITE)
        stack = self.font_md.render("OUT" if player.eliminated else f"Stack: ${player.stack}", True, GOLD)
        action = self.font_sm.render(player.last_action or "Waiting", True, MUTED)
        self.screen.blit(name, (180, 545))
        self.screen.blit(stack, (180, 590))
        self.screen.blit(action, (180, 625))
        current = self.font_sm.render("Current player", True, MUTED)
        self.screen.blit(current, (180, 665))

        self._draw_current_player_hand(player)

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
            thinking = self.font_md.render(f"{current.name} is thinking...", True, MUTED)
            self.screen.blit(thinking, thinking.get_rect(center=(1048, 615)))
            return
        self.buttons["call"].draw(self.screen, self.font_sm)
        self.buttons["fold"].draw(self.screen, self.font_sm)
        if "raise" in self.game.legal_actions():
            self.buttons["raise"].draw(self.screen, self.font_sm)
            self.buttons["raise_down"].draw(self.screen, self.font_sm)
            self.buttons["raise_up"].draw(self.screen, self.font_sm)
            amount = self.font_md.render(f"${self.raise_total}", True, GOLD)
            self.screen.blit(amount, amount.get_rect(center=(1048, 580)))

    def _draw_card(self, card: Card, x, y, scale, face_up):
        if not face_up:
            self._draw_card_back(x, y, scale)
            return
        w, h = int(74 * scale), int(106 * scale)
        rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(self.screen, BLACK, rect.move(4, 4), border_radius=5)
        pygame.draw.rect(self.screen, WHITE, rect, border_radius=5)
        pygame.draw.rect(self.screen, BLACK, rect, width=2, border_radius=5)
        color = RED if card.suit in RED_SUITS else BLACK
        rank_font = pygame.font.SysFont("arial", max(14, int(22 * scale)), bold=True)
        suit_font = pygame.font.SysFont("arial", max(12, int(18 * scale)), bold=True)
        rank = rank_font.render(card.rank, True, color)
        suit = suit_font.render(SUIT_SYMBOLS[card.suit], True, color)
        self.screen.blit(rank, (x + 7 * scale, y + 7 * scale))
        self.screen.blit(suit, suit.get_rect(center=rect.center))

    def _draw_card_back(self, x, y, scale):
        w, h = int(74 * scale), int(106 * scale)
        rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(self.screen, BLACK, rect.move(4, 4), border_radius=5)
        pygame.draw.rect(self.screen, RED, rect, border_radius=5)
        pygame.draw.rect(self.screen, WHITE, rect, width=2, border_radius=5)
        inset = rect.inflate(-14 * scale, -14 * scale)
        pygame.draw.rect(self.screen, (130, 26, 36), inset, width=2, border_radius=4)


if __name__ == "__main__":
    PokerApp().run()
