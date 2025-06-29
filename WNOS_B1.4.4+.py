import pygame
import pygame.gfxdraw
import os
import sys
import math
import datetime
import calendar
import random
import webbrowser
import requests
import re
import psutil
import time
import subprocess
import json
import socket
import platform
import shutil
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
try:
    import GPUtil
except ImportError:
    GPUtil = None
from pygame.locals import *

# Initialize pygame
pygame.init()

# Get display resolution
display_info = pygame.display.Info()
DISPLAY_WIDTH, DISPLAY_HEIGHT = display_info.current_w, display_info.current_h

# Constants (initial values)
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 700
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (230, 230, 230)
DARK_GRAY = (50, 50, 50)
BLUE = (70, 130, 180)
LIGHT_BLUE = (100, 180, 255)
RED = (220, 60, 60)
GREEN = (60, 180, 75)
PURPLE = (150, 60, 200)
YELLOW = (210, 180, 60)
ORANGE = (255, 165, 0)
CYAN = (0, 200, 200)

# Create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("WNOS Desktop Environment")
clock = pygame.time.Clock()

# Fonts
font_large = pygame.font.SysFont("Arial", 36, bold=True)
font_medium = pygame.font.SysFont("Arial", 28)
font_small = pygame.font.SysFont("Arial", 22)
font_tiny = pygame.font.SysFont("Arial", 18)

# Dark mode gradient colors
DARK_GRADIENT_TOP = (30, 30, 50)
DARK_GRADIENT_BOTTOM = (10, 10, 20)
LIGHT_GRADIENT_TOP = (230, 240, 255)
LIGHT_GRADIENT_BOTTOM = (180, 200, 240)

# Server settings (simulated)
SERVER_URL = "http://localhost:5000"  # Replace with actual server URL in production
PUBLISHED_APPS_FILE = "published_apps.json"
INSTALLED_APPS_FILE = "installed_apps.json"

# Load published apps from file
def load_published_apps():
    try:
        if os.path.exists(PUBLISHED_APPS_FILE):
            with open(PUBLISHED_APPS_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return []

# Save published apps to file
def save_published_apps(apps):
    with open(PUBLISHED_APPS_FILE, 'w') as f:
        json.dump(apps, f)

# Load installed apps
def load_installed_apps():
    try:
        if os.path.exists(INSTALLED_APPS_FILE):
            with open(INSTALLED_APPS_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return []

# Save installed apps
def save_installed_apps(apps):
    with open(INSTALLED_APPS_FILE, 'w') as f:
        json.dump(apps, f)

# Initialize apps
published_apps = load_published_apps()
installed_apps = load_installed_apps()

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color=WHITE, radius=10):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.hovered = False
        self.radius = radius
        self.active = True
        self.clicked = False
        
    def draw(self, surface):
        if not self.active:
            return
            
        color = self.hover_color if self.hovered else self.color
        
        # Draw button with rounded corners
        pygame.draw.rect(surface, color, self.rect, border_radius=self.radius)
        pygame.draw.rect(surface, (30, 30, 30), self.rect, 2, border_radius=self.radius)
        
        # Draw text
        text_surf = font_small.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        if not self.active:
            return False
        self.hovered = self.rect.collidepoint(pos)
        return self.hovered
        
    def is_clicked(self, pos, event):
        if not self.active:
            return False
            
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(pos):
                self.clicked = True
                return True
        elif event.type == MOUSEBUTTONUP and event.button == 1:
            if self.clicked and self.rect.collidepoint(pos):
                self.clicked = False
                return True
            self.clicked = False
            
        return False

class Window:
    def __init__(self, title, width, height):
        self.title = title
        self.width = width
        self.height = height
        self.x = (SCREEN_WIDTH - width) // 2
        self.y = (SCREEN_HEIGHT - height) // 2
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.title_bar_height = 30
        self.active = True
        self.dark_mode = False
        self.title_bar_color = BLUE
        self.close_button = Button(
            self.x + self.width - 30,
            self.y + 5,
            20, 20, "X", RED, (255, 100, 100)
        )
        self.dragging = False
        self.last_action = None
        
    def draw(self, surface):
        if not self.active:
            return
            
        # Draw window shadow
        shadow_surf = pygame.Surface((self.width + 10, self.height + 10), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 100), (0, 0, self.width, self.height), 
                        border_radius=5)
        surface.blit(shadow_surf, (self.x - 5, self.y - 5))
        
        # Draw window background
        bg_color = DARK_GRAY if self.dark_mode else LIGHT_GRAY
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=5)
        
        # Draw title bar
        title_bar_rect = pygame.Rect(self.x, self.y, self.width, self.title_bar_height)
        pygame.draw.rect(surface, self.title_bar_color, title_bar_rect, border_top_left_radius=5, border_top_right_radius=5)
        
        # Draw title
        title_surf = font_small.render(self.title, True, WHITE)
        surface.blit(title_surf, (self.x + 10, self.y + 5))
        
        # Draw close button
        self.close_button.draw(surface)
        
    def handle_event(self, event, pos):
        if not self.active:
            return False
            
        # Update button position
        self.close_button.rect = pygame.Rect(
            self.x + self.width - 30,
            self.y + 5,
            20, 20
        )
        
        # Check if close button is clicked
        if self.close_button.is_clicked(pos, event):
            self.active = False
            return True
            
        # Check if title bar is being dragged
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            title_bar_rect = pygame.Rect(self.x, self.y, self.width, self.title_bar_height)
            if title_bar_rect.collidepoint(pos):
                self.dragging = True
                self.drag_offset_x = self.x - pos[0]
                self.drag_offset_y = self.y - pos[1]
                return True
                
        if event.type == MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
            
        if event.type == MOUSEMOTION and self.dragging:
            self.x = pos[0] + self.drag_offset_x
            self.y = pos[1] + self.drag_offset_y
            self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
            return True
            
        return False

class ResolutionWindow(Window):
    def __init__(self):
        super().__init__("Change Resolution", 400, 350)  # Increased height for custom option
        self.resolutions = [
            (DISPLAY_WIDTH, DISPLAY_HEIGHT),  # Display resolution
            (800, 600),
            (1024, 768),
            (1280, 720),
            (SCREEN_WIDTH, SCREEN_HEIGHT)  # Current resolution
        ]
        self.buttons = []
        
        # Create resolution buttons
        for i, res in enumerate(self.resolutions):
            label = f"{res[0]}x{res[1]}"
            if res == (DISPLAY_WIDTH, DISPLAY_HEIGHT):
                label = f"{res[0]}x{res[1]} (Display)"
            elif res == (SCREEN_WIDTH, SCREEN_HEIGHT):
                label = f"{res[0]}x{res[1]} (Current)"
                
            btn = Button(
                self.x + 50,
                self.y + 50 + i * 60,
                300, 50,
                label,
                BLUE, LIGHT_BLUE
            )
            self.buttons.append(btn)
            
        # Add custom resolution button
        self.custom_btn = Button(
            self.x + 50,
            self.y + 50 + len(self.resolutions) * 60,
            300, 50,
            "Custom Resolution",
            PURPLE, (180, 100, 220)
        )
        
    def draw(self, surface):
        super().draw(surface)
        if not self.active:
            return
            
        # Draw title
        title_surf = font_medium.render("Select Screen Resolution", True, WHITE if self.dark_mode else BLACK)
        surface.blit(title_surf, (self.x + 20, self.y + 20))
        
        # Draw current resolution indicator
        current_text = f"Current: {SCREEN_WIDTH}x{SCREEN_HEIGHT}"
        current_surf = font_small.render(current_text, True, YELLOW if self.dark_mode else BLUE)
        surface.blit(current_surf, (self.x + 20, self.y + self.height - 30))
        
        # Draw buttons
        for btn in self.buttons:
            btn.draw(surface)
        self.custom_btn.draw(surface)
            
    def handle_event(self, event, pos):
        if super().handle_event(event, pos):
            return True
            
        if not self.active:
            return False
            
        # Update button positions
        for i, btn in enumerate(self.buttons):
            btn.rect = pygame.Rect(
                self.x + 50,
                self.y + 50 + i * 60,
                300, 50
            )
        self.custom_btn.rect = pygame.Rect(
            self.x + 50,
            self.y + 50 + len(self.resolutions) * 60,
            300, 50
        )
        
        # Update button hover states
        for btn in self.buttons:
            btn.check_hover(pos)
        self.custom_btn.check_hover(pos)
            
        # Check button clicks
        for i, btn in enumerate(self.buttons):
            if btn.is_clicked(pos, event):
                self.last_action = self.resolutions[i]
                return True
                
        if self.custom_btn.is_clicked(pos, event):
            self.last_action = "custom"
            return True
                
        return False

class CustomResolutionWindow(Window):
    def __init__(self):
        super().__init__("Custom Resolution", 400, 250)
        self.width_input = ""
        self.height_input = ""
        self.active_input = "width"  # 'width' or 'height'
        self.error_message = ""
        
        # Create input labels
        self.width_label = "Width: "
        self.height_label = "Height: "
        
        # Create buttons
        self.ok_button = Button(
            self.x + 100, self.y + 180,
            80, 40, "OK", 
            GREEN, (100, 220, 100)
        )
        self.cancel_button = Button(
            self.x + 220, self.y + 180,
            80, 40, "Cancel", 
            RED, (255, 100, 100)
        )
        
    def draw(self, surface):
        super().draw(surface)
        if not self.active:
            return
            
        # Draw title
        title_surf = font_medium.render("Enter Custom Resolution", True, WHITE if self.dark_mode else BLACK)
        surface.blit(title_surf, (self.x + 20, self.y + 20))
        
        # Draw width input
        width_text = self.width_label + self.width_input
        width_color = LIGHT_BLUE if self.active_input == "width" else WHITE
        pygame.draw.rect(surface, width_color, (self.x + 50, self.y + 70, 300, 30))
        pygame.draw.rect(surface, (100, 100, 100), (self.x + 50, self.y + 70, 300, 30), 1)
        text_surf = font_small.render(width_text, True, BLACK)
        surface.blit(text_surf, (self.x + 55, self.y + 75))
        
        # Draw height input
        height_text = self.height_label + self.height_input
        height_color = LIGHT_BLUE if self.active_input == "height" else WHITE
        pygame.draw.rect(surface, height_color, (self.x + 50, self.y + 110, 300, 30))
        pygame.draw.rect(surface, (100, 100, 100), (self.x + 50, self.y + 110, 300, 30), 1)
        text_surf = font_small.render(height_text, True, BLACK)
        surface.blit(text_surf, (self.x + 55, self.y + 115))
        
        # Draw buttons
        self.ok_button.draw(surface)
        self.cancel_button.draw(surface)
        
        # Draw error message
        if self.error_message:
            error_surf = font_small.render(self.error_message, True, RED)
            surface.blit(error_surf, (self.x + 20, self.y + 150))
    
    def handle_event(self, event, pos):
        if super().handle_event(event, pos):
            return True
            
        if not self.active:
            return False
            
        # Update button positions
        self.ok_button.rect = pygame.Rect(self.x + 100, self.y + 180, 80, 40)
        self.cancel_button.rect = pygame.Rect(self.x + 220, self.y + 180, 80, 40)
        
        # Handle button clicks
        if self.ok_button.is_clicked(pos, event):
            if self.width_input and self.height_input:
                try:
                    width = int(self.width_input)
                    height = int(self.height_input)
                    
                    # Check if resolution is too big
                    if width > DISPLAY_WIDTH or height > DISPLAY_HEIGHT:
                        self.error_message = "Custom resolution is bigger than the display resolution."
                    elif width < 800 or height < 600:
                        self.error_message = "Resolution too small (min 800x600)."
                    else:
                        self.last_action = (width, height)
                        return True
                except ValueError:
                    self.error_message = "Please enter valid numbers."
            else:
                self.error_message = "Please enter both width and height."
                
        if self.cancel_button.is_clicked(pos, event):
            self.active = False
            return True
            
        # Handle input focus
        if event.type == MOUSEBUTTONDOWN:
            if self.x + 50 <= pos[0] <= self.x + 350 and self.y + 70 <= pos[1] <= self.y + 100:
                self.active_input = "width"
            elif self.x + 50 <= pos[0] <= self.x + 350 and self.y + 110 <= pos[1] <= self.y + 140:
                self.active_input = "height"
        
        # Handle keyboard input
        if event.type == KEYDOWN:
            if event.key == K_TAB:
                self.active_input = "height" if self.active_input == "width" else "width"
            elif event.key == K_RETURN:
                if self.width_input and self.height_input:
                    try:
                        width = int(self.width_input)
                        height = int(self.height_input)
                        if width > DISPLAY_WIDTH or height > DISPLAY_HEIGHT:
                            self.error_message = "Custom resolution is bigger than the display resolution."
                        elif width < 800 or height < 600:
                            self.error_message = "Resolution too small (min 800x600)."
                        else:
                            self.last_action = (width, height)
                            return True
                    except ValueError:
                        self.error_message = "Please enter valid numbers."
            elif event.key == K_BACKSPACE:
                if self.active_input == "width" and self.width_input:
                    self.width_input = self.width_input[:-1]
                elif self.active_input == "height" and self.height_input:
                    self.height_input = self.height_input[:-1]
            elif event.unicode.isdigit():
                if self.active_input == "width":
                    self.width_input += event.unicode
                else:
                    self.height_input += event.unicode
                    
        return False

class SnakeGameWindow(Window):
    def __init__(self):
        super().__init__("Snake Game", 600, 500)
        self.grid_size = 20
        self.cell_size = 20
        self.width = (self.width // self.grid_size) * self.grid_size
        self.height = (self.height // self.grid_size) * self.grid_size
        self.reset_game()
        
        # Create buttons
        self.restart_button = Button(
            self.x + 10, self.y + 10, 
            100, 30, "Restart", 
            BLUE, LIGHT_BLUE
        )
        
    def reset_game(self):
        self.snake = [(self.grid_size // 2, self.grid_size // 2)]
        self.direction = (1, 0)
        self.food = self.spawn_food()
        self.score = 0
        self.game_over = False
        self.speed = 10  # Frames per move
        self.frame_count = 0
        
    def spawn_food(self):
        while True:
            food = (random.randint(0, self.grid_size - 1), random.randint(0, self.grid_size - 1))
            if food not in self.snake:
                return food
                
    def draw(self, surface):
        super().draw(surface)
        if not self.active:
            return
            
        # Update button position
        self.restart_button.rect = pygame.Rect(self.x + 10, self.y + 10, 100, 30)
        self.restart_button.draw(surface)
        
        # Draw score
        score_text = f"Score: {self.score}"
        score_surf = font_small.render(score_text, True, WHITE if self.dark_mode else BLACK)
        surface.blit(score_surf, (self.x + self.width - 150, self.y + 15))
        
        # Draw game area
        game_rect = pygame.Rect(
            self.x + 10, 
            self.y + 50, 
            self.grid_size * self.cell_size,
            self.grid_size * self.cell_size
        )
        pygame.draw.rect(surface, (40, 40, 40), game_rect)
        pygame.draw.rect(surface, (100, 100, 100), game_rect, 2)
        
        # Draw snake
        for segment in self.snake:
            rect = pygame.Rect(
                self.x + 10 + segment[0] * self.cell_size,
                self.y + 50 + segment[1] * self.cell_size,
                self.cell_size, self.cell_size
            )
            pygame.draw.rect(surface, GREEN, rect)
            pygame.draw.rect(surface, (30, 100, 30), rect, 1)
            
        # Draw food
        food_rect = pygame.Rect(
            self.x + 10 + self.food[0] * self.cell_size,
            self.y + 50 + self.food[1] * self.cell_size,
            self.cell_size, self.cell_size
        )
        pygame.draw.rect(surface, RED, food_rect)
        pygame.draw.rect(surface, (150, 30, 30), food_rect, 1)
        
        # Draw game over message
        if self.game_over:
            game_over_surf = font_large.render("GAME OVER", True, RED)
            surface.blit(game_over_surf, (self.x + self.width // 2 - game_over_surf.get_width() // 2, 
                                         self.y + self.height // 2 - 50))
            
            restart_surf = font_medium.render("Press SPACE to restart", True, WHITE)
            surface.blit(restart_surf, (self.x + self.width // 2 - restart_surf.get_width() // 2, 
                                       self.y + self.height // 2 + 10))
    
    def handle_event(self, event, pos):
        if super().handle_event(event, pos):
            return True
            
        if not self.active:
            return False
            
        # Handle restart button
        if self.restart_button.is_clicked(pos, event):
            self.reset_game()
            return True
            
        if event.type == KEYDOWN:
            if self.game_over and event.key == K_SPACE:
                self.reset_game()
                return True
                
            if not self.game_over:
                if event.key == K_UP and self.direction != (0, 1):
                    self.direction = (0, -1)
                elif event.key == K_DOWN and self.direction != (0, -1):
                    self.direction = (0, 1)
                elif event.key == K_LEFT and self.direction != (1, 0):
                    self.direction = (-1, 0)
                elif event.key == K_RIGHT and self.direction != (-1, 0):
                    self.direction = (1, 0)
                    
        return False
        
    def update(self, dt):
        if self.game_over or not self.active:
            return
            
        self.frame_count += 1
        if self.frame_count >= self.speed:
            self.frame_count = 0
            self.move_snake()
            
    def move_snake(self):
        head_x, head_y = self.snake[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])
        
        # Check for collision with walls or self
        if (new_head[0] < 0 or new_head[0] >= self.grid_size or 
            new_head[1] < 0 or new_head[1] >= self.grid_size or 
            new_head in self.snake):
            self.game_over = True
            return
            
        self.snake.insert(0, new_head)
        
        # Check for food collision
        if new_head == self.food:
            self.score += 1
            self.food = self.spawn_food()
            # Speed up slightly every 5 points
            if self.score % 5 == 0 and self.speed > 5:
                self.speed -= 1
        else:
            self.snake.pop()

class TicTacToeWindow(Window):
    def __init__(self):
        super().__init__("Tic-Tac-Toe", 400, 450)
        self.reset_game()
        
        # Create buttons
        self.restart_button = Button(
            self.x + 10, self.y + 10, 
            100, 30, "Restart", 
            BLUE, LIGHT_BLUE
        )
        
    def reset_game(self):
        self.board = [['' for _ in range(3)] for _ in range(3)]
        self.current_player = 'X'
        self.game_over = False
        self.winner = None
        
    def draw(self, surface):
        super().draw(surface)
        if not self.active:
            return
            
        # Update button position
        self.restart_button.rect = pygame.Rect(self.x + 10, self.y + 10, 100, 30)
        self.restart_button.draw(surface)
        
        # Draw current player
        player_text = f"Player: {self.current_player}"
        player_color = RED if self.current_player == 'X' else BLUE
        player_surf = font_small.render(player_text, True, player_color)
        surface.blit(player_surf, (self.x + self.width - 150, self.y + 15))
        
        # Draw game board
        board_size = 300
        board_x = self.x + (self.width - board_size) // 2
        board_y = self.y + 70
        
        # Draw board background
        pygame.draw.rect(surface, (50, 50, 70), (board_x, board_y, board_size, board_size))
        
        # Draw grid lines
        cell_size = board_size // 3
        for i in range(1, 3):
            # Vertical lines
            pygame.draw.line(surface, WHITE, 
                           (board_x + i * cell_size, board_y),
                           (board_x + i * cell_size, board_y + board_size), 4)
            # Horizontal lines
            pygame.draw.line(surface, WHITE, 
                           (board_x, board_y + i * cell_size),
                           (board_x + board_size, board_y + i * cell_size), 4)
        
        # Draw X's and O's
        for row in range(3):
            for col in range(3):
                cell_x = board_x + col * cell_size + cell_size // 2
                cell_y = board_y + row * cell_size + cell_size // 2
                
                if self.board[row][col] == 'X':
                    # Draw X
                    offset = cell_size // 3
                    pygame.draw.line(surface, RED, 
                                   (cell_x - offset, cell_y - offset),
                                   (cell_x + offset, cell_y + offset), 8)
                    pygame.draw.line(surface, RED, 
                                   (cell_x + offset, cell_y - offset),
                                   (cell_x - offset, cell_y + offset), 8)
                elif self.board[row][col] == 'O':
                    # Draw O
                    pygame.draw.circle(surface, BLUE, (cell_x, cell_y), cell_size // 3, 8)
        
        # Draw game over message
        if self.game_over:
            if self.winner:
                winner_text = f"Player {self.winner} wins!"
                winner_color = RED if self.winner == 'X' else BLUE
            else:
                winner_text = "It's a tie!"
                winner_color = YELLOW
                
            game_over_surf = font_large.render(winner_text, True, winner_color)
            surface.blit(game_over_surf, (self.x + self.width // 2 - game_over_surf.get_width() // 2, 
                                         self.y + self.height - 70))
            
            restart_surf = font_medium.render("Press SPACE to restart", True, WHITE)
            surface.blit(restart_surf, (self.x + self.width // 2 - restart_surf.get_width() // 2, 
                                       self.y + self.height - 30))
    
    def handle_event(self, event, pos):
        if super().handle_event(event, pos):
            return True
            
        if not self.active:
            return False
            
        # Handle restart button
        if self.restart_button.is_clicked(pos, event):
            self.reset_game()
            return True
            
        if event.type == KEYDOWN and self.game_over and event.key == K_SPACE:
            self.reset_game()
            return True
            
        if not self.game_over and event.type == MOUSEBUTTONDOWN:
            board_size = 300
            board_x = self.x + (self.width - board_size) // 2
            board_y = self.y + 70
            cell_size = board_size // 3
            
            # Check if click is inside board
            if (board_x <= pos[0] <= board_x + board_size and 
                board_y <= pos[1] <= board_y + board_size):
                col = (pos[0] - board_x) // cell_size
                row = (pos[1] - board_y) // cell_size
                
                # Check if cell is empty
                if self.board[row][col] == '':
                    self.board[row][col] = self.current_player
                    
                    # Check for win
                    if self.check_win(self.current_player):
                        self.game_over = True
                        self.winner = self.current_player
                    # Check for tie
                    elif self.is_board_full():
                        self.game_over = True
                        self.winner = None
                    else:
                        # Switch player
                        self.current_player = 'O' if self.current_player == 'X' else 'X'
                    
                    return True
                    
        return False
        
    def check_win(self, player):
        # Check rows
        for row in self.board:
            if row[0] == row[1] == row[2] == player:
                return True
                
        # Check columns
        for col in range(3):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] == player:
                return True
                
        # Check diagonals
        if self.board[0][0] == self.board[1][1] == self.board[2][2] == player:
            return True
        if self.board[0][2] == self.board[1][1] == self.board[2][0] == player:
            return True
            
        return False
        
    def is_board_full(self):
        for row in self.board:
            for cell in row:
                if cell == '':
                    return False
        return True

class CalendarWindow(Window):
    def __init__(self):
        super().__init__("Calendar", 700, 500)
        self.today = datetime.date.today()
        self.current_month = self.today.month
        self.current_year = self.today.year
        self.month_names = ["January", "February", "March", "April", "May", "June",
                          "July", "August", "September", "October", "November", "December"]
        self.day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        self.cell_size = 50
        self.calendar_width = self.cell_size * 7
        self.calendar_height = self.cell_size * 7
        self.calendar_x = self.x + (self.width - self.calendar_width) // 2
        self.calendar_y = self.y + 80
        
        # Create navigation buttons
        button_width = 100
        button_height = 40
        self.prev_button = Button(
            self.calendar_x, 
            self.calendar_y - 50, 
            button_width, 
            button_height, 
            "< Prev", 
            BLUE, 
            LIGHT_BLUE
        )
        
        self.next_button = Button(
            self.calendar_x + self.calendar_width - button_width, 
            self.calendar_y - 50, 
            button_width, 
            button_height, 
            "Next >", 
            BLUE, 
            LIGHT_BLUE
        )
        
    def draw(self, surface):
        super().draw(surface)
        if not self.active:
            return
            
        # Update button positions
        self.prev_button.rect = pygame.Rect(
            self.calendar_x, 
            self.calendar_y - 50, 
            100, 40
        )
        
        self.next_button.rect = pygame.Rect(
            self.calendar_x + self.calendar_width - 100, 
            self.calendar_y - 50, 
            100, 40
        )
            
        # Draw month and year header
        month_text = f"{self.month_names[self.current_month - 1]} {self.current_year}"
        month_surf = font_medium.render(month_text, True, WHITE if self.dark_mode else BLACK)
        month_rect = month_surf.get_rect(center=(self.x + self.width // 2, self.y + 50))
        surface.blit(month_surf, month_rect)
        
        # Draw navigation buttons
        self.prev_button.draw(surface)
        self.next_button.draw(surface)
        
        # Draw day names header
        for i, day in enumerate(self.day_names):
            x = self.calendar_x + i * self.cell_size
            y = self.calendar_y
            pygame.draw.rect(surface, BLUE, (x, y, self.cell_size, self.cell_size))
            day_surf = font_tiny.render(day, True, WHITE)
            day_rect = day_surf.get_rect(center=(x + self.cell_size // 2, y + self.cell_size // 2))
            surface.blit(day_surf, day_rect)
        
        # Get calendar data
        cal = calendar.monthcalendar(self.current_year, self.current_month)
        
        # Draw calendar cells
        for week_idx, week in enumerate(cal):
            for day_idx, day in enumerate(week):
                if day == 0:
                    continue
                    
                x = self.calendar_x + day_idx * self.cell_size
                y = self.calendar_y + (week_idx + 1) * self.cell_size
                
                # Highlight today
                is_today = (day == self.today.day and 
                           self.current_month == self.today.month and 
                           self.current_year == self.today.year)
                
                cell_color = LIGHT_BLUE if is_today else (LIGHT_GRAY if not self.dark_mode else DARK_GRAY)
                pygame.draw.rect(surface, cell_color, (x, y, self.cell_size, self.cell_size))
                pygame.draw.rect(surface, (100, 100, 100), (x, y, self.cell_size, self.cell_size), 1)
                
                # Draw day number
                day_surf = font_small.render(str(day), True, BLACK if not self.dark_mode else WHITE)
                day_rect = day_surf.get_rect(center=(x + self.cell_size // 2, y + self.cell_size // 2))
                surface.blit(day_surf, day_rect)
    
    def navigate_month(self, direction):
        self.current_month += direction
        if self.current_month > 12:
            self.current_month = 1
            self.current_year += 1
        elif self.current_month < 1:
            self.current_month = 12
            self.current_year -= 1
            
    def handle_event(self, event, pos):
        if super().handle_event(event, pos):
            return True
            
        if not self.active:
            return False
            
        # Update button hover states
        self.prev_button.check_hover(pos)
        self.next_button.check_hover(pos)
            
        if self.prev_button.is_clicked(pos, event):
            self.navigate_month(-1)
            return True
            
        if self.next_button.is_clicked(pos, event):
            self.navigate_month(1)
            return True
            
        return False

class TerminalWindow(Window):
    def __init__(self):
        super().__init__("Terminal", 600, 400)
        self.command_history = []
        self.current_command = ""
        self.output_lines = ["Welcome to WNOS Terminal", "Type '@help' for available commands"]
        self.cursor_visible = True
        self.cursor_timer = 0
        self.font = pygame.font.SysFont("Courier New", 18)
        self.prompt = "> "
        
    def draw(self, surface):
        super().draw(surface)
        if not self.active:
            return
            
        # Draw output area
        output_y = self.y + 50
        max_lines = 15
        visible_lines = self.output_lines[-max_lines:]
        
        for i, line in enumerate(visible_lines):
            text_surf = self.font.render(line, True, WHITE if self.dark_mode else BLACK)
            surface.blit(text_surf, (self.x + 20, output_y + i * 25))
        
        # Draw input area
        input_y = output_y + len(visible_lines) * 25 + 10
        pygame.draw.line(surface, BLUE, (self.x + 20, input_y + 20), 
                        (self.x + self.width - 20, input_y + 20), 2)
        
        # Draw command with cursor
        cmd_text = self.prompt + self.current_command
        cmd_surf = self.font.render(cmd_text, True, WHITE if self.dark_mode else BLACK)
        surface.blit(cmd_surf, (self.x + 20, input_y))
        
        # Draw cursor
        if self.cursor_visible:
            cursor_x = self.x + 20 + self.font.size(cmd_text)[0]
            pygame.draw.line(surface, WHITE if self.dark_mode else BLACK, 
                           (cursor_x, input_y), (cursor_x, input_y + 20), 2)
    
    def handle_event(self, event, pos):
        if super().handle_event(event, pos):
            return True
            
        if not self.active:
            return False
            
        if event.type == KEYDOWN:
            if event.key == K_RETURN:
                self.execute_command(self.current_command)
                self.current_command = ""
            elif event.key == K_BACKSPACE:
                if self.current_command:
                    self.current_command = self.current_command[:-1]
            elif event.key == K_UP:
                if self.command_history:
                    self.current_command = self.command_history[-1]
            elif event.key == K_DOWN:
                self.current_command = ""
            else:
                self.current_command += event.unicode
            return True
            
        return False
        
    def execute_command(self, command):
        self.command_history.append(command)
        self.output_lines.append(f"{self.prompt}{command}")
        
        if command == "@help":
            self.output_lines.extend([
                "Available commands:",
                "@help - Show this help",
                "@date - Show current date",
                "@time - Show current time",
                "@calc <expression> - Calculate expression",
                "@clear - Clear terminal",
                "@exit - Close terminal",
                "@ip - Show IP address",
                "@sysinfo - Show system information",
                "@ls [dir] - List directory contents",
                "@mkdir <name> - Create directory",
                "@rm <file> - Remove file",
                "@rmdir <dir> - Remove directory",
                "@echo <text> - Print text",
                "@open <url> - Open URL in browser",
                "@weather <city> - Get weather for city"
            ])
        elif command == "@date":
            today = datetime.date.today()
            self.output_lines.append(today.strftime("%Y-%m-%d"))
        elif command == "@time":
            now = datetime.datetime.now()
            self.output_lines.append(now.strftime("%H:%M:%S"))
        elif command.startswith("@calc "):
            try:
                expr = command[6:]
                result = eval(expr)
                self.output_lines.append(str(result))
            except Exception as e:
                self.output_lines.append(f"Error: {str(e)}")
        elif command == "@clear":
            self.output_lines = []
        elif command == "@exit":
            self.active = False
        elif command == "@ip":
            try:
                hostname = socket.gethostname()
                ip_address = socket.gethostbyname(hostname)
                self.output_lines.append(f"IP Address: {ip_address}")
            except:
                self.output_lines.append("Could not retrieve IP address")
        elif command == "@sysinfo":
            self.output_lines.append(f"System: {platform.system()} {platform.release()}")
            self.output_lines.append(f"Processor: {platform.processor()}")
            self.output_lines.append(f"Python: {platform.python_version()}")
        elif command.startswith("@ls"):
            path = os.getcwd()
            if len(command.split()) > 1:
                path = command.split()[1]
                
            try:
                contents = os.listdir(path)
                self.output_lines.append(f"Directory: {path}")
                for item in contents:
                    self.output_lines.append(f" - {item}")
            except Exception as e:
                self.output_lines.append(f"Error: {str(e)}")
        elif command.startswith("@mkdir "):
            try:
                dirname = command[7:]
                os.mkdir(dirname)
                self.output_lines.append(f"Created directory: {dirname}")
            except Exception as e:
                self.output_lines.append(f"Error: {str(e)}")
        elif command.startswith("@rm "):
            try:
                filename = command[4:]
                os.remove(filename)
                self.output_lines.append(f"Removed file: {filename}")
            except Exception as e:
                self.output_lines.append(f"Error: {str(e)}")
        elif command.startswith("@rmdir "):
            try:
                dirname = command[7:]
                shutil.rmtree(dirname)
                self.output_lines.append(f"Removed directory: {dirname}")
            except Exception as e:
                self.output_lines.append(f"Error: {str(e)}")
        elif command.startswith("@echo "):
            text = command[6:]
            self.output_lines.append(text)
        elif command.startswith("@open "):
            try:
                url = command[6:]
                webbrowser.open(url)
                self.output_lines.append(f"Opening: {url}")
            except Exception as e:
                self.output_lines.append(f"Error: {str(e)}")
        elif command.startswith("@weather "):
            city = command[9:]
            self.output_lines.append(f"Weather for {city}: Not implemented yet")
        else:
            self.output_lines.append(f"Unknown command: {command}")
    
    def update(self, dt):
        self.cursor_timer += dt
        if self.cursor_timer > 0.5:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

class SettingsWindow(Window):
    def __init__(self):
        super().__init__("System Settings", 600, 550)  # Increased height
        self.wallpapers = [
            "Gradient", "Sticky Notes", "Project Notes", 
            "Graph Paper", "Nature", "Solid Color"
        ]
        self.themes = ["Light", "Dark"]
        self.buttons = []
        
        # Create wallpaper buttons
        for i, wallpaper in enumerate(self.wallpapers):
            btn = Button(
                self.x + 50 + (i % 2) * 250,
                self.y + 80 + (i // 2) * 60,
                230, 50, wallpaper, 
                BLUE, LIGHT_BLUE
            )
            self.buttons.append(btn)
        
        # Create theme buttons
        for i, theme in enumerate(self.themes):
            btn = Button(
                self.x + 50 + i * 250,
                self.y + 280,
                230, 50, theme, 
                PURPLE, (180, 100, 220)
            )
            self.buttons.append(btn)
        
        # Create system info button
        self.sysinfo_btn = Button(
            self.x + 50, self.y + 350, 
            230, 50, "System Info", 
            GREEN, (100, 220, 100)
        )
        self.buttons.append(self.sysinfo_btn)
        
        # Create disk cleanup button
        self.disk_btn = Button(
            self.x + 50 + 250, self.y + 350, 
            230, 50, "Disk Cleanup", 
            ORANGE, (255, 200, 100)
        )
        self.buttons.append(self.disk_btn)
        
        # Create resolution change button
        self.resolution_btn = Button(
            self.x + 50, self.y + 420, 
            230, 50, "Change Resolution", 
            CYAN, (100, 220, 220)
        )
        self.buttons.append(self.resolution_btn)
        
    def draw(self, surface):
        super().draw(surface)
        if not self.active:
            return
            
        # Update button positions
        for i, btn in enumerate(self.buttons):
            if i < len(self.wallpapers):
                btn.rect = pygame.Rect(
                    self.x + 50 + (i % 2) * 250,
                    self.y + 80 + (i // 2) * 60,
                    230, 50
                )
            elif i < len(self.wallpapers) + len(self.themes):
                theme_idx = i - len(self.wallpapers)
                btn.rect = pygame.Rect(
                    self.x + 50 + theme_idx * 250,
                    self.y + 280,
                    230, 50
                )
            elif btn == self.sysinfo_btn:
                btn.rect = pygame.Rect(
                    self.x + 50, 
                    self.y + 350, 
                    230, 50
                )
            elif btn == self.disk_btn:
                btn.rect = pygame.Rect(
                    self.x + 50 + 250, 
                    self.y + 350, 
                    230, 50
                )
            elif btn == self.resolution_btn:
                btn.rect = pygame.Rect(
                    self.x + 50, 
                    self.y + 420, 
                    230, 50
                )
        
        # Draw section headers
        title_surf = font_medium.render("Wallpaper Settings", True, WHITE if self.dark_mode else BLACK)
        surface.blit(title_surf, (self.x + 50, self.y + 50))
        
        title_surf = font_medium.render("Theme Settings", True, WHITE if self.dark_mode else BLACK)
        surface.blit(title_surf, (self.x + 50, self.y + 250))
        
        title_surf = font_medium.render("System Tools", True, WHITE if self.dark_mode else BLACK)
        surface.blit(title_surf, (self.x + 50, self.y + 320))
        
        title_surf = font_medium.render("Display Settings", True, WHITE if self.dark_mode else BLACK)
        surface.blit(title_surf, (self.x + 50, self.y + 390))
        
        # Draw buttons
        for btn in self.buttons:
            btn.draw(surface)
    
    def handle_event(self, event, pos):
        if super().handle_event(event, pos):
            return True
            
        if not self.active:
            return False
            
        # Update button positions (critical fix for interaction)
        for i, btn in enumerate(self.buttons):
            if i < len(self.wallpapers):
                btn.rect = pygame.Rect(
                    self.x + 50 + (i % 2) * 250,
                    self.y + 80 + (i // 2) * 60,
                    230, 50
                )
            elif i < len(self.wallpapers) + len(self.themes):
                theme_idx = i - len(self.wallpapers)
                btn.rect = pygame.Rect(
                    self.x + 50 + theme_idx * 250,
                    self.y + 280,
                    230, 50
                )
            elif btn == self.sysinfo_btn:
                btn.rect = pygame.Rect(
                    self.x + 50, 
                    self.y + 350, 
                    230, 50
                )
            elif btn == self.disk_btn:
                btn.rect = pygame.Rect(
                    self.x + 50 + 250, 
                    self.y + 350, 
                    230, 50
                )
            elif btn == self.resolution_btn:
                btn.rect = pygame.Rect(
                    self.x + 50, 
                    self.y + 420, 
                    230, 50
                )
        
        # Update button hover states
        for btn in self.buttons:
            btn.check_hover(pos)
            
        # Check button clicks
        for i, btn in enumerate(self.buttons):
            if btn.is_clicked(pos, event):
                if i < len(self.wallpapers):
                    self.last_action = ("wallpaper", self.wallpapers[i])
                    return True
                elif i < len(self.wallpapers) + len(self.themes):
                    self.last_action = ("theme", self.themes[i - len(self.wallpapers)])
                    return True
                elif btn == self.sysinfo_btn:
                    self.last_action = ("sysinfo",)
                    return True
                elif btn == self.disk_btn:
                    self.last_action = ("disk",)
                    return True
                elif btn == self.resolution_btn:
                    self.last_action = ("resolution",)
                    return True
        return False

class NotepadWindow(Window):
    def __init__(self):
        super().__init__("Notepad", 600, 500)
        self.text = ""
        self.font = pygame.font.SysFont("Arial", 18)
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_pos = 0
        self.scroll_offset = 0
        self.filename = ""
        self.text_area_width = self.width - 40
        
        # Create buttons
        self.save_button = Button(
            self.x + 10, self.y + 40, 
            80, 30, "Save", 
            GREEN, (100, 220, 100)
        )
        self.save_as_button = Button(
            self.x + 100, self.y + 40, 
            100, 30, "Save As", 
            BLUE, LIGHT_BLUE
        )
        self.open_button = Button(
            self.x + 210, self.y + 40, 
            80, 30, "Open", 
            PURPLE, (180, 100, 220)
        )
        
    def draw(self, surface):
        super().draw(surface)
        if not self.active:
            return
            
        # Update button positions
        self.save_button.rect = pygame.Rect(self.x + 10, self.y + 40, 80, 30)
        self.save_as_button.rect = pygame.Rect(self.x + 100, self.y + 40, 100, 30)
        self.open_button.rect = pygame.Rect(self.x + 210, self.y + 40, 80, 30)
        
        # Draw buttons
        self.save_button.draw(surface)
        self.save_as_button.draw(surface)
        self.open_button.draw(surface)
        
        # Draw text area
        text_area = pygame.Rect(self.x + 10, self.y + 80, self.width - 20, self.height - 90)
        pygame.draw.rect(surface, WHITE if not self.dark_mode else DARK_GRAY, text_area)
        pygame.draw.rect(surface, (100, 100, 100), text_area, 1)
        
        # Wrap text and draw
        wrapped_lines = self.wrap_text(self.text)
        y_offset = 10
        for i, line in enumerate(wrapped_lines):
            if i < self.scroll_offset:
                continue
            text_surf = self.font.render(line, True, BLACK if not self.dark_mode else WHITE)
            surface.blit(text_surf, (self.x + 20, self.y + 90 + (i - self.scroll_offset) * 25))
            if (i - self.scroll_offset) * 25 > text_area.height:
                break
            
        # Draw filename
        filename_text = f"File: {self.filename}" if self.filename else "New File"
        filename_surf = font_tiny.render(filename_text, True, WHITE if self.dark_mode else BLACK)
        surface.blit(filename_surf, (self.x + 300, self.y + 50))
        
        # Draw cursor - simplified for wrapped text
        if self.cursor_visible:
            # Find cursor position in wrapped lines
            cursor_line, cursor_x = self.get_cursor_position()
            cursor_y = self.y + 90 + (cursor_line - self.scroll_offset) * 25
            cursor_x_pos = self.x + 20 + self.font.size(self.text[:self.cursor_pos].split('\n')[-1])[0]
            pygame.draw.line(surface, BLACK if not self.dark_mode else WHITE, 
                           (cursor_x_pos, cursor_y), (cursor_x_pos, cursor_y + 20), 2)
    
    def wrap_text(self, text):
        """Wrap text to fit within the notepad width"""
        lines = text.split('\n')
        wrapped_lines = []
        max_width = self.width - 40
        
        for line in lines:
            current_line = ""
            for word in line.split(' '):
                test_line = current_line + word + " "
                # If the line is too long, wrap it
                if self.font.size(test_line)[0] > max_width and current_line:
                    wrapped_lines.append(current_line)
                    current_line = word + " "
                else:
                    current_line = test_line
            wrapped_lines.append(current_line.rstrip())
        
        return wrapped_lines
    
    def get_cursor_position(self):
        """Get cursor position in wrapped lines"""
        # Count lines before cursor
        lines_before_cursor = self.text[:self.cursor_pos].split('\n')
        line_num = len(lines_before_cursor) - 1
        
        # Find the wrapped line index
        wrapped_lines = self.wrap_text(self.text)
        current_index = 0
        for i, line in enumerate(wrapped_lines):
            current_index += len(line) + 1  # +1 for newline
            if current_index >= self.cursor_pos:
                return i, self.cursor_pos - (current_index - len(line) - 1)
                
        return len(wrapped_lines) - 1, len(wrapped_lines[-1])
    
    def handle_event(self, event, pos):
        if super().handle_event(event, pos):
            return True
            
        if not self.active:
            return False
            
        # Handle button clicks
        if self.save_button.is_clicked(pos, event):
            self.save_file()
            return True
        if self.save_as_button.is_clicked(pos, event):
            self.save_file_as()
            return True
        if self.open_button.is_clicked(pos, event):
            self.open_file()
            return True
            
        if event.type == KEYDOWN:
            if event.key == K_BACKSPACE:
                if self.cursor_pos > 0:
                    self.text = self.text[:self.cursor_pos-1] + self.text[self.cursor_pos:]
                    self.cursor_pos -= 1
            elif event.key == K_RETURN:
                self.text = self.text[:self.cursor_pos] + '\n' + self.text[self.cursor_pos:]
                self.cursor_pos += 1
            elif event.key == K_LEFT:
                if self.cursor_pos > 0:
                    self.cursor_pos -= 1
            elif event.key == K_RIGHT:
                if self.cursor_pos < len(self.text):
                    self.cursor_pos += 1
            elif event.key == K_UP:
                # Move cursor up one line (simplified)
                prev_newline = self.text.rfind('\n', 0, self.cursor_pos)
                if prev_newline != -1:
                    prev_prev_newline = self.text.rfind('\n', 0, prev_newline)
                    line_start = prev_prev_newline + 1 if prev_prev_newline != -1 else 0
                    line_pos = self.cursor_pos - line_start
                    
                    target_line_start = prev_prev_newline + 1 if prev_prev_newline != -1 else 0
                    target_line_end = self.text.find('\n', target_line_start)
                    if target_line_end == -1:
                        target_line_end = len(self.text)
                    
                    target_pos = min(target_line_start + min(line_pos, target_line_end - target_line_start), target_line_end)
                    self.cursor_pos = target_pos
            elif event.key == K_DOWN:
                # Move cursor down one line (simplified)
                next_newline = self.text.find('\n', self.cursor_pos)
                if next_newline != -1:
                    next_next_newline = self.text.find('\n', next_newline + 1)
                    if next_next_newline == -1:
                        next_next_newline = len(self.text)
                    
                    current_line_start = self.text.rfind('\n', 0, self.cursor_pos)
                    if current_line_start == -1:
                        current_line_start = 0
                    else:
                        current_line_start += 1
                    
                    line_pos = self.cursor_pos - current_line_start
                    target_pos = min(next_newline + 1 + min(line_pos, next_next_newline - (next_newline + 1)), next_next_newline)
                    self.cursor_pos = target_pos
            elif event.key == K_PAGEUP:
                self.scroll_offset = max(0, self.scroll_offset - 10)
            elif event.key == K_PAGEDOWN:
                self.scroll_offset = min(len(self.wrap_text(self.text)) - 1, self.scroll_offset + 10)
            else:
                self.text = self.text[:self.cursor_pos] + event.unicode + self.text[self.cursor_pos:]
                self.cursor_pos += len(event.unicode)
            return True
            
        return False
    
    def save_file(self):
        if self.filename:
            try:
                with open(self.filename, "w") as f:
                    f.write(self.text)
                return True
            except Exception as e:
                print(f"Error saving file: {e}")
                return False
        else:
            return self.save_file_as()
    
    def save_file_as(self):
        # In a real app, we'd use a file dialog, but for simplicity we'll use a fixed name
        self.filename = "note.txt"
        try:
            with open(self.filename, "w") as f:
                f.write(self.text)
            return True
        except Exception as e:
            print(f"Error saving file: {e}")
            return False
    
    def open_file(self):
        # In a real app, we'd use a file dialog, but for simplicity we'll try to open note.txt
        try:
            with open("note.txt", "r") as f:
                self.text = f.read()
            self.filename = "note.txt"
            self.cursor_pos = 0
            self.scroll_offset = 0
            return True
        except FileNotFoundError:
            print("File not found")
            return False
    
    def update(self, dt):
        self.cursor_timer += dt
        if self.cursor_timer > 0.5:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

class SystemInfoWindow(Window):
    def __init__(self):
        super().__init__("System Information", 500, 400)
        self.cpu_usage = 0
        self.ram_usage = 0
        self.disk_usage = 0
        self.gpu_usage = 0
        self.gpu_temp = 0
        self.update_timer = 0
        self.values = []
        self.close_button = Button(
            self.x + self.width - 30,
            self.y + 5,
            20, 20, "X", RED, (255, 100, 100)
        )
        
    def update_metrics(self):
        try:
            self.cpu_usage = psutil.cpu_percent(interval=0.1)
            
            ram = psutil.virtual_memory()
            self.ram_usage = ram.percent
            
            disk = psutil.disk_usage('/')
            self.disk_usage = disk.percent
            
            if GPUtil:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]
                    self.gpu_usage = gpu.load * 100
                    self.gpu_temp = gpu.temperature
                else:
                    self.gpu_usage = -1
            else:
                self.gpu_usage = -1
        except:
            pass
        
        # Store values for graph
        self.values.append(self.cpu_usage)
        if len(self.values) > 30:
            self.values.pop(0)
    
    def draw(self, surface):
        super().draw(surface)
        if not self.active:
            return
            
        # Update metrics every 2 seconds
        self.update_timer += clock.get_time()
        if self.update_timer > 2000:
            self.update_metrics()
            self.update_timer = 0
            
        # Draw metrics
        y_pos = self.y + 50
        metrics = [
            f"CPU Usage: {self.cpu_usage:.1f}%",
            f"RAM Usage: {self.ram_usage:.1f}%",
            f"Disk Usage: {self.disk_usage:.1f}%",
            f"GPU Usage: {self.gpu_usage:.1f}%" if self.gpu_usage >= 0 else "GPU: Not available",
            f"GPU Temp: {self.gpu_temp:.1f}°C" if self.gpu_usage >= 0 else ""
        ]
        
        for metric in metrics:
            if metric:
                text_surf = font_small.render(metric, True, WHITE if self.dark_mode else BLACK)
                surface.blit(text_surf, (self.x + 20, y_pos))
                y_pos += 40
        
        # Draw CPU usage graph
        graph_rect = pygame.Rect(self.x + 20, y_pos, self.width - 40, 150)
        pygame.draw.rect(surface, (40, 40, 40), graph_rect)
        pygame.draw.rect(surface, (100, 100, 100), graph_rect, 1)
        
        if self.values:
            points = []
            max_val = max(self.values) if max(self.values) > 0 else 100
            for i, val in enumerate(self.values):
                x = graph_rect.left + i * (graph_rect.width / len(self.values))
                y = graph_rect.bottom - (val / max_val) * graph_rect.height
                points.append((x, y))
            
            if len(points) > 1:
                pygame.draw.lines(surface, LIGHT_BLUE, False, points, 2)
        
        # Draw graph title
        text_surf = font_tiny.render("CPU Usage History", True, WHITE if self.dark_mode else BLACK)
        surface.blit(text_surf, (self.x + 20, y_pos - 20))

# ===== WNBrowser Window =====
class BrowserWindow(Window):
    def __init__(self):
        super().__init__("WNBrowser", 800, 600)
        self.url = "https://www.google.com"
        self.url_input = self.url
        self.search_input = ""
        self.active_input = "url"  # 'url' or 'search'
        self.cursor_visible = True
        self.cursor_timer = 0
        self.history = []
        self.current_history_index = -1
        self.loading = False
        self.loading_progress = 0
        
        # Create buttons
        self.go_button = Button(
            self.x + 10, self.y + 40,
            60, 30, "Go",
            GREEN, (100, 220, 100)
        )
        self.back_button = Button(
            self.x + 80, self.y + 40,
            60, 30, "Back",
            BLUE, LIGHT_BLUE
        )
        self.forward_button = Button(
            self.x + 150, self.y + 40,
            60, 30, "Forward",
            BLUE, LIGHT_BLUE
        )
        self.search_button = Button(
            self.x + self.width - 80, self.y + 40,
            60, 30, "Search",
            PURPLE, (180, 100, 220)
        )
        
    def draw(self, surface):
        super().draw(surface)
        if not self.active:
            return
            
        # Update button positions
        self.go_button.rect = pygame.Rect(self.x + 10, self.y + 40, 60, 30)
        self.back_button.rect = pygame.Rect(self.x + 80, self.y + 40, 60, 30)
        self.forward_button.rect = pygame.Rect(self.x + 150, self.y + 40, 60, 30)
        self.search_button.rect = pygame.Rect(self.x + self.width - 80, self.y + 40, 60, 30)
        
        # Draw buttons
        self.go_button.draw(surface)
        self.back_button.draw(surface)
        self.forward_button.draw(surface)
        self.search_button.draw(surface)
        
        # Draw URL input
        url_rect = pygame.Rect(self.x + 220, self.y + 40, self.width - 310, 30)
        pygame.draw.rect(surface, WHITE if not self.dark_mode else DARK_GRAY, url_rect)
        pygame.draw.rect(surface, (100, 100, 100), url_rect, 1)
        
        url_text = self.url_input
        url_surf = font_small.render(url_text, True, BLACK if not self.dark_mode else WHITE)
        surface.blit(url_surf, (self.x + 225, self.y + 45))
        
        # Draw search input
        search_rect = pygame.Rect(self.x + 10, self.y + 80, self.width - 20, 30)
        pygame.draw.rect(surface, WHITE if not self.dark_mode else DARK_GRAY, search_rect)
        pygame.draw.rect(surface, (100, 100, 100), search_rect, 1)
        
        search_text = self.search_input
        search_surf = font_small.render(search_text, True, BLACK if not self.dark_mode else WHITE)
        surface.blit(search_surf, (self.x + 15, self.y + 85))
        
        # Draw cursor
        if self.cursor_visible:
            if self.active_input == "url":
                cursor_x = self.x + 225 + font_small.size(self.url_input)[0]
                pygame.draw.line(surface, BLACK if not self.dark_mode else WHITE, 
                               (cursor_x, self.y + 45), (cursor_x, self.y + 65), 2)
            elif self.active_input == "search":
                cursor_x = self.x + 15 + font_small.size(self.search_input)[0]
                pygame.draw.line(surface, BLACK if not self.dark_mode else WHITE, 
                               (cursor_x, self.y + 85), (cursor_x, self.y + 105), 2)
        
        # Draw browser content
        content_rect = pygame.Rect(self.x + 10, self.y + 120, self.width - 20, self.height - 140)
        pygame.draw.rect(surface, WHITE, content_rect)
        pygame.draw.rect(surface, (100, 100, 100), content_rect, 1)
        
        # Loading indicator
        if self.loading:
            # Draw progress bar
            progress_width = content_rect.width * self.loading_progress
            pygame.draw.rect(surface, LIGHT_BLUE, (content_rect.x, content_rect.y, progress_width, 5))
            
            # Draw loading text
            loading_surf = font_small.render("Loading...", True, BLUE)
            surface.blit(loading_surf, (content_rect.centerx - loading_surf.get_width() // 2, 
                                       content_rect.centery - 20))
        else:
            # Simulated browser content
            content_text = f"Loaded: {self.url}"
            content_surf = font_medium.render(content_text, True, BLACK)
            surface.blit(content_surf, (content_rect.centerx - content_surf.get_width() // 2, 
                                       content_rect.centery - content_surf.get_height() // 2))
            
            # Speed indicator
            speed_text = "Loading speed: 0.5s (faster than Chrome)"
            speed_surf = font_tiny.render(speed_text, True, GREEN)
            surface.blit(speed_surf, (content_rect.centerx - speed_surf.get_width() // 2, 
                                     content_rect.centery + 50))
    
    def handle_event(self, event, pos):
        if super().handle_event(event, pos):
            return True
            
        if not self.active:
            return False
            
        # Handle button clicks
        if self.go_button.is_clicked(pos, event):
            self.navigate_to_url()
            return True
            
        if self.back_button.is_clicked(pos, event) and self.current_history_index > 0:
            self.current_history_index -= 1
            self.url = self.history[self.current_history_index]
            self.url_input = self.url
            self.simulate_loading()
            return True
            
        if self.forward_button.is_clicked(pos, event) and self.current_history_index < len(self.history) - 1:
            self.current_history_index += 1
            self.url = self.history[self.current_history_index]
            self.url_input = self.url
            self.simulate_loading()
            return True
            
        if self.search_button.is_clicked(pos, event):
            self.search_web()
            return True
            
        # Handle input focus
        if event.type == MOUSEBUTTONDOWN:
            url_rect = pygame.Rect(self.x + 220, self.y + 40, self.width - 310, 30)
            if url_rect.collidepoint(pos):
                self.active_input = "url"
            search_rect = pygame.Rect(self.x + 10, self.y + 80, self.width - 20, 30)
            if search_rect.collidepoint(pos):
                self.active_input = "search"
        
        # Handle keyboard input
        if event.type == KEYDOWN:
            if event.key == K_RETURN:
                if self.active_input == "url":
                    self.navigate_to_url()
                elif self.active_input == "search":
                    self.search_web()
                return True
            elif event.key == K_BACKSPACE:
                if self.active_input == "url" and self.url_input:
                    self.url_input = self.url_input[:-1]
                elif self.active_input == "search" and self.search_input:
                    self.search_input = self.search_input[:-1]
            else:
                if self.active_input == "url":
                    self.url_input += event.unicode
                elif self.active_input == "search":
                    self.search_input += event.unicode
            return True
            
        return False
        
    def navigate_to_url(self):
        url = self.url_input
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
            
        # Add to history
        if not self.history or self.history[-1] != url:
            self.history.append(url)
            self.current_history_index = len(self.history) - 1
            
        # Simulate fast loading
        self.simulate_loading()
        
    def search_web(self):
        query = self.search_input
        if query:
            url = f"https://www.google.com/search?q={query}"
            self.url_input = url
            self.navigate_to_url()
    
    def simulate_loading(self):
        self.loading = True
        self.loading_progress = 0
        
        def loading_thread():
            # Simulate fast loading
            for i in range(10):
                time.sleep(0.05)  # Much faster than regular browsers
                self.loading_progress = (i + 1) / 10
            self.loading = False
            
        threading.Thread(target=loading_thread, daemon=True).start()
    
    def update(self, dt):
        self.cursor_timer += dt
        if self.cursor_timer > 0.5:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

# ===== WNStore Window =====
class StoreWindow(Window):
    def __init__(self):
        super().__init__("WNStore", 700, 500)
        self.games = published_apps.copy()  # Start with published apps
        self.buttons = []
        self.installed_buttons = []
        self.selected_app = None
        self.status_message = ""
        self.status_timer = 0
        self.refresh_button = Button(
            self.x + 140, self.y + 40,
            100, 30, "Refresh",
            BLUE, LIGHT_BLUE
        )
        
        # Create upload button
        self.upload_button = Button(
            self.x + 10, self.y + 40,
            120, 30, "Upload App",
            PURPLE, (180, 100, 220)
        )
        
    def draw(self, surface):
        super().draw(surface)
        if not self.active:
            return
            
        # Update button positions
        self.upload_button.rect = pygame.Rect(self.x + 10, self.y + 40, 120, 30)
        self.refresh_button.rect = pygame.Rect(self.x + 140, self.y + 40, 100, 30)
        self.upload_button.draw(surface)
        self.refresh_button.draw(surface)
        
        # Draw status message
        if self.status_message and self.status_timer > 0:
            status_color = GREEN if "success" in self.status_message else RED
            status_surf = font_small.render(self.status_message, True, status_color)
            surface.blit(status_surf, (self.x + 250, self.y + 50))
        
        # Draw available apps section
        title_surf = font_medium.render("Available Apps", True, WHITE if self.dark_mode else BLACK)
        surface.blit(title_surf, (self.x + 20, self.y + 80))
        
        # Draw apps
        y_pos = self.y + 120
        for i, game in enumerate(self.games):
            # Only show install button if not already installed
            is_installed = any(app["name"] == game["name"] for app in installed_apps)
            
            # Draw app box
            app_rect = pygame.Rect(self.x + 20, y_pos, self.width - 40, 60)
            color = LIGHT_BLUE if self.selected_app == i else (LIGHT_GRAY if not self.dark_mode else DARK_GRAY)
            pygame.draw.rect(surface, color, app_rect, border_radius=5)
            pygame.draw.rect(surface, (100, 100, 100), app_rect, 1, border_radius=5)
            
            # Draw icon
            icon_rect = pygame.Rect(self.x + 30, y_pos + 10, 40, 40)
            pygame.draw.rect(surface, self.get_icon_color(game.get("type", "system")), icon_rect, border_radius=5)
            
            # Draw app info
            name_surf = font_small.render(game["name"], True, BLACK if not self.dark_mode else WHITE)
            surface.blit(name_surf, (self.x + 80, y_pos + 10))
            
            desc_surf = font_tiny.render(game.get("description", "No description"), True, BLACK if not self.dark_mode else WHITE)
            surface.blit(desc_surf, (self.x + 80, y_pos + 35))
            
            # Draw install button
            if not is_installed:
                install_btn = Button(
                    self.x + self.width - 120, y_pos + 15,
                    90, 30, "Install",
                    GREEN, (100, 220, 100)
                )
                install_btn.draw(surface)
                self.buttons.append({"btn": install_btn, "index": i})
            
            y_pos += 70
        
        # Draw installed apps section
        title_surf = font_medium.render("Installed Apps", True, WHITE if self.dark_mode else BLACK)
        surface.blit(title_surf, (self.x + 20, y_pos + 20))
        y_pos += 60
        
        for i, app in enumerate(installed_apps):
            # Draw app box
            app_rect = pygame.Rect(self.x + 20, y_pos, self.width - 40, 60)
            color = LIGHT_BLUE if self.selected_app == f"installed_{i}" else (LIGHT_GRAY if not self.dark_mode else DARK_GRAY)
            pygame.draw.rect(surface, color, app_rect, border_radius=5)
            pygame.draw.rect(surface, (100, 100, 100), app_rect, 1, border_radius=5)
            
            # Draw icon
            icon_rect = pygame.Rect(self.x + 30, y_pos + 10, 40, 40)
            pygame.draw.rect(surface, self.get_icon_color(app.get("type", "system")), icon_rect, border_radius=5)
            
            # Draw app info
            name_surf = font_small.render(app["name"], True, BLACK if not self.dark_mode else WHITE)
            surface.blit(name_surf, (self.x + 80, y_pos + 10))
            
            # Draw run button
            run_btn = Button(
                self.x + self.width - 220, y_pos + 15,
                90, 30, "Run",
                BLUE, LIGHT_BLUE
            )
            run_btn.draw(surface)
            self.installed_buttons.append({"btn": run_btn, "index": i, "type": "run"})
            
            # Draw uninstall button
            uninstall_btn = Button(
                self.x + self.width - 120, y_pos + 15,
                90, 30, "Uninstall",
                RED, (255, 100, 100)
            )
            uninstall_btn.draw(surface)
            self.installed_buttons.append({"btn": uninstall_btn, "index": i, "type": "uninstall"})
            
            y_pos += 70
    
    def get_icon_color(self, icon_type):
        colors = {
            "calendar": BLUE,
            "terminal": GREEN,
            "settings": PURPLE,
            "notepad": ORANGE,
            "system": CYAN,
            "snake": (100, 200, 100),
            "tictactoe": (200, 100, 200),
            "browser": (100, 150, 255),
            "store": (255, 150, 100)
        }
        return colors.get(icon_type, BLUE)
    
    def handle_event(self, event, pos):
        if super().handle_event(event, pos):
            return True
            
        if not self.active:
            return False
            
        # Handle upload button
        if self.upload_button.is_clicked(pos, event):
            self.upload_app()
            return True
            
        # Handle refresh button
        if self.refresh_button.is_clicked(pos, event):
            self.refresh_apps()
            return True
            
        # Handle install buttons
        for button_info in self.buttons:
            if button_info["btn"].is_clicked(pos, event):
                self.install_app(button_info["index"])
                return True
                
        # Handle installed app buttons
        for button_info in self.installed_buttons:
            if button_info["btn"].is_clicked(pos, event):
                if button_info["type"] == "run":
                    self.run_app(button_info["index"])
                elif button_info["type"] == "uninstall":
                    self.uninstall_app(button_info["index"])
                return True
                
        # Handle app selection
        if event.type == MOUSEBUTTONDOWN:
            # Clear selection
            self.selected_app = None
            
            # Check available apps
            y_pos = self.y + 120
            for i in range(len(self.games)):
                app_rect = pygame.Rect(self.x + 20, y_pos, self.width - 40, 60)
                if app_rect.collidepoint(pos):
                    self.selected_app = i
                    return True
                y_pos += 70
                
            # Check installed apps
            y_pos += 60  # Skip installed apps title
            for i in range(len(installed_apps)):
                app_rect = pygame.Rect(self.x + 20, y_pos, self.width - 40, 60)
                if app_rect.collidepoint(pos):
                    self.selected_app = f"installed_{i}"
                    return True
                y_pos += 70
                    
        return False
        
    def install_app(self, index):
        app = self.games[index]
        # Check if already installed
        if any(installed["name"] == app["name"] for installed in installed_apps):
            self.show_status("App already installed", success=False)
            return
            
        # Add to installed apps
        installed_apps.append(app)
        save_installed_apps(installed_apps)
        self.show_status(f"Installed: {app['name']}")
        
    def run_app(self, index):
        app = installed_apps[index]
        try:
            if platform.system() == "Windows" and app["path"].endswith(".exe"):
                subprocess.Popen(app["path"])
            elif platform.system() == "Darwin" and app["path"].endswith(".app"):
                subprocess.Popen(["open", app["path"]])
            else:
                subprocess.Popen(app["path"])
            self.show_status(f"Running: {app['name']}")
        except Exception as e:
            self.show_status(f"Error running app: {str(e)}", success=False)
            
    def uninstall_app(self, index):
        if 0 <= index < len(installed_apps):
            # Remove the app
            app_name = installed_apps[index]["name"]
            del installed_apps[index]
            save_installed_apps(installed_apps)
            self.show_status(f"Uninstalled: {app_name}")
            
    def upload_app(self):
        # Use tkinter file dialog for simplicity
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        file_path = filedialog.askopenfilename(
            title="Select Application File",
            filetypes=[("Executable Files", "*.exe *.app *.py"), ("All Files", "*.*")]
        )
        
        if file_path:
            # Get filename without extension
            filename = os.path.basename(file_path)
            app_name = os.path.splitext(filename)[0]
            
            # Ask for app description
            description = tk.simpledialog.askstring("App Description", 
                                                   "Enter a description for your app:", 
                                                   parent=root)
            
            if description is None:
                return
                
            # Add to published apps
            new_app = {
                "name": app_name,
                "description": description,
                "path": file_path,
                "type": "external",
                "publisher": "You"
            }
            
            # Simulate publishing to server
            self.publish_app(new_app)
            
    def publish_app(self, app):
        # In a real app, this would send the app to a server
        # Here we'll just add it to our local published list and save
        published_apps.append(app)
        save_published_apps(published_apps)
        
        # Update the list
        self.games = published_apps.copy()
        self.show_status(f"Published: {app['name']} - Now available to others!")
        
        # In a real app, you would send this to a server
        # Here's what that might look like:
        """
        try:
            response = requests.post(f"{SERVER_URL}/publish", json=app)
            if response.status_code == 200:
                self.show_status(f"Published: {app['name']} - Now available to others!")
            else:
                self.show_status("Publishing failed", success=False)
        except Exception as e:
            self.show_status(f"Error publishing: {str(e)}", success=False)
        """
    
    def refresh_apps(self):
        # In a real app, this would fetch from a server
        # Here we'll just reload from file
        global published_apps
        published_apps = load_published_apps()
        self.games = published_apps.copy()
        self.show_status("Apps refreshed from server")
        
        # Simulate network request
        """
        try:
            response = requests.get(f"{SERVER_URL}/apps")
            if response.status_code == 200:
                published_apps = response.json()
                self.games = published_apps.copy()
                self.show_status("Apps refreshed from server")
            else:
                self.show_status("Refresh failed", success=False)
        except Exception as e:
            self.show_status(f"Error refreshing: {str(e)}", success=False)
        """
    
    def show_status(self, message, success=True):
        self.status_message = message
        self.status_timer = 3  # Show for 3 seconds
    
    def update(self, dt):
        if self.status_timer > 0:
            self.status_timer -= dt

# ===== Programs Window =====
class ProgramsWindow(Window):
    def __init__(self):
        super().__init__("Programs", 500, 400)
        self.app_buttons = []
        
    def draw(self, surface):
        super().draw(surface)
        if not self.active:
            return
            
        # Draw title
        title_surf = font_medium.render("Installed Applications", True, WHITE if self.dark_mode else BLACK)
        surface.blit(title_surf, (self.x + 20, self.y + 20))
        
        # Draw installed apps
        y_pos = self.y + 60
        self.app_buttons = []
        
        for i, app in enumerate(installed_apps):
            # Draw app button
            btn = Button(
                self.x + 20, y_pos,
                self.width - 40, 50,
                app["name"],
                self.get_app_color(app.get("type", "system")),
                LIGHT_BLUE
            )
            btn.draw(surface)
            self.app_buttons.append(btn)
            
            y_pos += 60
    
    def get_app_color(self, app_type):
        colors = {
            "calendar": BLUE,
            "terminal": GREEN,
            "settings": PURPLE,
            "notepad": ORANGE,
            "system": CYAN,
            "snake": (100, 200, 100),
            "tictactoe": (200, 100, 200),
            "browser": (100, 150, 255),
            "store": (255, 150, 100),
            "external": LIGHT_BLUE
        }
        return colors.get(app_type, BLUE)
    
    def handle_event(self, event, pos):
        if super().handle_event(event, pos):
            return True
            
        if not self.active:
            return False
            
        # Handle app button clicks
        for i, btn in enumerate(self.app_buttons):
            if btn.is_clicked(pos, event):
                app = installed_apps[i]
                try:
                    if platform.system() == "Windows" and app["path"].endswith(".exe"):
                        subprocess.Popen(app["path"])
                    elif platform.system() == "Darwin" and app["path"].endswith(".app"):
                        subprocess.Popen(["open", app["path"]])
                    else:
                        subprocess.Popen(app["path"])
                except Exception as e:
                    print(f"Error running app: {e}")
                return True
                    
        return False

class DesktopIcon:
    def __init__(self, x, y, text, app_type):
        self.rect = pygame.Rect(x, y, 80, 90)
        self.text = text
        self.app_type = app_type
        self.hovered = False
        self.colors = {
            "calendar": BLUE,
            "terminal": GREEN,
            "settings": PURPLE,
            "notepad": ORANGE,
            "system": CYAN,
            "snake": (100, 200, 100),  # Green for snake game
            "tictactoe": (200, 100, 200),  # Purple for tic-tac-toe
            "browser": (100, 150, 255),    # Blue for browser
            "store": (255, 150, 100),      # Orange for store
            "programs": (150, 100, 200),   # Purple for programs
            "external": LIGHT_BLUE         # Light blue for external apps
        }
        
    def draw(self, surface):
        color = self.colors.get(self.app_type, BLUE)
        hover_color = tuple(min(c + 40, 255) for c in color)
        
        # Draw icon background
        pygame.draw.rect(surface, hover_color if self.hovered else color, self.rect, border_radius=10)
        pygame.draw.rect(surface, (30, 30, 30), self.rect, 2, border_radius=10)
        
        # Draw icon symbol
        symbol_rect = pygame.Rect(self.rect.x + 15, self.rect.y + 10, 50, 50)
        pygame.draw.rect(surface, WHITE, symbol_rect, border_radius=5)
        
        # Draw app-specific symbol
        if self.app_type == "calendar":
            pygame.draw.rect(surface, BLUE, (symbol_rect.x + 10, symbol_rect.y + 10, 30, 30), 2)
            for i in range(7):
                pygame.draw.rect(surface, BLUE, (symbol_rect.x + 10 + i*4, symbol_rect.y + 15, 2, 2))
        elif self.app_type == "terminal":
            pygame.draw.rect(surface, GREEN, (symbol_rect.x + 10, symbol_rect.y + 15, 30, 20))
            text_surf = font_tiny.render(">_", True, WHITE)
            surface.blit(text_surf, (symbol_rect.x + 15, symbol_rect.y + 18))
        elif self.app_type == "settings":
            pygame.draw.circle(surface, PURPLE, symbol_rect.center, 20, 2)
            pygame.draw.circle(surface, PURPLE, symbol_rect.center, 10, 2)
            pygame.draw.line(surface, PURPLE, 
                           (symbol_rect.centerx, symbol_rect.centery - 25),
                           (symbol_rect.centerx, symbol_rect.centery - 15), 2)
        elif self.app_type == "notepad":
            pygame.draw.rect(surface, ORANGE, (symbol_rect.x + 10, symbol_rect.y + 10, 30, 30))
            for i in range(4):
                pygame.draw.line(surface, WHITE, 
                               (symbol_rect.x + 15, symbol_rect.y + 15 + i*7),
                               (symbol_rect.x + 35, symbol_rect.y + 15 + i*7), 2)
        elif self.app_type == "system":
            pygame.draw.rect(surface, CYAN, (symbol_rect.x + 10, symbol_rect.y + 10, 30, 30))
            pygame.draw.line(surface, WHITE, 
                           (symbol_rect.centerx - 10, symbol_rect.centery),
                           (symbol_rect.centerx + 10, symbol_rect.centery), 2)
            pygame.draw.line(surface, WHITE, 
                           (symbol_rect.centerx, symbol_rect.centery - 10),
                           (symbol_rect.centerx, symbol_rect.centery + 10), 2)
        elif self.app_type == "snake":
            # Draw snake icon
            pygame.draw.rect(surface, GREEN, (symbol_rect.x + 15, symbol_rect.y + 20, 20, 10))
            pygame.draw.rect(surface, GREEN, (symbol_rect.x + 25, symbol_rect.y + 15, 10, 20))
            # Draw food
            pygame.draw.rect(surface, RED, (symbol_rect.x + 35, symbol_rect.y + 25, 5, 5))
        elif self.app_type == "tictactoe":
            # Draw tic-tac-toe board
            pygame.draw.line(surface, BLACK, 
                           (symbol_rect.x + 20, symbol_rect.y + 15),
                           (symbol_rect.x + 20, symbol_rect.y + 35), 2)
            pygame.draw.line(surface, BLACK, 
                           (symbol_rect.x + 30, symbol_rect.y + 15),
                           (symbol_rect.x + 30, symbol_rect.y + 35), 2)
            pygame.draw.line(surface, BLACK, 
                           (symbol_rect.x + 15, symbol_rect.y + 20),
                           (symbol_rect.x + 35, symbol_rect.y + 20), 2)
            pygame.draw.line(surface, BLACK, 
                           (symbol_rect.x + 15, symbol_rect.y + 30),
                           (symbol_rect.x + 35, symbol_rect.y + 30), 2)
            # Draw X and O
            pygame.draw.line(surface, RED, 
                           (symbol_rect.x + 17, symbol_rect.y + 17),
                           (symbol_rect.x + 23, symbol_rect.y + 23), 2)
            pygame.draw.line(surface, RED, 
                           (symbol_rect.x + 23, symbol_rect.y + 17),
                           (symbol_rect.x + 17, symbol_rect.y + 23), 2)
            pygame.draw.circle(surface, BLUE, (symbol_rect.x + 33, symbol_rect.y + 33), 4, 2)
        elif self.app_type == "browser":
            # Draw browser icon
            pygame.draw.rect(surface, (100, 150, 255), (symbol_rect.x + 10, symbol_rect.y + 10, 30, 30))
            pygame.draw.rect(surface, (200, 200, 255), (symbol_rect.x + 15, symbol_rect.y + 15, 20, 15))
            pygame.draw.rect(surface, (100, 150, 255), (symbol_rect.x + 15, symbol_rect.y + 15, 20, 5))
        elif self.app_type == "store":
            # Draw store icon
            pygame.draw.rect(surface, (255, 150, 100), (symbol_rect.x + 10, symbol_rect.y + 10, 30, 30))
            pygame.draw.rect(surface, (255, 200, 150), (symbol_rect.x + 15, symbol_rect.y + 15, 20, 10))
            pygame.draw.rect(surface, (255, 200, 150), (symbol_rect.x + 15, symbol_rect.y + 27, 8, 8))
            pygame.draw.rect(surface, (255, 200, 150), (symbol_rect.x + 27, symbol_rect.y + 27, 8, 8))
        elif self.app_type == "programs":
            # Draw programs icon (start menu style)
            pygame.draw.rect(surface, (150, 100, 200), (symbol_rect.x + 10, symbol_rect.y + 10, 30, 30))
            pygame.draw.line(surface, WHITE, (symbol_rect.x + 15, symbol_rect.y + 15), (symbol_rect.x + 25, symbol_rect.y + 15), 2)
            pygame.draw.line(surface, WHITE, (symbol_rect.x + 15, symbol_rect.y + 20), (symbol_rect.x + 25, symbol_rect.y + 20), 2)
            pygame.draw.line(surface, WHITE, (symbol_rect.x + 15, symbol_rect.y + 25), (symbol_rect.x + 25, symbol_rect.y + 25), 2)
        else:  # External app
            # Draw generic app icon
            pygame.draw.rect(surface, (100, 180, 255), (symbol_rect.x + 10, symbol_rect.y + 10, 30, 30))
            pygame.draw.circle(surface, WHITE, (symbol_rect.x + 25, symbol_rect.y + 25), 10, 2)
            pygame.draw.line(surface, WHITE, (symbol_rect.x + 20, symbol_rect.y + 25), (symbol_rect.x + 30, symbol_rect.y + 25), 2)
            pygame.draw.line(surface, WHITE, (symbol_rect.x + 25, symbol_rect.y + 20), (symbol_rect.x + 25, symbol_rect.y + 30), 2)
        
        # Draw text
        text_surf = font_tiny.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=(self.rect.centerx, self.rect.bottom - 15))
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)
        return self.hovered
        
    def is_clicked(self, pos, event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

def draw_gradient_background(surface, dark_mode):
    """Draw gradient background based on mode"""
    top_color = DARK_GRADIENT_TOP if dark_mode else LIGHT_GRADIENT_TOP
    bottom_color = DARK_GRADIENT_BOTTOM if dark_mode else LIGHT_GRADIENT_BOTTOM
    
    for y in range(SCREEN_HEIGHT):
        ratio = y / SCREEN_HEIGHT
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (SCREEN_WIDTH, y))

def draw_sticky_notes_background(surface):
    """Draw sticky notes background pattern"""
    colors = [
        (255, 255, 200),  # Yellow
        (200, 255, 200),  # Green
        (255, 200, 200),  # Pink
        (200, 200, 255),  # Blue
    ]
    
    note_width, note_height = 120, 120
    for y in range(0, SCREEN_HEIGHT + note_height, note_height):
        for x in range(0, SCREEN_WIDTH + note_width, note_width):
            idx = (x // note_width + y // note_height) % len(colors)
            color = colors[idx]
            
            # Draw note with shadow
            pygame.draw.rect(surface, (150, 150, 150), 
                            (x + 5, y + 5, note_width, note_height))
            pygame.draw.rect(surface, color, 
                            (x, y, note_width, note_height))
            
            # Draw note corner
            pygame.draw.polygon(surface, (220, 220, 180), 
                              [(x + note_width - 20, y),
                               (x + note_width, y),
                               (x + note_width, y + 20)])

def draw_graph_paper_background(surface, dark_mode):
    """Draw graph paper background"""
    bg_color = DARK_GRADIENT_BOTTOM if dark_mode else LIGHT_GRADIENT_BOTTOM
    grid_color = (80, 80, 100) if dark_mode else (180, 180, 200)
    axis_color = (120, 120, 150) if dark_mode else (150, 150, 180)
    
    surface.fill(bg_color)
    
    # Draw grid
    grid_size = 20
    for x in range(0, SCREEN_WIDTH, grid_size):
        color = axis_color if x % 100 == 0 else grid_color
        pygame.draw.line(surface, color, (x, 0), (x, SCREEN_HEIGHT), 1 if x % 100 != 0 else 2)
        
    for y in range(0, SCREEN_HEIGHT, grid_size):
        color = axis_color if y % 100 == 0 else grid_color
        pygame.draw.line(surface, color, (0, y), (SCREEN_WIDTH, y), 1 if y % 100 != 0 else 2)
    
    # Draw coordinate labels
    for x in range(100, SCREEN_WIDTH, 100):
        for y in range(100, SCREEN_HEIGHT, 100):
            label = f"({x//100}, {y//100})"
            text_surf = font_tiny.render(label, True, grid_color)
            surface.blit(text_surf, (x + 5, y + 5))

def draw_nature_background(surface):
    """Draw nature-inspired background"""
    # Sky gradient
    for y in range(SCREEN_HEIGHT // 2):
        ratio = y / (SCREEN_HEIGHT // 2)
        r = int(135 * (1 - ratio) + 70 * ratio)
        g = int(206 * (1 - ratio) + 130 * ratio)
        b = int(235 * (1 - ratio) + 180 * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (SCREEN_WIDTH, y))
    
    # Ground
    pygame.draw.rect(surface, (60, 120, 60), (0, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
    
    # Sun
    pygame.draw.circle(surface, (255, 255, 200), (SCREEN_WIDTH - 100, 100), 50)
    
    # Trees
    for x in range(100, SCREEN_WIDTH, 200):
        tree_height = 120 + (x % 50)
        pygame.draw.rect(surface, (100, 70, 40), (x, SCREEN_HEIGHT // 2 - tree_height // 3, 20, tree_height // 3))
        pygame.draw.circle(surface, (40, 120, 60), (x + 10, SCREEN_HEIGHT // 2 - tree_height // 3 - 30), 50)

def draw_project_notes_background(surface, dark_mode):
    """Draw project notes background"""
    bg_color = DARK_GRADIENT_BOTTOM if dark_mode else LIGHT_GRADIENT_BOTTOM
    surface.fill(bg_color)
    
    # Draw notes
    notes = [
        {"text": "PROJECT", "pos": (100, 100), "color": (200, 150, 255)},
        {"text": "PHASE: 1", "pos": (300, 150), "color": (150, 200, 255)},
        {"text": "PHASE: 2", "pos": (500, 200), "color": (255, 200, 150)},
        {"text": "Set GOALS", "pos": (200, 300), "color": (200, 255, 150)},
        {"text": "FINAL REPORT", "pos": (400, 350), "color": (255, 150, 200)},
        {"text": "QUALITY STANDARD", "pos": (600, 400), "color": (150, 255, 200)},
        {"text": "DOUBLE CHECK", "pos": (800, 100), "color": (255, 220, 150)},
    ]
    
    for note in notes:
        x, y = note["pos"]
        color = note["color"]
        
        # Draw note
        pygame.draw.rect(surface, (50, 50, 50), (x + 5, y + 5, 200, 50))
        pygame.draw.rect(surface, color, (x, y, 200, 50), border_radius=5)
        pygame.draw.rect(surface, (30, 30, 30), (x, y, 200, 50), 2, border_radius=5)
        
        # Draw text
        text_surf = font_small.render(note["text"], True, (30, 30, 30))
        text_rect = text_surf.get_rect(center=(x + 100, y + 25))
        surface.blit(text_surf, text_rect)

def draw_solid_color_background(surface, color):
    """Draw solid color background"""
    surface.fill(color)

def main():
    global SCREEN_WIDTH, SCREEN_HEIGHT, screen, published_apps, installed_apps
    
    # Desktop settings
    dark_mode = False
    current_wallpaper = "Gradient"
    solid_color = BLUE
    
    # Create desktop icons
    icons = [
        DesktopIcon(50, 50, "Calendar", "calendar"),
        DesktopIcon(150, 50, "Terminal", "terminal"),
        DesktopIcon(250, 50, "Settings", "settings"),
        DesktopIcon(350, 50, "Notepad", "notepad"),
        DesktopIcon(450, 50, "System Info", "system"),
        DesktopIcon(50, 150, "Snake Game", "snake"),
        DesktopIcon(150, 150, "Tic-Tac-Toe", "tictactoe"),
        DesktopIcon(250, 150, "Browser", "browser"),
        DesktopIcon(350, 150, "App Store", "store"),
        DesktopIcon(450, 150, "Programs", "programs")  # New programs icon
    ]
    
    # Add icons for installed apps
    x_pos, y_pos = 50, 250
    for app in installed_apps:
        icons.append(DesktopIcon(x_pos, y_pos, app["name"], app.get("type", "external")))
        x_pos += 100
        if x_pos > SCREEN_WIDTH - 100:
            x_pos = 50
            y_pos += 110
    
    # Create taskbar
    taskbar_height = 40
    taskbar_rect = pygame.Rect(0, SCREEN_HEIGHT - taskbar_height, SCREEN_WIDTH, taskbar_height)
    
    # Start menu button
    start_button = Button(10, SCREEN_HEIGHT - 35, 80, 30, "Start", BLUE, LIGHT_BLUE)
    
    # Clock
    clock_font = pygame.font.SysFont("Arial", 18)
    
    # Open windows
    open_windows = []
    
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0  # Delta time in seconds
        mouse_pos = pygame.mouse.get_pos()
        
        # Event handling
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == VIDEORESIZE:
                # Handle window resizing
                SCREEN_WIDTH, SCREEN_HEIGHT = event.size
                screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
                
                # Update taskbar position
                taskbar_rect = pygame.Rect(0, SCREEN_HEIGHT - taskbar_height, SCREEN_WIDTH, taskbar_height)
                
                # Update start button position
                start_button.rect = pygame.Rect(10, SCREEN_HEIGHT - 35, 80, 30)
                
                # Reset desktop icons to top-left corner
                for i, icon in enumerate(icons):
                    if i < 10:  # First row of icons
                        icon.rect = pygame.Rect(50 + (i % 5) * 100, 50 + (i // 5) * 100, 80, 90)
                    else:  # Installed apps
                        # We'll just reset them to avoid complexity
                        pass
                
            # Handle open windows (from top to bottom)
            window_handled = False
            for window in reversed(open_windows):
                if window.active and window.handle_event(event, mouse_pos):
                    window_handled = True
                    break
                    
            if window_handled:
                continue
                
            # Handle start button
            if start_button.is_clicked(mouse_pos, event):
                # Open programs window when start button is clicked
                open_windows.append(ProgramsWindow())
                continue
                
            # Handle desktop icons
            for icon in icons:
                if icon.is_clicked(mouse_pos, event):
                    if icon.app_type == "calendar":
                        open_windows.append(CalendarWindow())
                    elif icon.app_type == "terminal":
                        open_windows.append(TerminalWindow())
                    elif icon.app_type == "settings":
                        open_windows.append(SettingsWindow())
                    elif icon.app_type == "notepad":
                        open_windows.append(NotepadWindow())
                    elif icon.app_type == "system":
                        open_windows.append(SystemInfoWindow())
                    elif icon.app_type == "snake":
                        open_windows.append(SnakeGameWindow())
                    elif icon.app_type == "tictactoe":
                        open_windows.append(TicTacToeWindow())
                    elif icon.app_type == "browser":
                        open_windows.append(BrowserWindow())
                    elif icon.app_type == "store":
                        open_windows.append(StoreWindow())
                    elif icon.app_type == "programs":
                        open_windows.append(ProgramsWindow())
                    else:
                        # Handle installed apps
                        for app in installed_apps:
                            if app["name"] == icon.text:
                                try:
                                    if platform.system() == "Windows" and app["path"].endswith(".exe"):
                                        subprocess.Popen(app["path"])
                                    elif platform.system() == "Darwin" and app["path"].endswith(".app"):
                                        subprocess.Popen(["open", app["path"]])
                                    else:
                                        subprocess.Popen(app["path"])
                                except Exception as e:
                                    print(f"Error running app: {e}")
                    break
        
        # Update hover states
        for icon in icons:
            icon.check_hover(mouse_pos)
        start_button.check_hover(mouse_pos)
        
        # Draw background based on wallpaper selection
        if current_wallpaper == "Gradient":
            draw_gradient_background(screen, dark_mode)
        elif current_wallpaper == "Sticky Notes":
            draw_sticky_notes_background(screen)
        elif current_wallpaper == "Project Notes":
            draw_project_notes_background(screen, dark_mode)
        elif current_wallpaper == "Graph Paper":
            draw_graph_paper_background(screen, dark_mode)
        elif current_wallpaper == "Nature":
            draw_nature_background(screen)
        elif current_wallpaper == "Solid Color":
            draw_solid_color_background(screen, solid_color)
        
        # Draw desktop icons
        for icon in icons:
            icon.draw(screen)
        
        # Draw taskbar
        pygame.draw.rect(screen, (50, 50, 70), taskbar_rect)
        pygame.draw.line(screen, (100, 100, 120), (0, SCREEN_HEIGHT - taskbar_height), 
                        (SCREEN_WIDTH, SCREEN_HEIGHT - taskbar_height), 2)
        
        # Draw start button
        start_button.draw(screen)
        
        # Draw clock
        current_time = time.strftime("%H:%M:%S")
        time_surf = clock_font.render(current_time, True, WHITE)
        screen.blit(time_surf, (SCREEN_WIDTH - 100, SCREEN_HEIGHT - 30))
        
        # Draw open windows
        for window in open_windows:
            window.draw(screen)
            
        # Update windows that need it
        for window in open_windows:
            if isinstance(window, (TerminalWindow, NotepadWindow, SnakeGameWindow, BrowserWindow, StoreWindow)):
                window.update(dt)
        
        # Handle settings changes
        for window in open_windows[:]:
            if isinstance(window, SettingsWindow) and window.last_action:
                action = window.last_action
                window.last_action = None
                
                if action[0] == "wallpaper":
                    current_wallpaper = action[1]
                    if current_wallpaper == "Solid Color":
                        solid_color = random.choice([BLUE, GREEN, PURPLE, ORANGE, CYAN])
                
                elif action[0] == "theme":
                    dark_mode = (action[1] == "Dark")
                    # Apply theme to all open windows
                    for w in open_windows:
                        w.dark_mode = dark_mode
                
                elif action[0] == "sysinfo":
                    open_windows.append(SystemInfoWindow())
                
                elif action[0] == "resolution":
                    open_windows.append(ResolutionWindow())
        
        # Handle resolution changes
        for window in open_windows[:]:
            if isinstance(window, ResolutionWindow) and window.last_action:
                resolution = window.last_action
                window.last_action = None
                
                if resolution == "custom":
                    custom_window = CustomResolutionWindow()
                    open_windows.append(custom_window)
                else:
                    # Apply resolution change
                    SCREEN_WIDTH, SCREEN_HEIGHT = resolution
                    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
                    pygame.display.set_caption("WNOS Desktop Environment")
                    
                    # Update taskbar position
                    taskbar_rect = pygame.Rect(0, SCREEN_HEIGHT - taskbar_height, SCREEN_WIDTH, taskbar_height)
                    
                    # Update start button position
                    start_button.rect = pygame.Rect(10, SCREEN_HEIGHT - 35, 80, 30)
                    
                    # Reset desktop icons to top-left corner
                    for i, icon in enumerate(icons):
                        if i < 10:  # First row of icons
                            icon.rect = pygame.Rect(50 + (i % 5) * 100, 50 + (i // 5) * 100, 80, 90)
                        else:  # Installed apps
                            # We'll just reset them to avoid complexity
                            pass
            
            elif isinstance(window, CustomResolutionWindow) and window.last_action:
                resolution = window.last_action
                window.last_action = None
                
                # Apply custom resolution
                SCREEN_WIDTH, SCREEN_HEIGHT = resolution
                screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
                pygame.display.set_caption("WNOS Desktop Environment")
                
                # Update taskbar position
                taskbar_rect = pygame.Rect(0, SCREEN_HEIGHT - taskbar_height, SCREEN_WIDTH, taskbar_height)
                
                # Update start button position
                start_button.rect = pygame.Rect(10, SCREEN_HEIGHT - 35, 80, 30)
                
                # Reset desktop icons to top-left corner
                for i, icon in enumerate(icons):
                    if i < 10:  # First row of icons
                        icon.rect = pygame.Rect(50 + (i % 5) * 100, 50 + (i // 5) * 100, 80, 90)
                    else:  # Installed apps
                        # We'll just reset them to avoid complexity
                        pass
        
        # Remove closed windows
        open_windows = [w for w in open_windows if w.active]
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()