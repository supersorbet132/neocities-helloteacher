import pygame
import random
import sys
import os




# --- INITIALIZATION & CONSTANTS ---
pygame.init()




# Screen Dimensions
WIDTH, HEIGHT = 1200, 800
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))    
pygame.display.set_caption("Classic Texas Hold'em")




# Game Constants
STARTING_STACK = 670
SMALL_BLIND = 10
BIG_BLIND = 20




# --- CLASSIC CASINO COLOR PALETTE ---
BG_COLOR = (20, 20, 20)           # Dark Gray Background
TABLE_FELT = (34, 139, 34)        # Classic Poker Green
TABLE_RIM = (101, 67, 33)         # Wood Brown
TABLE_OUTLINE = (50, 30, 10)      # Dark Wood Outline
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
GREEN_BTN = (0, 150, 0)           # Darker Green for buttons
BLUE_BTN = (0, 80, 180)           # Standard Blue
GOLD = (255, 215, 0)
GRAY = (100, 100, 100)
OVERLAY_BG = (0, 0, 0, 200)




# Fonts
FONT_XL = pygame.font.SysFont('arial', 60, bold=True)
FONT_LARGE = pygame.font.SysFont('arial', 40, bold=True)
FONT_MED = pygame.font.SysFont('arial', 24, bold=True)
FONT_SMALL = pygame.font.SysFont('arial', 18, bold=True)




# Card Dictionary Info
SUIT_COLORS = {'Hearts': RED, 'Diamonds': RED, 'Clubs': BLACK, 'Spades': BLACK}
SUIT_SYMBOLS = {'Hearts': '♥', 'Diamonds': '♦', 'Clubs': '♣', 'Spades': '♠'}
RANK_VALUES = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
    '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14
}




# --- CLASSES ---




class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.value = RANK_VALUES[rank]
        self.color = SUIT_COLORS[suit]
        self.symbol = SUIT_SYMBOLS[suit]
        self.rect = None
        self.is_face_up = True




    def draw(self, surface, x, y, scale=1.0, force_hidden=False):
        w, h = int(80 * scale), int(120 * scale)
        self.rect = pygame.Rect(x, y, w, h)
       
        # Simple Shadow
        pygame.draw.rect(surface, (0,0,0,100), (x+4, y+4, w, h), border_radius=4)




        if self.is_face_up and not force_hidden:
            # Front (White)
            pygame.draw.rect(surface, WHITE, self.rect, border_radius=4)
            pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=4)
           
            # Rank
            rank_font = pygame.font.SysFont('arial', int(22 * scale), bold=True)
            rank_text = rank_font.render(self.rank, True, self.color)
            surface.blit(rank_text, (x + 5, y + 5))
           
            # Suit Center
            suit_font = pygame.font.SysFont('arial', int(45 * scale))
            suit_text = suit_font.render(self.symbol, True, self.color)
            text_rect = suit_text.get_rect(center=(x + w//2, y + h//2))
            surface.blit(suit_text, text_rect)
           
            # Small Suit Corner
            small_suit = pygame.font.SysFont('arial', int(16 * scale))
            s_text = small_suit.render(self.symbol, True, self.color)
            surface.blit(s_text, (x + 5, y + 25))
        else:
            # Back (Classic Red Pattern)
            pygame.draw.rect(surface, RED, self.rect, border_radius=4)
            pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=4)
           
            # Crosshatch Pattern
            for i in range(0, w, 10):
                pygame.draw.line(surface, (150, 0, 0), (x+i, y), (x+i, y+h))
            for i in range(0, h, 10):
                pygame.draw.line(surface, (150, 0, 0), (x, y+i), (x+w, y+i))




    def __repr__(self):
        return f"{self.rank}{self.symbol}"




class Player:
    def __init__(self, name, is_bot, money, position, player_num):
        self.name = name
        self.player_num = player_num
        self.is_bot = is_bot
        self.money = money
        self.hand = []
        self.folded = False
        self.current_bet = 0
        self.position = position
        self.last_action = ""
        self.all_in = False
        self.eliminated = False




    def reset_round(self):
        self.hand = []
        self.folded = False
        self.all_in = False
        self.current_bet = 0
        self.last_action = ""




    def bot_action(self, current_bet_to_match, game_stage):
        if self.folded or self.all_in or self.eliminated: return 0
       
        call_amount = current_bet_to_match - self.current_bet
       
        if call_amount == 0:
            self.last_action = "Check"
            return 0
       
        if call_amount >= self.money:
            self.last_action = "All-In"
            bet = self.money
            self.money = 0
            self.current_bet += bet
            self.all_in = True  
            return bet




        roll = random.random()
        if roll > 0.85:
            raise_amt = call_amount + 50
            if raise_amt <= self.money:
                self.money -= raise_amt
                self.current_bet += raise_amt
                self.last_action = "Raise"
                return raise_amt
       
        if roll > 0.15:
            self.money -= call_amount
            self.current_bet += call_amount
            self.last_action = "Call"
            return call_amount
           
        self.folded = True
        self.last_action = "Fold"
        return 0




class Button:
    def __init__(self, text, x, y, w, h, color, action_code):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.base_color = color
        self.hover_color = tuple(min(c + 40, 255) for c in color)
        self.action_code = action_code
   
    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        col = self.hover_color if self.rect.collidepoint(mouse_pos) else self.base_color
       
        pygame.draw.rect(surface, col, self.rect, border_radius=5)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=5)
       
        text_surf = FONT_SMALL.render(self.text, True, WHITE if sum(col) < 500 else BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)




    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)




class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = GRAY
        self.text = text
        self.active = False
        self.error_state = False




    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = WHITE if self.active else GRAY
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    return self.text
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
        return None




    def draw(self, screen):
        pygame.draw.rect(screen, BLACK, self.rect)
        border_col = RED if self.error_state else (GOLD if self.active else GRAY)
        pygame.draw.rect(screen, border_col, self.rect, 2)
       
        text_surf = FONT_MED.render(self.text, True, WHITE)
        screen.blit(text_surf, (self.rect.x + 10, self.rect.y + 10))




class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-8, -2)
        self.size = random.randint(3, 6)
        self.life = 100




    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.4
        self.life -= 2
   
    def draw(self, surface):
        if self.life > 0:
            s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            alpha = int(self.life * 2.5)
            pygame.draw.circle(s, (*self.color, alpha), (self.size//2, self.size//2), self.size//2)
            surface.blit(s, (self.x, self.y))




# --- HELPER FUNCTIONS ---




def get_hand_score(cards):
    if not cards: return (0, 0)
    cards.sort(key=lambda c: c.value, reverse=True)
    values = [c.value for c in cards]
    suits = [c.suit for c in cards]
    unique_values = sorted(list(set(values)), reverse=True)
   
    is_flush = False
    for s in ['Hearts', 'Diamonds', 'Clubs', 'Spades']:
        if suits.count(s) >= 5: is_flush = True; break
           
    straight_high = 0
    is_straight = False
    for i in range(len(unique_values) - 4):
        if unique_values[i] - unique_values[i+4] == 4:
            is_straight = True; straight_high = unique_values[i]; break
    if not is_straight and {14, 2, 3, 4, 5}.issubset(set(unique_values)):
        is_straight = True; straight_high = 5




    counts = {v: values.count(v) for v in unique_values}
    four = [v for v, c in counts.items() if c == 4]
    three = [v for v, c in counts.items() if c == 3]
    two = [v for v, c in counts.items() if c == 2]
   
    if is_flush and is_straight: return (8, straight_high)
    if four: return (7, four[0])
    if three and two: return (6, (three[0], two[0]))
    if is_flush: return (5, 0)
    if is_straight: return (4, straight_high)
    if three: return (3, three[0])
    if len(two) >= 2: return (2, two[:2])
    if two: return (1, two[0])
    return (0, values[:5])




def load_bankroll():
    try:
        with open("poker_bankroll.txt", "r") as f: return int(f.read().strip())
    except: return STARTING_STACK




def save_bankroll(amount):
    try:
        with open("poker_bankroll.txt", "w") as f: f.write(str(int(amount)))
    except: pass




def draw_overlay(surface, title, lines):
    bg = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    bg.fill(OVERLAY_BG)
    surface.blit(bg, (0,0))
   
    box_rect = pygame.Rect(100, 80, 1000, 640)
    pygame.draw.rect(surface, (40, 40, 40), box_rect) # Dark gray box
    pygame.draw.rect(surface, GOLD, box_rect, 3) # Gold border
   
    t_surf = FONT_LARGE.render(title, True, GOLD)
    surface.blit(t_surf, (WIDTH//2 - t_surf.get_width()//2, 100))
   
    y = 160
    for line in lines:
        if line == "":
            y += 15
            continue
        l_surf = FONT_MED.render(line, True, WHITE)
        surface.blit(l_surf, (130, y))
        y += 30




# --- MAIN GAME ---




def main():
    human_money = load_bankroll()
   
    current_screen = "MENU"
    game_mode = "SINGLE"
   
    deck = []
    community_cards = []
    pot = 0
    players = []
    particles = []
   
    game_stage = "IDLE"
    turn_index = 0
    dealer_index = 0
    players_acted = 0
   
    # UI Flags
    show_cards_toggled = False
    waiting_for_next_player = False
    raising_mode = False
    pending_raise_amount = 0
    show_cheat_sheet = False
    name_error_message = ""
   
    bot_timer = 0 # Timer for bot action delay
   
    # Setup
    num_players_to_setup = 4
    setup_names_list = []
    name_input = InputBox(WIDTH//2 - 100, HEIGHT//2, 200, 50)
   
    # Buttons
    btn_single = Button("Single Player (Vs Bot)", 350, 350, 500, 60, BLUE_BTN, "mode_single")
    btn_multi = Button("Pass & Play (Multiplayer)", 350, 430, 500, 60, GREEN_BTN, "mode_multi")
    btn_tutorial = Button("How To Play", 350, 510, 500, 60, GRAY, "tutorial")
   
    setup_btns = [Button(f"{i} Players", 300 + ((i-2)%2)*250, 300 + ((i-2)//2)*80, 200, 50, BLUE_BTN, i) for i in range(2, 7)]
    btn_next_name = Button("CONFIRM NAME", 500, 550, 200, 50, GREEN_BTN, "next_name")
   
    btn_deal = Button("DEAL HAND", 950, 650, 200, 60, GOLD, "deal")
    btn_call = Button("CHECK / CALL", 950, 500, 200, 50, BLUE_BTN, "call")
    btn_raise_start = Button("RAISE...", 950, 430, 200, 50, BLUE_BTN, "raise_mode")
    btn_fold = Button("FOLD", 950, 570, 200, 50, RED, "fold")
    btn_quit = Button("QUIT GAME", 20, 20, 150, 40, RED, "quit")
    btn_cheat = Button("HANDS", 20, 70, 100, 40, GRAY, "cheat")
    btn_close_cheat = Button("CLOSE", 900, 650, 100, 50, RED, "close_cheat")
    btn_back_tut = Button("BACK", 50, 50, 100, 50, RED, "back")
   
    btn_r_plus = Button("+ $10", 1100, 430, 60, 50, GRAY, "r+")
    btn_r_minus = Button("- $10", 880, 430, 60, 50, GRAY, "r-")
    btn_confirm_raise = Button("CONFIRM", 950, 370, 200, 50, GREEN_BTN, "confirm_raise")
    btn_cancel_raise = Button("CANCEL", 950, 590, 200, 40, RED, "cancel_raise")
   
    btn_ready = Button("I AM READY", 400, 600, 400, 80, GREEN_BTN, "ready")
   
    btn_peek = Button("SHOW / HIDE", 950, 720, 200, 50, GRAY, "peek")




    # Instructions
    tutorial_lines = [
        "OBJECTIVE: Win the pot with the best 5-card hand or force others to fold.",
        "",
        "GAME FLOW:",
        "1. BLINDS: Two players left of dealer post bets before cards are dealt.",
        "2. PREFLOP: You get 2 hole cards. Action starts left of Big Blind.",
        "   Options: Call (Match Bet), Raise (Increase Bet), Fold (Quit Hand).",
        "3. THE FLOP: 3 Community cards dealt face up. Betting round follows.",
        "4. THE TURN: 4th Community card dealt. Betting round follows.",
        "5. THE RIVER: 5th Community card dealt. Final betting round.",
        "6. SHOWDOWN: Players reveal cards. Best hand wins.",
        "",
        "HAND RANKINGS are available via the 'HANDS' button in-game."
    ]




    # Cheat Sheet
    cheat_lines = [
        "ROYAL FLUSH: A, K, Q, J, 10 of same suit (e.g. A♥ K♥ Q♥ J♥ 10♥)",
        "STRAIGHT FLUSH: 5 consecutive cards of same suit (e.g. 9♣ 8♣ 7♣ 6♣ 5♣)",
        "QUADS: 4 cards of same rank (e.g. Q♦ Q♣ Q♥ Q♠)",
        "FULL HOUSE: 3 of a kind + Pair (e.g. J♥ J♣ J♦ 8♠ 8♥)",
        "FLUSH: 5 cards of same suit, any order (e.g. K♠ J♠ 9♠ 4♠ 2♠)",
        "STRAIGHT: 5 consecutive ranks, any suit (e.g. 5, 6, 7, 8, 9)",
        "TRIPS: 3 cards of same rank (e.g. 7♣ 7♦ 7♠)",
        "TWO PAIR: Two different pairs (e.g. A-A and 8-8)",
        "PAIR: Two cards of same rank (e.g. K-K)",
        "HIGH CARD: Highest card value (A > K > Q > J > 10...)"
    ]
   
    clock = pygame.time.Clock()
    running = True




    while running:
        SCREEN.fill(BG_COLOR)
        events = pygame.event.get()
        mouse_pos = pygame.mouse.get_pos()




        for event in events:
            if event.type == pygame.QUIT:
                running = False
           
            if current_screen == "SETUP_NAMES":
                name_input.handle_event(event)
           
            if event.type == pygame.MOUSEBUTTONDOWN:
                if show_cheat_sheet:
                    if btn_close_cheat.is_clicked(mouse_pos): show_cheat_sheet = False
                    continue

                if current_screen == "MENU":
                    if btn_single.is_clicked(mouse_pos):
                        game_mode = "SINGLE"; current_screen = "SETUP_PLAYERS"
                    elif btn_multi.is_clicked(mouse_pos):
                        game_mode = "MULTI"; current_screen = "SETUP_PLAYERS"
                    elif btn_tutorial.is_clicked(mouse_pos):
                        current_screen = "TUTORIAL"

                elif current_screen == "TUTORIAL":
                    if btn_back_tut.is_clicked(mouse_pos): current_screen = "MENU"

                elif current_screen == "SETUP_PLAYERS":
                    for b in setup_btns:
                        if b.is_clicked(mouse_pos):
                            num_players_to_setup = b.action_code
                            setup_names_list = []
                            current_screen = "SETUP_NAMES"
                            name_input.text = ""
                            name_error_message = ""

                elif current_screen == "SETUP_NAMES":
                    if btn_next_name.is_clicked(mouse_pos):
                        raw_name = name_input.text.strip()
                        if not raw_name:
                            name_error_message = "Name cannot be empty!"
                        elif raw_name in setup_names_list:
                            name_error_message = "Name already taken!"
                            name_input.error_state = True
                        else:
                            name_input.error_state = False
                            setup_names_list.append(raw_name)
                            name_input.text = ""
                            name_error_message = ""
                           
                            if len(setup_names_list) >= num_players_to_setup:
                                players = []
                                cx, cy = 600, 400
                                rx, ry = 480, 260
                                import math
                                for i in range(num_players_to_setup):
                                    angle = math.radians(90 + (360/num_players_to_setup)*i)
                                    px = cx + rx * math.cos(angle) - 40
                                    py = cy + ry * math.sin(angle) - 40
                                    is_bot = (game_mode == "SINGLE" and i > 0)
                                    p_name = setup_names_list[i]
                                    players.append(Player(p_name, is_bot, STARTING_STACK, (int(px), int(py)), i+1))
                                current_screen = "GAME"




                elif current_screen == "GAME":
                    if waiting_for_next_player:
                        if btn_ready.is_clicked(mouse_pos): waiting_for_next_player = False
                        continue
                   
                    if btn_quit.is_clicked(mouse_pos):
                        if game_mode == "SINGLE": save_bankroll(players[0].money)
                        running = False
                   
                    if btn_cheat.is_clicked(mouse_pos):
                        show_cheat_sheet = True
                   
                    if btn_deal.is_clicked(mouse_pos) and game_stage in ["IDLE", "SHOWDOWN"]:
                        deck = [Card(r, s) for r in RANK_VALUES for s in SUIT_COLORS]
                        random.shuffle(deck)
                        community_cards = []
                        particles = []
                        pot = 0
                       
                        active_count = 0
                        for p in players:
                            if p.money <= 0 and not p.eliminated:
                                p.eliminated = True
                            if not p.eliminated:
                                active_count += 1
                                p.reset_round()
                                p.hand = [deck.pop(), deck.pop()]
                                for c in p.hand: c.is_face_up = True




                        if active_count < 2:
                            game_stage = "IDLE"
                        else:
                            game_stage = "PREFLOP"
                            dealer_index = (dealer_index + 1) % len(players)
                            while players[dealer_index].eliminated:
                                dealer_index = (dealer_index + 1) % len(players)




                            sb_idx = (dealer_index + 1) % len(players)
                            while players[sb_idx].eliminated: sb_idx = (sb_idx + 1) % len(players)
                           
                            bb_idx = (sb_idx + 1) % len(players)
                            while players[bb_idx].eliminated: bb_idx = (bb_idx + 1) % len(players)




                            sb_p = players[sb_idx]
                            sb_amt = min(SMALL_BLIND, sb_p.money)
                            sb_p.money -= sb_amt
                            sb_p.current_bet = sb_amt
                            pot += sb_amt




                            bb_p = players[bb_idx]
                            bb_amt = min(BIG_BLIND, bb_p.money)
                            bb_p.money -= bb_amt
                            bb_p.current_bet = bb_amt
                            pot += bb_amt




                            turn_index = (bb_idx + 1) % len(players)
                            while players[turn_index].eliminated: turn_index = (turn_index + 1) % len(players)
                           
                            players_acted = 0
                            show_cards_toggled = False
                            if game_mode == "MULTI": waiting_for_next_player = True
                            bot_timer = 0




                    cur_p = players[turn_index]
                    if game_stage not in ["IDLE", "SHOWDOWN"] and not cur_p.is_bot and not cur_p.eliminated:
                       
                        if btn_peek.is_clicked(mouse_pos) and game_mode == "MULTI":
                            show_cards_toggled = not show_cards_toggled




                        if raising_mode:
                            if btn_cancel_raise.is_clicked(mouse_pos): raising_mode = False
                            elif btn_r_plus.is_clicked(mouse_pos):
                                if pending_raise_amount + 10 <= cur_p.money: pending_raise_amount += 10
                            elif btn_r_minus.is_clicked(mouse_pos):
                                if pending_raise_amount - 10 > 0: pending_raise_amount -= 10
                            elif btn_confirm_raise.is_clicked(mouse_pos):
                                cur_p.money -= pending_raise_amount
                                cur_p.current_bet += pending_raise_amount
                                pot += pending_raise_amount
                                cur_p.last_action = "Raise"
                                players_acted = 0
                               
                                turn_index = (turn_index + 1) % len(players)
                                while players[turn_index].eliminated: turn_index = (turn_index + 1) % len(players)
                                players_acted += 1
                                raising_mode = False
                                show_cards_toggled = False
                                if game_mode == "MULTI": waiting_for_next_player = True




                        else:
                            action_done = False
                            if btn_fold.is_clicked(mouse_pos):
                                cur_p.folded = True
                                cur_p.last_action = "Fold"
                                action_done = True
                            elif btn_call.is_clicked(mouse_pos):
                                high_bet = max(p.current_bet for p in players)
                                diff = high_bet - cur_p.current_bet
                                if cur_p.money >= diff:
                                    cur_p.money -= diff
                                    cur_p.current_bet += diff
                                    pot += diff
                                    cur_p.last_action = "Call" if diff > 0 else "Check"
                                else:
                                    cur_p.last_action = "All-In"
                                    cur_p.all_in = True
                                    pot += cur_p.money
                                    cur_p.current_bet += cur_p.money
                                    cur_p.money = 0
                                action_done = True
                            elif btn_raise_start.is_clicked(mouse_pos):
                                high_bet = max(p.current_bet for p in players)
                                call_amt = high_bet - cur_p.current_bet
                                pending_raise_amount = call_amt + BIG_BLIND
                                if pending_raise_amount > cur_p.money: pending_raise_amount = cur_p.money
                                raising_mode = True




                            if action_done:
                                # FIX: Check if game should end immediately (only 1 player left)
                                survivors = [p for p in players if not p.folded and not p.eliminated]
                                if len(survivors) == 1:
                                    # Game Over -> Winner. Skip pass device.
                                    waiting_for_next_player = False
                                else:
                                    turn_index = (turn_index + 1) % len(players)
                                    while players[turn_index].eliminated: turn_index = (turn_index + 1) % len(players)
                                    players_acted += 1
                                    show_cards_toggled = False
                                    if game_mode == "MULTI": waiting_for_next_player = True
                                bot_timer = 0




        # --- UPDATE LOOP ---
        if current_screen == "GAME" and game_stage not in ["IDLE", "SHOWDOWN"] and not waiting_for_next_player and not show_cheat_sheet:
            active = [p for p in players if not p.folded and not p.eliminated and not p.all_in]
            not_folded = [p for p in players if not p.folded and not p.eliminated]
            high_bet = max(p.current_bet for p in players if not p.eliminated)
            all_matched = all(p.current_bet == high_bet or p.folded or p.all_in for p in not_folded)
           
            if len(not_folded) == 1:
                w = not_folded[0]
                w.money += pot
                pot = 0
                game_stage = "SHOWDOWN"
                particles.append(Particle(w.position[0], w.position[1], GOLD))
           
            elif all_matched and players_acted >= len(not_folded):
                players_acted = 0
                turn_index = (dealer_index + 1) % len(players)
                while players[turn_index].eliminated or players[turn_index].folded or players[turn_index].all_in:
                    turn_index = (turn_index + 1) % len(players)
                    if turn_index == (dealer_index + 1) % len(players): break




                if game_stage == "PREFLOP":
                    community_cards = [deck.pop() for _ in range(3)]
                    game_stage = "FLOP"
                elif game_stage == "FLOP":
                    community_cards.append(deck.pop())
                    game_stage = "TURN"
                elif game_stage == "TURN":
                    community_cards.append(deck.pop())
                    game_stage = "RIVER"
                elif game_stage == "RIVER":
                    game_stage = "SHOWDOWN"
                    best = -1
                    winners = []
                    for p in not_folded:
                        s = get_hand_score(p.hand + community_cards)[0]
                        if s > best: best = s; winners = [p]
                        elif s == best: winners.append(p)
                   
                    if winners:
                        share = pot // len(winners)
                        for w in winners:
                            w.money += share
                            w.last_action = "WIN"
                            for _ in range(40): particles.append(Particle(w.position[0], w.position[1], GOLD))
                        pot = 0
                        if game_mode == "SINGLE": save_bankroll(players[0].money)
               
                if game_stage != "SHOWDOWN" and game_mode == "MULTI":
                     waiting_for_next_player = True
           
            else:
                curr = players[turn_index]
                if curr.folded or curr.all_in or curr.eliminated:
                    turn_index = (turn_index + 1) % len(players)
                elif curr.is_bot:
                    # FIX: Add Delay for CPU
                    if bot_timer == 0:
                        bot_timer = pygame.time.get_ticks()
                   
                    # Wait 1000ms (1 second) before acting
                    if pygame.time.get_ticks() - bot_timer > 1000:
                        added = curr.bot_action(high_bet, game_stage)
                        pot += added
                        if curr.last_action == "Raise":
                            players_acted = 0
                        players_acted += 1
                        turn_index = (turn_index + 1) % len(players)
                        while players[turn_index].eliminated: turn_index = (turn_index + 1) % len(players)
                        bot_timer = 0




        # --- DRAWING ---
        if current_screen == "MENU":
            t = FONT_XL.render("CLASSIC HOLD'EM", True, GOLD)
            st = FONT_MED.render("Standard Edition", True, WHITE)
            SCREEN.blit(t, (WIDTH//2 - t.get_width()//2, 150))
            SCREEN.blit(st, (WIDTH//2 - st.get_width()//2, 220))
            btn_single.draw(SCREEN)
            btn_multi.draw(SCREEN)
            btn_tutorial.draw(SCREEN)




        elif current_screen == "TUTORIAL":
            draw_overlay(SCREEN, "HOW TO PLAY", tutorial_lines)
            btn_back_tut.draw(SCREEN)




        elif current_screen == "SETUP_PLAYERS":
            t = FONT_LARGE.render("SELECT PLAYERS", True, GOLD)
            SCREEN.blit(t, (WIDTH//2 - t.get_width()//2, 150))
            for b in setup_btns: b.draw(SCREEN)




        elif current_screen == "SETUP_NAMES":
            t = FONT_LARGE.render(f"NAME FOR PLAYER {len(setup_names_list)+1}", True, GOLD)
            SCREEN.blit(t, (WIDTH//2 - t.get_width()//2, 200))
            name_input.draw(SCREEN)
            btn_next_name.draw(SCREEN)
           
            if name_error_message:
                err = FONT_SMALL.render(name_error_message, True, RED)
                SCREEN.blit(err, (WIDTH//2 - err.get_width()//2, 450))




            y = 300
            for i, n in enumerate(setup_names_list):
                txt = FONT_SMALL.render(f"P{i+1}: {n}", True, GRAY)
                SCREEN.blit(txt, (WIDTH//2 - 200, y))
                y += 25




        elif current_screen == "GAME":
            # Table Background - Classic Green Felt & Wood
            pygame.draw.ellipse(SCREEN, TABLE_RIM, (100, 150, 1000, 500))
            pygame.draw.ellipse(SCREEN, TABLE_FELT, (120, 170, 960, 460))
            pygame.draw.ellipse(SCREEN, TABLE_OUTLINE, (120, 170, 960, 460), 3)
           
            st = FONT_LARGE.render(game_stage, True, WHITE)
            pt = FONT_MED.render(f"POT: ${pot}", True, GOLD)
            SCREEN.blit(st, (WIDTH//2 - st.get_width()//2, 240))
            SCREEN.blit(pt, (WIDTH//2 - pt.get_width()//2, 280))




            cx = WIDTH//2 - (5 * 90)//2
            for i, c in enumerate(community_cards):
                c.draw(SCREEN, cx + (i * 90), HEIGHT//2 - 60)




            for i, p in enumerate(players):
                is_turn = (i == turn_index and game_stage not in ["IDLE", "SHOWDOWN"])
                px, py = p.position
               
                if is_turn:
                    # Gold highlight for turn
                    pygame.draw.circle(SCREEN, GOLD, (px+40, py+40), 50, 4)
                   
                    # FIX: Show "YOUR TURN" text for human players
                    if not p.is_bot and not p.eliminated:
                         yt = FONT_LARGE.render("YOUR TURN", True, GOLD)
                         # Draw near center table or near player
                         SCREEN.blit(yt, (WIDTH//2 - yt.get_width()//2, 380))




                col = RED if p.eliminated else (GRAY if p.folded else WHITE)
                pygame.draw.circle(SCREEN, (20,20,30), (px+40, py+40), 40)
                pygame.draw.circle(SCREEN, col, (px+40, py+40), 38, 2)
               
                name_s = FONT_SMALL.render(p.name, True, WHITE)
                name_rect = name_s.get_rect(center=(px+40, py - 50))
                SCREEN.blit(name_s, name_rect)




                if p.eliminated:
                    mon_s = FONT_SMALL.render("OUT", True, RED)
                else:
                    mon_s = FONT_SMALL.render(f"${p.money}", True, GOLD)
                mon_rect = mon_s.get_rect(center=(px+40, py - 25))
                SCREEN.blit(mon_s, mon_rect)
               
                act_s = FONT_SMALL.render(p.last_action, True, GOLD)
                act_rect = act_s.get_rect(center=(px+40, py + 40))
                SCREEN.blit(act_s, act_rect)




                if not p.folded and not p.eliminated:
                    should_show = False
                    if game_stage == "SHOWDOWN": should_show = True
                    elif game_mode == "SINGLE" and i == 0: should_show = True
                    elif game_mode == "MULTI" and i == turn_index and show_cards_toggled and not waiting_for_next_player: should_show = True
                   
                    for k, card in enumerate(p.hand):
                        card.draw(SCREEN, px + (k * 40), py + 90, 0.5, force_hidden=not should_show)




            if waiting_for_next_player:
                draw_overlay(SCREEN, f"{players[turn_index].name}'s TURN", ["Pass Device"])
                btn_ready.draw(SCREEN)
            elif show_cheat_sheet:
                draw_overlay(SCREEN, "HAND RANKINGS", cheat_lines)
                btn_close_cheat.draw(SCREEN)
            else:
                if game_stage in ["IDLE", "SHOWDOWN"]:
                    btn_deal.draw(SCREEN)
                else:
                    cur = players[turn_index]
                    if not cur.is_bot:
                        if raising_mode:
                            pygame.draw.rect(SCREEN, (50, 50, 50), (800, 350, 400, 300), border_radius=5)
                            pygame.draw.rect(SCREEN, WHITE, (800, 350, 400, 300), 2, border_radius=5)
                            amt_s = FONT_XL.render(f"${pending_raise_amount}", True, GOLD)
                            SCREEN.blit(amt_s, (950, 420))
                           
                            btn_r_plus.draw(SCREEN)
                            btn_r_minus.draw(SCREEN)
                            btn_confirm_raise.draw(SCREEN)
                            btn_cancel_raise.draw(SCREEN)
                        else:
                            btn_call.draw(SCREEN)
                            btn_raise_start.draw(SCREEN)
                            btn_fold.draw(SCREEN)
                            if game_mode == "MULTI": btn_peek.draw(SCREEN)




            btn_quit.draw(SCREEN)
            btn_cheat.draw(SCREEN)
           
            for p in particles[:]:
                p.update()
                p.draw(SCREEN)
                if p.life <= 0: particles.remove(p)




        pygame.display.flip()
        clock.tick(60)




    pygame.quit()
    sys.exit()




if __name__ == "__main__":
    main()



