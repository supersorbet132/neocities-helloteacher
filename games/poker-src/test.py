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

...
