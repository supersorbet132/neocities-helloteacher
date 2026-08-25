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

class Particle:
# Particle Class remains the same
# ... (omitted for brevity)
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
           
            if current_screen == "SETUP_NAMES" and setup_offset_y == -HEIGHT:
            # Calculate the total offsets (screen X offset + setup Y offset relative to the name input rect)
            # The name input rect starts at Y=1250 (450 + HEIGHT). The draw offset is -800.
                total_offset_y = (setup_offset_y + HEIGHT) - HEIGHT # This simplifies to setup_offset_y (-800)
            
            # The name input draw call passes `name_element_offset_y-800` which is (setup_offset_y + HEIGHT) - 800.
            # Let's use that same calculation here for consistency with the existing draw logic.
                name_element_offset_y = setup_offset_y + HEIGHT
                offset_for_input = name_element_offset_y -800
            
            # Pass all events to the InputBox with the correct offsets
                entered_name = name_input.handle_event(event, screen_offset_x, offset_for_input)
            
            # If the user pressed ENTER (handled by handle_event), we run the submission logic.
                if entered_name is not None and event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                # Set a flag to trigger the name submission logic below
                    trigger_name_submit = True
                else:
                    trigger_name_submit = False
            # --- END Input Handling ---

            if event.type == pygame.MOUSEBUTTONDOWN:
                if show_cheat_sheet:
                    if btn_close_cheat.is_clicked(mouse_pos): show_cheat_sheet = False
                    continue


                if current_screen == "MENU" and target_offset_x == 0:
                    # Pass the current offset to check if the button was clicked in the visible area
                    if btn_single.is_clicked(mouse_pos, screen_offset_x):
                        game_mode = "SINGLE"; target_offset_x = -WIDTH; next_screen = "SETUP_PLAYERS" 
                    elif btn_multi.is_clicked(mouse_pos, screen_offset_x):
                        game_mode = "MULTI"; target_offset_x = -WIDTH; next_screen = "SETUP_PLAYERS" 
                    elif btn_tutorial.is_clicked(mouse_pos, screen_offset_x) or btn_texas.is_clicked(mouse_pos, screen_offset_x) or btn_holdem.is_clicked(mouse_pos, screen_offset_x):
                        current_screen = "TUTORIAL"


                elif current_screen == "TUTORIAL":
                    if btn_back_tut.is_clicked(mouse_pos): target_offset_x = 0; next_screen = "MENU" # Slide back to MENU


                # poker_test.py (around line 434)

# poker_test.py (around line 434)
                # Button clicking is only active when there is no pending vertical slide (setup_offset_y == 0)
                elif current_screen == "SETUP_PLAYERS": 
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
                            current_screen = "SETUP_NAMES" # <--- IMPORTANT: This state change enables the input loop later


                # --- Name Input Screen (SETUP_NAMES) MOUSEBUTTONDOWN Logic ---
                elif current_screen == "SETUP_NAMES":# and setup_offset_y == -HEIGHT: 
                # MOUSEBUTTONDOWN on the Confirm button or ENTER key press (from above) triggers submission
                    name_element_offset_y = setup_offset_y + HEIGHT # 0
                    print("hello")
                # Check the Confirm button click
                    is_confirm_clicked = btn_next_name.is_clicked(mouse_pos, screen_offset_x, name_element_offset_y)
                
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
                            # ... (existing finalization logic around line 489)
                            # (This code block is correct and will run if you have it)
                            
                            # Finalization logic from the file around line 493:
                            # 1. Human player
                                p_name = setup_names_list[0]
                                players.append(Player(p_name, False, human_money, (WIDTH/2, HEIGHT - 100), 1))
                            
                            # 2. Add remaining players as bots
                                for i, name in enumerate(setup_names_list[1:]):
                                    is_bot = (game_mode == "SINGLE")
                                # Calculate player position
                                    pos_x = WIDTH // 2 + 300 * math.cos(i * 2 * math.pi / (num_players_to_setup - 1) - math.pi / 2)
                                    pos_y = HEIGHT // 2 + 200 * math.sin(i * 2 * math.pi / (num_players_to_setup - 1) - math.pi / 2)
                                
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
        # --- NEW: Viewport Transition Logic (Horizontal) ---
        # Smoothly move the viewport towards the target offset (Lerping)
        if abs(screen_offset_x - target_offset_x) > 1:
            screen_offset_x += (target_offset_x - screen_offset_x) * 0.15
        else:
            screen_offset_x = target_offset_x
            # Change screen state only when the slide animation is complete
            if current_screen != next_screen:
                current_screen = next_screen 
        
        # poker_test.py (around line 506)
        
# poker_test.py (around line 506)
        # --- NEW: Setup Screen Transition Logic (Vertical) ---
        # Smoothly move the setup screen elements towards the target offset
        if abs(setup_offset_y - target_setup_offset_y) > 1:
            setup_offset_y += (target_setup_offset_y - setup_offset_y) * 0.15
        else:
            # FIX: Force final position to ensure the strict check (setup_offset_y == -HEIGHT) passes reliably
            setup_offset_y = target_setup_offset_y
        
        # The screen state change from SETUP_PLAYERS to SETUP_NAMES happens only when the button is clicked,
        # but the vertical offset is what determines which elements are visible/interactable.
        
        # Update POKER letter bobbing timer
        bob_time = pygame.time.get_ticks() / 300.0
        for i, char in enumerate('POKER'):
            # Use sine wave for bobbing
            letter_offsets[char] = math.sin(bob_time + i * 0.5) * 5 # Max bob height of 5 pixels
        
        
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
        if current_screen == "MENU" or next_screen in ["SETUP_PLAYERS", "MENU"]:
            # --- MENU Screen (Positioned at x=0) ---
            
            # --- LAYER 1: Background ---
            SCREEN.blit(ASSETS['TITLE_BG'], (0 + screen_offset_x, 0))
            
            # --- LAYER 2: Cards Image (Behind everything except BG) ---
            SCREEN.blit(ASSETS['TITLE_CARDS_LAYER'], (0 + screen_offset_x, 0))

            # --- LAYER 3: POKER Letters (Bobbing) ---
            start_x = 8 # X-position for the start of the 'P'
            y_base = 275 # Adjusted Y-position to move letters lower
            x_offset = 0
            
            for char in 'POKER':
                letter_surf = ASSETS['TITLE_LETTERS'][char]
                y_pos = y_base + letter_offsets[char]
                if char == 'O':
                    y_pos += 120
                    x_offset -= 80
                if char == 'R':
                    y_pos -= 20
                    x_offset += 20
                SCREEN.blit(letter_surf, (start_x + x_offset + screen_offset_x, y_pos))
                x_offset += letter_surf.get_width() - 40 # -25 for overlap
            
            # --- LAYER 4: Folder Image (Behind buttons/Texas/Holdem) ---
            folder_surf = ASSETS['TITLE_FOLDER']
            # Positioned to frame the right-hand buttons
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
        if current_screen in ["SETUP_PLAYERS", "SETUP_NAMES"] or next_screen in ["SETUP_PLAYERS", "GAME"]:
            # --- Draw Player Select Screen (Positioned at WIDTH) ---
            
            # 1. Draw Background (Offset by WIDTH)
            # The background remains fixed during the vertical slide
            SCREEN.blit(ASSETS['PS_BG'], (WIDTH + screen_offset_x, 0))
            
            # 2. Draw Title (Offset by WIDTH) - Title slides with the rest of the screen elements
            title_surf = ASSETS['PS_TITLE']
            title_x = WIDTH + screen_offset_x + (WIDTH // 2) - (title_surf.get_width() // 2)
            SCREEN.blit(title_surf, (title_x, 0 + setup_offset_y)) 
            
            # base_x is used for button/input positioning
            base_x = WIDTH + 300

            # --- Player Count Buttons (Slide Up) ---
            if current_screen == "SETUP_PLAYERS" or (current_screen == "MENU" and next_screen == "SETUP_PLAYERS"):
                # Draw player count buttons, offset by screen_offset_x AND setup_offset_y
                for b in setup_btns: b.draw(SCREEN, screen_offset_x, setup_offset_y)

            # --- Name Input Elements (Slide Up from Bottom) ---
            
            # Determine the offset for the Name Input elements.
            # If setup_offset_y is 0, these elements are at HEIGHT (off-screen bottom).
            # If setup_offset_y is -HEIGHT, these elements are at 0 (on-screen).
            name_element_offset_y = setup_offset_y + HEIGHT 
            
            # 1. Name Input Background Image
            #name_bg_surf = ASSETS['PS_NAME_INPUT_BG']
            #name_bg_x = WIDTH + screen_offset_x + (WIDTH // 2) - (name_bg_surf.get_width() // 2)
            #SCREEN.blit(name_bg_surf, (name_bg_x, 0 + name_element_offset_y))
            
            # 2. Name Input Title Image
            name_title_surf = ASSETS['PS_NAME_INPUT_TITLE']
            name_title_x = WIDTH + screen_offset_x + (WIDTH // 2) - (name_title_surf.get_width() // 2)
            SCREEN.blit(name_title_surf, (name_title_x, 80 + name_element_offset_y))
            
            # 3. "Player X of Y" Prompt Text
            #if num_players_to_setup > 0:
              #  p_text = f"NAME FOR PLAYER {len(setup_names_list)+1} OF {num_players_to_setup}"
             #   t = FONT_LARGE.render(p_text, True, WHITE)
            #    text_x = WIDTH + screen_offset_x + (WIDTH//2 - t.get_width()//2)
           #     SCREEN.blit(t, (text_x, 280 + name_element_offset_y)) 
            
            # 4. Input Box
            name_input.draw(SCREEN, screen_offset_x, name_element_offset_y-800)
            
            # 5. Confirm Button
            btn_next_name.draw(SCREEN, screen_offset_x, name_element_offset_y-800)
           
            # 6. Error Message
            if name_error_message:
                err = FONT_SMALL.render(name_error_message, True, RED)
                err_x = WIDTH + screen_offset_x + (WIDTH//2 - err.get_width()//2)
                SCREEN.blit(err, (err_x, 520 + name_element_offset_y)) 
           
            # 7. List of Entered Names
            y = name_element_offset_y
            names_x = WIDTH + screen_offset_x + (WIDTH//2 - 200)
            for i, n in enumerate(setup_names_list):
                txt = FONT_SMALL.render(f"P{i+1}: {n}", True, GRAY)
                SCREEN.blit(txt, (names_x, y))
                y += 25


        elif current_screen == "GAME":
            # --- GAME Screen (Positioned at x=0 once slide is complete) ---
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