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
        # Filename check based on user's mention of changes
        ASSETS['TITLE_BG'] = pygame.image.load(os.path.join("Title", "Title_BG.png")).convert_alpha()
        
        # NEW LAYERS for Title Screen (Using confirmed/expected names)
        ASSETS['TITLE_CARDS_LAYER'] = pygame.image.load(os.path.join("Title", "Title_Cards.png")).convert_alpha()
        ASSETS['TITLE_FOLDER'] = pygame.image.load(os.path.join("Title", "Title_Folder.png")).convert_alpha()
        ASSETS['TITLE_TEXAS'] = pygame.image.load(os.path.join("Title", "Title_Texas.png")).convert_alpha()
        ASSETS['TITLE_HOLDEM'] = pygame.image.load(os.path.join("Title", "Title_Holdem.png")).convert_alpha() # Corrected name
        
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
        

    def draw(self, surface, offset_x=0):
        # Adjust position based on viewport offset
        draw_rect = self.rect.move(offset_x, 0)
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


    def is_clicked(self, pos, offset_x=0):
        # Check collision against the viewport-adjusted rect
        adjusted_rect = self.rect.move(offset_x, 0)
        return adjusted_rect.collidepoint(pos)


class InputBox:
# InputBox Class remains the same
# ... (omitted for brevity)
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
    screen_offset_x = 0  # Current visual offset for the viewport
    target_offset_x = 0  # Where the viewport needs to slide to
    
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
    
    # Name Input and Next Name Button (These must also be offset by WIDTH)
    name_input = InputBox(base_x + 150, HEIGHT//2, 200, 50)
    # START: ADDED MISSING NEXT NAME BUTTON INITIALIZATION
    btn_next_name = Button("CONFIRM", base_x + 150, HEIGHT//2 + 80, 200, 50, GREEN_BTN, "next_name")
    # END: ADDED MISSING NEXT NAME BUTTON INITIALIZATION

    # --- GAME UI BUTTONS (Positioned at x=0) ---
    # ... (omitted game button initialization for brevity)

    # Tutorial Text
    tutorial_lines = [
    # ... (omitted tutorial lines for brevity)
    ]

    # Cheat Sheet
    cheat_lines = [
    # ... (omitted cheat lines for brevity)
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
            
            # START: MODIFIED INPUT BOX EVENT HANDLING (STATIC POSITION)
            if current_screen == "SETUP_NAMES":
                # The name input box is now treated as static relative to the screen for event checking.
                # Its original x is base_x + 150 (1650). Its static screen x is 1650 - 1200 = 450.
                STATIC_X = name_input.rect.x + target_offset_x # e.g. 1650 + (-1200) = 450
                
                original_x = name_input.rect.x
                name_input.rect.x = STATIC_X # Temporarily set to static screen position
                
                # Only allow activation/deactivation if transition is near complete
                if abs(screen_offset_x - target_offset_x) < 5: 
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if name_input.rect.collidepoint(event.pos):
                            name_input.active = not name_input.active
                        else:
                            name_input.active = False
                        name_input.color = WHITE if name_input.active else GRAY
                
                # If a key is pressed while active, handle input
                if name_input.active and event.type == pygame.KEYDOWN:
                    name_input.handle_event(event)
                    
                name_input.rect.x = original_x # Reset rect to its off-screen initialization position
            # END: MODIFIED INPUT BOX EVENT HANDLING

            # General Event Handling (Buttons)
            if current_screen == "MENU":
                if btn_single.is_clicked(mouse_pos):
                    game_mode = "SINGLE"
                    num_players_to_setup = 4 # Default to 4 players
                    target_offset_x = -WIDTH # Slide to player select screen
                    next_screen = "SETUP_PLAYERS" 
                elif btn_multi.is_clicked(mouse_pos):
                    game_mode = "MULTI"
                    target_offset_x = -WIDTH # Slide to player select screen
                    next_screen = "SETUP_PLAYERS"
                elif btn_tutorial.is_clicked(mouse_pos):
                    current_screen = "TUTORIAL"
            elif current_screen == "TUTORIAL":
                # Back button is assumed to be handled
                pass # Assuming a back button logic here
            elif current_screen == "SETUP_PLAYERS":
                for b in setup_btns:
                    # Pass the current offset for the Player Select buttons
                    if b.is_clicked(mouse_pos, screen_offset_x):
                        num_players_to_setup = b.action_code
                        setup_names_list = []
                        # The transition to SETUP_NAMES is a state change, not a slide, so target_offset_x remains -WIDTH
                        current_screen = "SETUP_NAMES"
                        name_input.text = ""
                        name_error_message = ""
            elif current_screen == "SETUP_NAMES":
                # Check button click with offset (MOVING BUTTON)
                if btn_next_name.is_clicked(mouse_pos, screen_offset_x):
                    raw_name = name_input.text.strip()
                    if not raw_name:
                        name_error_message = "Name cannot be empty!"
                        name_input.error_state = True
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
                            for i in range(num_players_to_setup):
                                angle = math.radians(90 + (360/num_players_to_setup)*i)
                                px = cx + rx * math.cos(angle) - 40
                                py = cy + ry * math.sin(angle) - 40
                                is_bot = (game_mode == "SINGLE" and i > 0)
                                p_name = setup_names_list[i]
                                players.append(Player(p_name, is_bot, STARTING_STACK, (int(px), int(py)), i+1))
                            # Transition from Setup screen (at WIDTH) back to Game screen (at 0)
                            target_offset_x = 0
                            next_screen = "GAME"
            # ... (omitted other screen/game state event handling for brevity)
            
            # Quitting/Cheat Sheet logic
            if current_screen == "GAME":
                # ... (omitted game UI button handling for brevity)
                pass # Assuming game buttons are here

        # --- TRANSITION LOGIC ---
        # Smoothly move the viewport towards the target position
        screen_offset_x += (target_offset_x - screen_offset_x) * 0.2
        
        # Lock the screen when the slide is complete
        if abs(target_offset_x - screen_offset_x) < 1:
            screen_offset_x = target_offset_x
            
        # Change screen state only when the slide animation is complete
        if current_screen != next_screen:
            current_screen = next_screen

        # Update POKER letter bobbing timer
        bob_time = pygame.time.get_ticks() / 300.0
        for i, char in enumerate('POKER'):
            # Use sine wave for bobbing
            letter_offsets[char] = math.sin(bob_time + i * 0.5) * 5 # Max bob height of 5 pixels
        
        # ... (omitted game logic for brevity)
            
        # --- DRAWING ---
        if current_screen == "MENU" or next_screen in ["SETUP_PLAYERS", "MENU"]:
            # --- MENU Screen (Positioned at x=0) ---
            # ... (omitted Menu screen drawing for brevity)
            
            # --- LAYER 5: Main Buttons ---
            btn_single.draw(SCREEN, screen_offset_x)
            btn_multi.draw(SCREEN, screen_offset_x)
            btn_tutorial.draw(SCREEN, screen_offset_x)
            
            # --- LAYER 6: Texas/Hold-em Hoverable Titles ---
            # ... (omitted Menu screen drawing for brevity)

        # --- PLAYER SELECT SCREEN DRAWING (When sliding or active) ---
        if current_screen == "SETUP_PLAYERS" or current_screen == "SETUP_NAMES" or next_screen == "SETUP_PLAYERS":
            # --- Draw BG/Title for Player Select (Moving) ---
            SCREEN.blit(ASSETS['PS_BG'], (WIDTH + screen_offset_x, 0))
            SCREEN.blit(ASSETS['PS_TITLE'], (WIDTH + screen_offset_x + 300, 50))
            
            # Draw Player Count Buttons (Moving)
            if current_screen == "SETUP_PLAYERS":
                for b in setup_btns:
                    b.draw(SCREEN, screen_offset_x)
                    
            elif current_screen == "SETUP_NAMES":
                # Draw name prompt text (Moving)
                t = FONT_LARGE.render(f"NAME FOR PLAYER {len(setup_names_list)+1}", True, GOLD)
                text_x = WIDTH + screen_offset_x + (WIDTH//2 - t.get_width()//2)
                SCREEN.blit(t, (text_x, 280))

                # START: MODIFIED INPUT BOX DRAWING (STATIC POSITION)
                # The input box is now drawn in a static position, regardless of screen_offset_x
                if screen_offset_x < 0: # Only draw the input box after the transition starts
                    # Static X position for drawing. (e.g., 1650 + (-1200) = 450)
                    STATIC_INPUT_X = name_input.rect.x + target_offset_x 
                    
                    original_x = name_input.rect.x
                    name_input.rect.x = STATIC_INPUT_X # Set to final screen position for drawing
                    name_input.draw(SCREEN)
                    name_input.rect.x = original_x # Reset the rect to its static position
                # END: MODIFIED INPUT BOX DRAWING

                # Draw moving Next Button (Keeps moving as requested)
                btn_next_name.draw(SCREEN, screen_offset_x)
                
                # Draw Error Message (Moving)
                if name_error_message:
                    err = FONT_SMALL.render(name_error_message, True, RED)
                    err_x = WIDTH + screen_offset_x + (WIDTH//2 - err.get_width()//2)
                    SCREEN.blit(err, (err_x, 520))
                
                # Draw player list (Moving)
                y = 570
                for i, n in enumerate(setup_names_list):
                    txt = FONT_SMALL.render(f"P{i+1}: {n}", True, GRAY) 
                    text_x = WIDTH + screen_offset_x + (WIDTH//2 - 200)
                    SCREEN.blit(txt, (text_x, y))
                    y += 25
                    
        # ... (omitted Game screen drawing for brevity)
        
        pygame.display.flip()
        clock.tick(60)


    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()