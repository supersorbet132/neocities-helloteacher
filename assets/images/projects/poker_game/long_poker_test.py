import pygame
import random
import sys
import os
import math # Necessary for the POKER title bobbing animation


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


# --- GLOBAL ASSET STORAGE ---
ASSETS = {}

def load_assets():
    """Loads all necessary game images using os.path.join for cross-platform safety."""
    global ASSETS
    try:
        # Load Title Screen Assets
        ASSETS['TITLE_BG'] = pygame.image.load(os.path.join("Title", "Title_BG.png")).convert_alpha()
        
        # NEW LAYERS for Title Screen
        ASSETS['TITLE_CARDS_LAYER'] = pygame.image.load(os.path.join("Title", "Title_Cards.png")).convert_alpha()
        ASSETS['TITLE_FOLDER'] = pygame.image.load(os.path.join("Title", "Title_Folder.png")).convert_alpha()
        ASSETS['TITLE_TEXAS'] = pygame.image.load(os.path.join("Title", "Title_Texas.png")).convert_alpha()
        ASSETS['TITLE_HOLDEM'] = pygame.image.load(os.path.join("Title", "Title_Holdem.png")).convert_alpha()
        
        # Load Bobbing Letters
        ASSETS['TITLE_LETTERS'] = {
            'P': pygame.image.load(os.path.join("Title", "Title_P.png")).convert_alpha(),
            'O': pygame.image.load(os.path.join("Title", "Title_O.png")).convert_alpha(),
            'K': pygame.image.load(os.path.join("Title", "Title_K.png")).convert_alpha(),
            'E': pygame.image.load(os.path.join("Title", "Title_E.png")).convert_alpha(),
            'R': pygame.image.load(os.path.join("Title", "Title_R.png")).convert_alpha(),
        }
        
        # Load Title Buttons
        ASSETS['TITLE_BTN_SINGLE'] = pygame.image.load(os.path.join("Title", "Title_Button_SinglePlayer.png")).convert_alpha()
        ASSETS['TITLE_BTN_MULTI'] = pygame.image.load(os.path.join("Title", "Title_Button_Multiplayer.png")).convert_alpha()
        ASSETS['TITLE_BTN_TUTORIAL'] = pygame.image.load(os.path.join("Title", "Title_Button_HowToPlay.png")).convert_alpha()
        
        # Load Player Select Assets
        ASSETS['PS_BG'] = pygame.image.load(os.path.join("Player Select", "PlayerSelect_BG.png")).convert_alpha()
        ASSETS['PS_TITLE'] = pygame.image.load(os.path.join("Player Select", "PlayerSelect_Title.png")).convert_alpha()
        ASSETS['PS_BTNS'] = {}
        for i in range(2, 7):
            ASSETS['PS_BTNS'][i] = pygame.image.load(os.path.join("Player Select", f"PlayerSelect_Button_{i}P.png")).convert_alpha()
        ASSETS['PS_BTNS']['FUNNY'] = pygame.image.load(os.path.join("Player Select", "PlayerSelect_Button_Funny.png")).convert_alpha()

        # --- NEW: Load Name Entry Assets ---
        #ASSETS['PS_NAME_INPUT_BG'] = pygame.image.load(os.path.join("Player Select", "PlayerSelect_NameInput_BG.png")).convert_alpha()
        ASSETS['PS_NAME_INPUT_TITLE'] = pygame.image.load(os.path.join("Player Select", "PlayerSelect_EnterName.png")).convert_alpha()
        ASSETS['PS_NAME_INPUT_BTN'] = pygame.image.load(os.path.join("Player Select", "PlayerSelect_Button_Confirm.png")).convert_alpha()

        # Load Card Assets (Placeholder)
        # Assuming a "Cards" folder exists for future steps
        #ASSETS['CARD_BACK'] = pygame.image.load(os.path.join("Cards", "Card_Back.png")).convert_alpha()


    except pygame.error as e:
        print(f"Error loading assets: {e}")
        print("Ensure the image files and folder structure (Title/, Player Select/, Cards/) are correct and in the same directory as the script.")
        pygame.quit()
        sys.exit()


# --- CLASSES ---


class Card:
# Card Class remains the same
# ... (omitted for brevity)
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.value = RANK_VALUES[rank]
        self.color = SUIT_COLORS[suit]
        self.symbol = SUIT_SYMBOLS[suit]
        self.rect = None
        self.is_face_up = True
        
        # New: Store the image key (e.g., 'AS', 'H2', etc.)
        self.image_key = f"{self.rank[0]}{self.suit[0]}" 

    def draw(self, surface, x, y, scale=1.0, force_hidden=False):
        # NOTE: This entire method will be replaced when card images are available
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
# Player Class remains the same
# ... (omitted for brevity)
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
    def __init__(self, text, x, y, w, h, color, action_code, image=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.action_code = action_code
        self.image = image
        
        # New properties for image hover effects
        self.base_scale = 1.0
        self.hover_scale = 1.1 # Scale the image up by 10% on hover
        self.current_scale = 1.0
        
        # If no image is used, use legacy color change
        if not image:
            self.base_color = color
            self.hover_color = tuple(min(c + 40, 255) for c in color)
            
    def update(self, is_hovering):
        """Smoothly adjusts the scale based on the hover state."""
        target = self.hover_scale if is_hovering else self.base_scale
        
        # Linear Interpolation (Lerp) for smooth scaling
        self.current_scale += (target - self.current_scale) * 0.2
        

    def draw(self, surface, offset_x=0, offset_y=0):
        # Adjust position based on viewport offset
        draw_rect = self.rect.move(offset_x, offset_y)
        mouse_pos = pygame.mouse.get_pos()
        
        is_hovering = draw_rect.collidepoint(mouse_pos)
        self.update(is_hovering) # Update the scale based on hover
        
        if self.image:
            # --- Draw the Image Asset with Scaling (Hue change removed) ---
            
            # 1. Scaling the image
            new_w = int(self.image.get_width() * self.current_scale)
            new_h = int(self.image.get_height() * self.current_scale)
            scaled_img = pygame.transform.smoothscale(self.image, (new_w, new_h))
            
            # 2. Centering the scaled image
            x_pos = draw_rect.x + (draw_rect.width // 2) - (new_w // 2)
            y_pos = draw_rect.y + (draw_rect.height // 2) - (new_h // 2)
            
            surface.blit(scaled_img, (x_pos, y_pos))
            
            # NOTE: Hue change removed as requested.
            
        else:
            # --- Draw Legacy Color Rectangle (for game buttons) ---
            col = self.hover_color if is_hovering else self.base_color
            
            pygame.draw.rect(surface, col, draw_rect, border_radius=5)
            pygame.draw.rect(surface, WHITE, draw_rect, 2, border_radius=5)
       
            text_surf = FONT_SMALL.render(self.text, True, WHITE if sum(col) < 500 else BLACK)
            text_rect = text_surf.get_rect(center=draw_rect.center)
            surface.blit(text_surf, text_rect)


    def is_clicked(self, pos, offset_x=0, offset_y=0):
        # Check collision against the viewport-adjusted rect
        adjusted_rect = self.rect.move(offset_x, offset_y)
        return adjusted_rect.collidepoint(pos)


class InputBox:
# FIX: The entire InputBox class is updated to be offset-aware.
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = GRAY
        self.text = text
        self.active = False
        self.error_state = False

    # FIX: Added offset_x and offset_y to correctly check collision against the VISIBLE element.
    def handle_event(self, event, offset_x=0, offset_y=0):
        # Create an adjusted rect for collision check against event.pos
        adjusted_rect = self.rect.move(offset_x, offset_y) 

        if event.type == pygame.MOUSEBUTTONDOWN:
            if adjusted_rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = WHITE if self.active else GRAY
            # Return None, as a click only activates/deactivates
            return None
            
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    return self.text # Return text on Enter key press
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
        return None

    def draw(self, screen, offset_x=0, offset_y=0):
        draw_rect = self.rect.move(offset_x, offset_y)
        pygame.draw.rect(screen, BLACK, draw_rect)
        border_col = RED if self.error_state else (GOLD if self.active else GRAY)
        pygame.draw.rect(screen, border_col, draw_rect, 2)
       
        text_surf = FONT_MED.render(self.text, True, WHITE)
        screen.blit(text_surf, (draw_rect.x + 10, draw_rect.y + 10))


# --- HELPER FUNCTIONS ---


def get_hand_score(cards):
# Hand scoring function remains the same
# ... (omitted for brevity)
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
# Bankroll functions remain the same
# ... (omitted for brevity)
    try:
        with open("poker_bankroll.txt", "r") as f: return int(f.read().strip())
    except: return STARTING_STACK


def save_bankroll(amount):
    try:
        with open("poker_bankroll.txt", "w") as f: f.write(str(int(amount)))
    except: pass


def draw_overlay(surface, title, lines):
# Overlay function remains the same
# ... (omitted for brevity)
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
    # --- CALL ASSET LOADING ---
    load_assets()
    
    human_money = load_bankroll()
   
    current_screen = "MENU"
    next_screen = "MENU" # NEW: State to transition to
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
    
    # --- NEW VIEWPORT AND ANIMATION VARIABLES ---
    screen_offset_x = 0  # Current visual offset for the X-axis (between MENU and SETUP/GAME)
    target_offset_x = 0  # Where the X-viewport needs to slide to
    
    # --- NEW SETUP ANIMATION VARIABLES ---
    setup_offset_y = 0  # Current visual offset for the Y-axis (between SETUP_PLAYERS and SETUP_NAMES)
    target_setup_offset_y = 0 # Where the Y-viewport needs to slide to
    
    # Helper for the bobbing POKER letters
    letter_offsets = {char: 0 for char in 'POKER'}
    bob_time = 0
   
    bot_timer = 0 # Timer for bot action delay
   
    # Setup
    num_players_to_setup = 4
    setup_names_list = []
    
    # --- TITLE SCREEN BUTTONS (New Positioning) ---
    # Texas/Hold-em (Far left, used as hoverable background elements)
    # The rect only defines the hover area.
    btn_texas = Button("", 20, 70, 300, 100, None, "tutorial", image=ASSETS['TITLE_TEXAS'])
    btn_holdem = Button("", 140, 155, 300, 100, None, "tutorial", image=ASSETS['TITLE_HOLDEM'])

    # Main Buttons (Aligned vertically on the right side)
    BUTTON_WIDTH, BUTTON_HEIGHT = 400, 70
    BUTTON_LEFT_X = 700 
    
    btn_single = Button("", BUTTON_LEFT_X-75, 160, BUTTON_WIDTH, BUTTON_HEIGHT, None, "mode_single", image=ASSETS['TITLE_BTN_SINGLE'])
    btn_multi = Button("", BUTTON_LEFT_X+60, 360, BUTTON_WIDTH, BUTTON_HEIGHT, None, "mode_multi", image=ASSETS['TITLE_BTN_MULTI'])
    btn_tutorial = Button("", BUTTON_LEFT_X-160, 605, BUTTON_WIDTH, BUTTON_HEIGHT, None, "tutorial", image=ASSETS['TITLE_BTN_TUTORIAL'])

    # --- PLAYER SELECT SCREEN BUTTONS (Shifted by +WIDTH) ---
    # These coordinates are relative to the Player Select viewport (WIDTH, 0)
    base_x = WIDTH + 300
    base_y = 350
    # Player select buttons already use tighter rects (220x70)
    setup_btns = [
        Button("", base_x - 50, base_y - 100, 220, 70, None, 2, image=ASSETS['PS_BTNS'][2]),
        Button("", base_x + 380, base_y - 100, 220, 70, None, 3, image=ASSETS['PS_BTNS'][3]),
        Button("", base_x - 40, base_y + 80, 220, 70, None, 4, image=ASSETS['PS_BTNS'][4]),
        Button("", base_x + 400, base_y + 80, 220, 70, None, 5, image=ASSETS['PS_BTNS'][5]),
        Button("", base_x - 20, base_y + 280, 220, 70, None, 6, image=ASSETS['PS_BTNS'][6]),
    ]
    btn_funny = Button("", base_x + 330, base_y + 280, 220, 70, None, 7, image=ASSETS['PS_BTNS']['FUNNY'])
    setup_btns.append(btn_funny)
    
    # --- NAME INPUT ELEMENTS (Shifted by +WIDTH and placed below the fold: +HEIGHT) ---
    
    # Input box and button should be placed where they appear after the slide.
    # The whole setup viewport is at (WIDTH + screen_offset_x, 0)
    # The name entry elements start at Y=HEIGHT and slide up to Y=0
    name_input_x = WIDTH + (WIDTH // 2) - 100 # Center X relative to the setup viewport
    name_input_y_start = 450 + HEIGHT # Starts off-screen (below 800), slides to 450
    
    # Input box needs to be defined relative to its final position (450)
    name_input = InputBox(name_input_x, name_input_y_start, 200, 50)
    
    # Confirm button is image-based now
    btn_next_name = Button("", name_input_x - 100, name_input_y_start + 150, 400, 70, None, "next_name", image=ASSETS['PS_NAME_INPUT_BTN'])
    
    
    # Old button definitions retained for the GAME screen
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
        " Options: Call (Match Bet), Raise (Increase Bet), Fold (Quit Hand).",
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
        "STRAIGHT: 5 consecutive cards of any suit (e.g. 9♥ 8♣ 7♦ 6♠ 5♥)",
        "TRIPS: 3 cards of the same rank (e.g. A♠ A♥ A♦)",
        "TWO PAIR: Two different pairs (e.g. K♠ K♥ 5♦ 5♣)",
        "PAIR: 2 cards of the same rank (e.g. J♣ J♦)",
        "HIGH CARD: Highest single card if no other hand is made."
    ]


    clock = pygame.time.Clock()
    running = True


    while running:
        # --- FRAME-RATE INDEPENDENT UPDATES ---
        dt = clock.tick(60) / 1000.0
        bob_time += dt * 5 # Control the speed of the bobbing motion
       
        # --- VIEWPORT ANIMATION LOGIC (Horizontal Slide) ---
        if abs(screen_offset_x - target_offset_x) > 1:
            screen_offset_x += (target_offset_x - screen_offset_x) * 0.15
        else:
            screen_offset_x = target_offset_x
            current_screen = next_screen # Finalize screen transition


        # --- INPUT HANDLER / EVENT LOOP ---
        trigger_name_submit = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if current_screen == "GAME" and game_mode == "SINGLE": save_bankroll(players[0].money)
                running = False
                
            # --- FIX: Centralized Input Handling for Name Entry ---
            # This handles both MOUSEBUTTONDOWN (for activation) and KEYDOWN (for typing/Enter)
            if current_screen == "SETUP_NAMES" and setup_offset_y == -HEIGHT:
                
                # The Y offset calculation for the input box and button needs to match the drawing code.
                # Draw: name_input.draw(SCREEN, screen_offset_x, name_element_offset_y-800)
                # where name_element_offset_y is setup_offset_y + HEIGHT, which is 0 when slide is complete.
                # Therefore, the offset is -800.
                name_element_offset_y = setup_offset_y + HEIGHT
                offset_for_input = name_element_offset_y - 800
                
                # Pass all events to the InputBox with the correct offsets
                entered_name = name_input.handle_event(event, screen_offset_x, offset_for_input)
                
                # If the user pressed ENTER, we set a flag for the submission logic below
                if entered_name is not None and event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    trigger_name_submit = True
                
            
            # --- MOUSE BUTTON DOWN EVENT HANDLING ---
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos

                if show_cheat_sheet:
                    if btn_close_cheat.is_clicked(mouse_pos): show_cheat_sheet = False
                    continue
                
                # --- Menu Screen (MENU) Logic ---
                if current_screen == "MENU" and target_offset_x == 0:
                    # Pass the current offset to check if the button was clicked in the visible area
                    if btn_single.is_clicked(mouse_pos, screen_offset_x):
                        game_mode = "SINGLE"; target_offset_x = -WIDTH; next_screen = "SETUP_PLAYERS"
                    elif btn_multi.is_clicked(mouse_pos, screen_offset_x):
                        game_mode = "MULTI"; target_offset_x = -WIDTH; next_screen = "SETUP_PLAYERS"
                    elif btn_tutorial.is_clicked(mouse_pos, screen_offset_x) or btn_texas.is_clicked(mouse_pos, screen_offset_x) or btn_holdem.is_clicked(mouse_pos, screen_offset_x):
                        current_screen = "TUTORIAL"

                # --- Tutorial Screen (TUTORIAL) Logic ---
                elif current_screen == "TUTORIAL":
                    if btn_back_tut.is_clicked(mouse_pos):
                        target_offset_x = 0; next_screen = "MENU" # Slide back to MENU

                # --- Player Select Screen (SETUP_PLAYERS) Logic ---
                # Check for buttons only when the vertical view is centered (setup_offset_y == 0)
                elif current_screen == "SETUP_PLAYERS" and setup_offset_y == 0: 
                    for b in setup_btns:
                        # Pass the current offset for the Player Select buttons
                        if b.is_clicked(mouse_pos, screen_offset_x, setup_offset_y):
                            num_players_to_setup = b.action_code
                            setup_names_list = []
                            name_input.text = ""
                            name_error_message = ""
                            # Trigger the vertical slide up
                            target_setup_offset_y = -HEIGHT 
                            # FIX: Set the screen state immediately so the input handler is checked once the slide is done
                            current_screen = "SETUP_NAMES" # <--- This enables input handling
                            break
                
                # --- Name Input Screen (SETUP_NAMES) SUBMISSION Logic ---
                # Submission happens either on the Confirm button click OR on Enter key press
                elif current_screen == "SETUP_NAMES" and setup_offset_y == -HEIGHT:
                    # Check button click with offset
                    name_element_offset_y = setup_offset_y + HEIGHT # This is 0 when setup_offset_y is -HEIGHT
                    
                    # Calculate the button's final offset
                    button_offset_y = name_element_offset_y - 800
                    
                    # Check the Confirm button click
                    is_confirm_clicked = btn_next_name.is_clicked(mouse_pos, screen_offset_x, button_offset_y)
                    
                    # FIX: Process submission if button is clicked OR Enter key was pressed (trigger_name_submit)
                    if is_confirm_clicked or trigger_name_submit:
                        entered_name = name_input.text.strip()
                        # Name validation
                        if not entered_name:
                            name_error_message = "Name cannot be empty."
                            name_input.error_state = True
                        elif entered_name in setup_names_list:
                            name_error_message = "Name already taken."
                            name_input.error_state = True
                        else:
                            # Valid name submission
                            name_input.error_state = False
                            setup_names_list.append(entered_name)
                            name_input.text = ""
                            name_input.active = False
                            name_error_message = ""
                            
                            # Check if all names are entered
                            if len(setup_names_list) == num_players_to_setup:
                                # Finalize players and transition to GAME
                                human_money = load_bankroll()
                                human_money = max(human_money, STARTING_STACK) # Ensures at least STARTING_STACK
                                
                                # 1. Human player
                                p_name = setup_names_list[0]
                                is_bot = (game_mode == "SINGLE" and num_players_to_setup > 1)
                                if is_bot: # If single player mode, you are Player 1 (Human)
                                    players.append(Player(p_name, False, human_money, (WIDTH/2, HEIGHT - 100), 1))
                                else: # Multiplayer, first name is Human
                                    players.append(Player(p_name, False, STARTING_STACK, (WIDTH/2, HEIGHT - 100), 1))
                                
                                # 2. Add remaining players as bots/humans
                                for i, name in enumerate(setup_names_list[1:]):
                                    # In single player, all others are bots. In multiplayer, they are humans.
                                    is_bot = (game_mode == "SINGLE")
                                    # Calculate player position (i+1 since human is player 1)
                                    # Total players = num_players_to_setup
                                    # Number of other players = num_players_to_setup - 1
                                    other_count = num_players_to_setup - 1
                                    
                                    # Calculate angle for even spacing, starting from center-left of table
                                    angle_step = (2 * math.pi) / other_count
                                    angle = i * angle_step + math.pi / 2 # Start 90 degrees/up, and rotate clockwise
                                    
                                    # Adjust position calculation for a round table
                                    pos_x = WIDTH // 2 + 400 * math.cos(angle)
                                    pos_y = HEIGHT // 2 + 250 * math.sin(angle)
                                    
                                    # Finalize player position
                                    players.append(Player(name, is_bot, STARTING_STACK, (int(pos_x), int(pos_y)), i + 2))
                                
                                # Transition from Setup screen (at WIDTH) back to Game screen (at 0)
                                target_offset_x = 0
                                next_screen = "GAME"
                                
                            elif game_mode == "SINGLE" and len(setup_names_list) == 1 and num_players_to_setup > 1:
                                # For single player, skip name entry for bots
                                for i in range(1, num_players_to_setup):
                                    setup_names_list.append(f"Bot {i}")
                                # All names/bots set, initiate final slide
                                target_offset_x = 0
                                next_screen = "GAME"
                            
                # --- Game Screen (GAME) Logic ---
                elif current_screen == "GAME":
                    if waiting_for_next_player:
                        if btn_ready.is_clicked(mouse_pos):
                            waiting_for_next_player = False
                            continue

                    if btn_quit.is_clicked(mouse_pos):
                        if game_mode == "SINGLE": save_bankroll(players[0].money)
                        running = False
                    
                    if btn_cheat.is_clicked(mouse_pos):
                        show_cheat_sheet = True

                    if btn_deal.is_clicked(mouse_pos) and game_stage in ["IDLE", "SHOWDOWN"]:
                        # Reset and Deal
                        deck = [Card(r, s) for r in RANK_VALUES for s in SUIT_COLORS]
                        random.shuffle(deck)
                        community_cards = []
                        particles = []
                        pot = 0
                        active_count = 0
                        for p in players:
                            if p.money <= 0 and not p.eliminated:
                                p.eliminated = True
                            if not p.eliminated: active_count += 1
                            p.reset_round()
                            p.hand = [deck.pop(), deck.pop()]
                            for c in p.hand: c.is_face_up = True
                        
                        if active_count < 2:
                            game_stage = "IDLE"
                        else:
                            game_stage = "PREFLOP"
                            dealer_index = (dealer_index + 1) % len(players)
                            while players[dealer_index].eliminated: dealer_index = (dealer_index + 1) % len(players)
                            
                            # Post Blinds
                            sb_idx = (dealer_index + 1) % len(players)
                            while players[sb_idx].eliminated: sb_idx = (dealer_index + 1) % len(players)
                            
                            bb_idx = (sb_idx + 1) % len(players)
                            while players[bb_idx].eliminated: bb_idx = (bb_idx + 1) % len(players)
                            
                            # Small Blind
                            sb_bet = min(SMALL_BLIND, players[sb_idx].money)
                            players[sb_idx].money -= sb_bet
                            players[sb_idx].current_bet += sb_bet
                            players[sb_idx].last_action = "SB" if sb_bet == SMALL_BLIND else "All-In"
                            pot += sb_bet
                            if sb_bet < SMALL_BLIND: players[sb_idx].all_in = True
                            
                            # Big Blind
                            bb_bet = min(BIG_BLIND, players[bb_idx].money)
                            players[bb_idx].money -= bb_bet
                            players[bb_idx].current_bet += bb_bet
                            players[bb_idx].last_action = "BB" if bb_bet == BIG_BLIND else "All-In"
                            pot += bb_bet
                            if bb_bet < BIG_BLIND: players[bb_idx].all_in = True

                            # Set initial turn index
                            turn_index = (bb_idx + 1) % len(players)
                            while players[turn_index].eliminated: turn_index = (turn_index + 1) % len(players)
                            players_acted = 0
                            
                            if game_mode == "MULTI": waiting_for_next_player = True

                    # Player Actions (Only for Human player)
                    cur_p = players[turn_index]
                    if game_stage not in ["IDLE", "SHOWDOWN"] and not cur_p.is_bot and not waiting_for_next_player:
                        action_done = False
                        
                        if raising_mode:
                            # Raise Mode Buttons
                            if btn_cancel_raise.is_clicked(mouse_pos):
                                raising_mode = False
                            elif btn_confirm_raise.is_clicked(mouse_pos):
                                high_bet = max(p.current_bet for p in players if not p.eliminated)
                                bet_needed = pending_raise_amount - cur_p.current_bet
                                cur_p.money -= bet_needed
                                pot += bet_needed
                                cur_p.current_bet = pending_raise_amount
                                cur_p.last_action = "Raise"
                                if cur_p.money == 0: cur_p.all_in = True
                                action_done = True
                                
                            elif btn_r_plus.is_clicked(mouse_pos):
                                next_raise = pending_raise_amount + 10
                                if next_raise <= cur_p.money + cur_p.current_bet:
                                    pending_raise_amount = next_raise
                                elif next_raise > cur_p.money + cur_p.current_bet:
                                    pending_raise_amount = cur_p.money + cur_p.current_bet

                            elif btn_r_minus.is_clicked(mouse_pos):
                                high_bet = max(p.current_bet for p in players if not p.eliminated)
                                min_raise = high_bet + BIG_BLIND
                                if pending_raise_amount - 10 >= min_raise:
                                    pending_raise_amount -= 10
                                else:
                                    pending_raise_amount = min_raise
                        
                        else:
                            # Standard Action Buttons
                            if btn_fold.is_clicked(mouse_pos):
                                cur_p.folded = True
                                cur_p.last_action = "Fold"
                                action_done = True

                            elif btn_call.is_clicked(mouse_pos):
                                high_bet = max(p.current_bet for p in players if not p.eliminated)
                                diff = high_bet - cur_p.current_bet
                                
                                if cur_p.money >= diff:
                                    cur_p.money -= diff
                                    cur_p.current_bet += diff
                                    pot += diff
                                    cur_p.last_action = "Call" if diff > 0 else "Check"
                                else:
                                    # All-in
                                    cur_p.last_action = "All-In"
                                    cur_p.all_in = True
                                    pot += cur_p.money
                                    cur_p.current_bet += cur_p.money
                                    cur_p.money = 0
                                action_done = True
                                
                            elif btn_raise_start.is_clicked(mouse_pos):
                                high_bet = max(p.current_bet for p in players if not p.eliminated)
                                call_amt = high_bet - cur_p.current_bet
                                pending_raise_amount = call_amt + BIG_BLIND
                                
                                if pending_raise_amount > cur_p.money + cur_p.current_bet:
                                    pending_raise_amount = cur_p.money + cur_p.current_bet

                                raising_mode = True
                            
                            elif btn_peek.is_clicked(mouse_pos):
                                show_cards_toggled = not show_cards_toggled


                        if action_done:
                            # Advance Turn Logic
                            survivors = [p for p in players if not p.folded and not p.eliminated]
                            if len(survivors) == 1:
                                # Game Over -> Winner. Skip pass device.
                                waiting_for_next_player = False
                            else:
                                turn_index = (turn_index + 1) % len(players)
                                while players[turn_index].eliminated or players[turn_index].folded or players[turn_index].all_in:
                                    turn_index = (turn_index + 1) % len(players)
                                players_acted += 1
                                raising_mode = False
                                show_cards_toggled = False
                                
                                if game_mode == "MULTI": waiting_for_next_player = True


        # --- GAME STATE UPDATES (Bot Turns / Animation) ---
        
        # --- NEW: Setup Screen Transition Logic (Vertical) ---
        # Smoothly move the setup screen elements towards the target offset
        if abs(setup_offset_y - target_setup_offset_y) > 1:
            setup_offset_y += (target_setup_offset_y - setup_offset_y) * 0.15
        else:
            # FIX: Force the offset to the target position to ensure the strict check passes reliably
            setup_offset_y = target_setup_offset_y
        
        # Bot Turn Logic (Only in single-player mode)
        if current_screen == "GAME" and game_stage not in ["IDLE", "SHOWDOWN"] and not waiting_for_next_player:
            cur_p = players[turn_index]
            if cur_p.is_bot:
                bot_timer += dt
                if bot_timer > 0.5: # 0.5 second delay for bot action
                    high_bet = max(p.current_bet for p in players if not p.eliminated)
                    
                    bet_amt = cur_p.bot_action(high_bet, game_stage)
                    pot += bet_amt
                    
                    # Advance Turn Logic
                    survivors = [p for p in players if not p.folded and not p.eliminated]
                    if len(survivors) == 1:
                        # Game Over -> Winner. Skip pass device.
                        waiting_for_next_player = False
                    else:
                        turn_index = (turn_index + 1) % len(players)
                        while players[turn_index].eliminated or players[turn_index].folded or players[turn_index].all_in:
                            turn_index = (turn_index + 1) % len(players)
                        players_acted += 1
                        
                    bot_timer = 0 # Reset timer


        # --- GAME ROUND PROGRESSION LOGIC (End of street) ---
        if current_screen == "GAME" and game_stage not in ["IDLE", "SHOWDOWN"] and not waiting_for_next_player:
            
            # Check if all active players have matched the high bet
            active = [p for p in players if not p.folded and not p.eliminated and not p.all_in]
            not_folded = [p for p in players if not p.folded and not p.eliminated]
            high_bet = max(p.current_bet for p in players if not p.eliminated)
            
            # Everyone who hasn't folded or gone all-in must have matched the high bet
            all_matched = all(p.current_bet == high_bet or p.folded or p.all_in for p in not_folded)
            
            # Special case: Only one player left (everyone else folded)
            if len(not_folded) == 1:
                w = not_folded[0]
                w.money += pot
                pot = 0
                game_stage = "SHOWDOWN"
                particles.append(Particle(w.position[0], w.position[1], GOLD))
                
            # Normal street end: All bets matched and everyone has had a chance to act (players_acted >= count of not-folded)
            elif all_matched and players_acted >= len(not_folded):
                
                # Reset bets for the next street
                for p in players: p.current_bet = 0
                players_acted = 0
                
                # Set next dealer/turn index (Starts left of dealer, or first non-folded/non-eliminated)
                turn_index = (dealer_index + 1) % len(players)
                while players[turn_index].eliminated or players[turn_index].folded or players[turn_index].all_in:
                    turn_index = (turn_index + 1) % len(players)
                    # Safety break if we cycle back to the start
                    if turn_index == (dealer_index + 1) % len(players): break

                # Deal next street
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
                    
                # If there's only one player who can still bet, skip to showdown/next street immediately
                can_act = [p for p in not_folded if not p.all_in]
                if len(can_act) <= 1 and game_stage != "SHOWDOWN":
                    waiting_for_next_player = False
                    
                if game_stage != "SHOWDOWN" and game_mode == "MULTI":
                    waiting_for_next_player = True
        
        # --- SHOWDOWN LOGIC ---
        if current_screen == "GAME" and game_stage == "SHOWDOWN":
            not_folded = [p for p in players if not p.folded and not p.eliminated]
            
            if not not_folded: # Should not happen if game loop is correct
                pass
            else:
                best = -1
                winners = []
                for p in not_folded:
                    s = get_hand_score(p.hand + community_cards)
                    if s[0] > best:
                        best = s[0]
                        winners = [p]
                    elif s[0] == best:
                        winners.append(p)
                        
                # Split pot and distribute
                split = pot // len(winners)
                for w in winners:
                    w.money += split
                    particles.append(Particle(w.position[0], w.position[1], GOLD))
                
                pot = 0 # Remaining pot (if any due to division) is irrelevant for this simple implementation
                
                if game_mode == "MULTI": waiting_for_next_player = True
                
        # --- DRAWING ---
        SCREEN.fill(BG_COLOR)

        # --- DRAW MENU SCREEN (Always centered on the screen_offset_x viewport) ---
        # The entire menu scene is drawn relative to the screen_offset_x
        
        # --- LAYER 1: Background ---
        SCREEN.blit(ASSETS['TITLE_BG'], (0 + screen_offset_x, 0))
        
        # --- LAYER 2: Cards Image (Behind everything except BG) ---
        SCREEN.blit(ASSETS['TITLE_CARDS_LAYER'], (0 + screen_offset_x, 0))
        
        # --- LAYER 3: POKER Letters (Bobbing) ---
        start_x = 8 # X-position for the start of the 'P'
        y_base = 275 # Adjusted Y-position to move letters lower
        x_offset = 0
        for i, char in enumerate('POKER'):
            letter_surf = ASSETS['TITLE_LETTERS'][char]
            letter_offsets[char] = math.sin(bob_time + i * 0.5) * 5 # Max bob height of 5 pixels
            y_pos = y_base + letter_offsets[char]
            if char == 'O': y_pos += 120; x_offset -= 80
            if char == 'R': y_pos -= 20; x_offset += 20
            SCREEN.blit(letter_surf, (start_x + x_offset + screen_offset_x, y_pos))
            x_offset += letter_surf.get_width() - 40 # -25 for overlap

        # --- LAYER 4: Folder Image (Behind buttons/Texas/Holdem) ---
        folder_surf = ASSETS['TITLE_FOLDER'] # Positioned to frame the right-hand buttons
        folder_x = screen_offset_x
        folder_y = 0
        SCREEN.blit(folder_surf, (folder_x, folder_y))
        
        # --- LAYER 5: Main Buttons ---
        btn_single.draw(SCREEN, screen_offset_x)
        btn_multi.draw(SCREEN, screen_offset_x)
        btn_tutorial.draw(SCREEN, screen_offset_x)
        
        # --- LAYER 6: Texas/Hold-em Hoverable Titles ---
        # Repositioned to the upper-left, relative to the POKER title
        btn_texas.draw(SCREEN, screen_offset_x)
        btn_holdem.draw(SCREEN, screen_offset_x)

        if current_screen == "TUTORIAL":
            # Tutorial does not use the screen offset
            draw_overlay(SCREEN, "HOW TO PLAY", tutorial_lines)
            btn_back_tut.draw(SCREEN)

        # Setup screen logic has been merged and shifted by WIDTH
        if current_screen in ["SETUP_PLAYERS", "SETUP_NAMES"] or target_offset_x == -WIDTH:
            
            # --- DRAW PLAYER SELECT / NAME ENTRY VIEWPORT ---
            
            # The entire setup screen scene is drawn relative to the screen_offset_x
            setup_viewport_x = WIDTH + screen_offset_x # When screen_offset_x = -WIDTH, this is 0
            
            # --- Draw Background/Title for Player Select (Fixed elements in this viewport) ---
            SCREEN.blit(ASSETS['PS_BG'], (setup_viewport_x, 0))
            SCREEN.blit(ASSETS['PS_TITLE'], (setup_viewport_x + (WIDTH//2) - (ASSETS['PS_TITLE'].get_width() // 2), 100))
            
            # --- Draw Player Count Buttons (Offset by setup_offset_y) ---
            if setup_offset_y >= -HEIGHT: # Only draw the player select screen if it's visible or sliding
                for b in setup_btns:
                    b.draw(SCREEN, screen_offset_x, setup_offset_y)

            # --- Draw Name Input Elements (Offset by setup_offset_y + HEIGHT) ---
            # These elements are at 0 (on-screen) when setup_offset_y is -HEIGHT
            name_element_offset_y = setup_offset_y + HEIGHT 
            
            # 1. Name Input Title Image
            name_title_surf = ASSETS['PS_NAME_INPUT_TITLE']
            name_title_x = WIDTH + screen_offset_x + (WIDTH // 2) - (name_title_surf.get_width() // 2)
            SCREEN.blit(name_title_surf, (name_title_x, 80 + name_element_offset_y))

            # 2. "Player X of Y" Prompt Text
            if num_players_to_setup > 0:
                p_text = f"NAME FOR PLAYER {len(setup_names_list)+1} OF {num_players_to_setup}"
                t = FONT_LARGE.render(p_text, True, WHITE)
                text_x = WIDTH + screen_offset_x + (WIDTH//2 - t.get_width()//2)
                SCREEN.blit(t, (text_x, 280 + name_element_offset_y))

            # 3. Input Box
            # The y-coordinate passed to draw must be relative to the input box's rect
            name_input.draw(SCREEN, screen_offset_x, name_element_offset_y-800)

            # 4. Confirm Button
            btn_next_name.draw(SCREEN, screen_offset_x, name_element_offset_y-800)

            # 5. Error message (always drawn, but may be empty)
            if name_error_message:
                err_s = FONT_MED.render(name_error_message, True, RED)
                err_rect = err_s.get_rect(center=(WIDTH + screen_offset_x + WIDTH//2, name_input_y_start + 100 + name_element_offset_y - 800))
                SCREEN.blit(err_s, err_rect)
            
            # 6. List of Entered Names
            y_names = 650 + name_element_offset_y
            for i, name in enumerate(setup_names_list):
                n_s = FONT_MED.render(f"{i+1}. {name}", True, GOLD)
                SCREEN.blit(n_s, (WIDTH + screen_offset_x + 50, y_names))
                y_names += 30


        # --- DRAW GAME SCREEN (Always fixed at (0, 0)) ---
        if current_screen == "GAME" or target_offset_x == 0:
            # Draw game table and elements
            pygame.draw.circle(SCREEN, TABLE_RIM, (WIDTH//2, HEIGHT//2), 350)
            pygame.draw.circle(SCREEN, TABLE_FELT, (WIDTH//2, HEIGHT//2), 340)
            
            # Draw Community Cards (Center of the table)
            card_spacing = 100
            start_x = WIDTH//2 - (len(community_cards) * 80 + (len(community_cards)-1) * 20) // 2
            for i, card in enumerate(community_cards):
                card.draw(SCREEN, start_x + i * card_spacing, HEIGHT//2 - 60)
            
            # Draw Pot
            pot_s = FONT_LARGE.render(f"Pot: ${pot}", True, GOLD)
            SCREEN.blit(pot_s, (WIDTH//2 - pot_s.get_width()//2, HEIGHT//2 + 50))
            
            # Draw Player Info
            for i, p in enumerate(players):
                # Player Box
                px, py = p.position
                box_color = (60, 60, 60)
                if i == turn_index and game_stage not in ["IDLE", "SHOWDOWN"]:
                    box_color = (80, 80, 40) # Highlight active player
                
                # Draw Player Info Box
                pygame.draw.rect(SCREEN, box_color, (px, py, 150, 100), border_radius=5)
                pygame.draw.rect(SCREEN, WHITE, (px, py, 150, 100), 2, border_radius=5)
                
                # Name & Status
                name_s = FONT_MED.render(p.name, True, WHITE)
                name_rect = name_s.get_rect(center=(px+75, py + 15))
                
                if p.folded:
                    status_s = FONT_SMALL.render("FOLDED", True, RED)
                elif p.all_in:
                    status_s = FONT_SMALL.render("ALL-IN", True, GOLD)
                elif p.eliminated:
                    status_s = FONT_SMALL.render("OUT", True, (150, 150, 150))
                else:
                    status_s = FONT_SMALL.render(f"${p.money}", True, GOLD)
                
                status_rect = status_s.get_rect(center=(px+75, py + 40))
                
                # Current Bet
                bet_s = FONT_SMALL.render(f"Bet: ${p.current_bet}", True, WHITE)
                bet_rect = bet_s.get_rect(center=(px+75, py + 60))
                
                # Last Action
                action_s = FONT_SMALL.render(p.last_action, True, (0, 200, 255))
                action_rect = action_s.get_rect(center=(px+75, py + 80))
                
                SCREEN.blit(name_s, name_rect)
                SCREEN.blit(status_s, status_rect)
                SCREEN.blit(bet_s, bet_rect)
                SCREEN.blit(action_s, action_rect)

                # Draw Cards
                if p.hand:
                    scale = 0.7
                    card_width = 80 * scale
                    
                    show_hand = p.is_bot or (p.player_num == players[0].player_num and show_cards_toggled) or game_stage == "SHOWDOWN"

                    # Card 1
                    p.hand[0].draw(SCREEN, px + 5, py - 120, scale, force_hidden=not show_hand)
                    # Card 2
                    p.hand[1].draw(SCREEN, px + 5 + card_width + 5, py - 120, scale, force_hidden=not show_hand)
                
                # Draw Dealer/Blind Buttons
                if i == dealer_index:
                    d_s = FONT_SMALL.render("D", True, BLACK)
                    pygame.draw.circle(SCREEN, WHITE, (px - 10, py - 10), 10)
                    d_rect = d_s.get_rect(center=(px - 10, py - 10))
                    SCREEN.blit(d_s, d_rect)

            
            # --- Draw Game Action Buttons ---
            if waiting_for_next_player:
                btn_ready.draw(SCREEN)
            else:
                if game_stage in ["IDLE", "SHOWDOWN"]:
                    btn_deal.draw(SCREEN)
                else:
                    cur = players[turn_index]
                    if not cur.is_bot:
                        if raising_mode:
                            # Raise Box UI
                            pygame.draw.rect(SCREEN, (50, 50, 50), (800, 350, 400, 300), border_radius=5)
                            pygame.draw.rect(SCREEN, WHITE, (800, 350, 400, 300), 2, border_radius=5)
                            
                            amt_s = FONT_XL.render(f"${pending_raise_amount}", True, GOLD)
                            amt_rect = amt_s.get_rect(center=(990, 430))
                            SCREEN.blit(amt_s, amt_rect)
                           
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


            if show_cheat_sheet:
                draw_overlay(SCREEN, "HAND RANKINGS", cheat_lines)
                btn_close_cheat.draw(SCREEN)


        pygame.display.flip()
        clock.tick(60)


    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    # Create dummy folders for assets if they don't exist, to prevent crashing on load_assets
    for folder in ["Title", "Player Select", "Cards"]:
        if not os.path.exists(folder):
            try:
                os.makedirs(folder)
            except OSError as e:
                print(f"Error creating directory {folder}: {e}. Game may crash if assets are missing.")
                
    main()