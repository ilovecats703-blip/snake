#!/usr/bin/env python3
"""
Terminal Snake Game
A classic Snake game implemented using Python's curses library.
Controls: Use arrow keys or WASD to move, Q to quit, R to restart.
"""

import curses
import random
import time
from enum import Enum
from typing import List, Tuple

class Direction(Enum):
    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)

class SnakeGame:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.score = 0
        self.high_score = 0
        
        # Get screen dimensions
        self.height, self.width = stdscr.getmaxyx()
        
        # Game area (leave space for borders and score)
        self.game_height = self.height - 4  # Leave space for score and instructions
        self.game_width = self.width - 2    # Leave space for side borders
        
        # Initialize game state
        self.reset_game()
        
        # Setup curses
        curses.curs_set(0)  # Hide cursor
        stdscr.nodelay(1)   # Don't wait for key input
        stdscr.timeout(100)  # Game speed (milliseconds)
        
        # Setup colors if terminal supports them
        if curses.has_colors():
            curses.start_color()
            curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Snake
            curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)    # Food
            curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Score
            curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)   # Border
        
    def reset_game(self):
        """Reset the game to initial state"""
        # Snake starts in the middle of the screen
        start_y = self.game_height // 2
        start_x = self.game_width // 2
        
        self.snake = [(start_y, start_x), (start_y, start_x - 1), (start_y, start_x - 2)]
        self.direction = Direction.RIGHT
        self.food = self.generate_food()
        self.game_over = False
        self.score = 0
        
    def generate_food(self) -> Tuple[int, int]:
        """Generate food at a random position not occupied by the snake"""
        while True:
            food_y = random.randint(1, self.game_height - 1)
            food_x = random.randint(1, self.game_width - 1)
            if (food_y, food_x) not in self.snake:
                return (food_y, food_x)
    
    def handle_input(self):
        """Handle keyboard input"""
        key = self.stdscr.getch()
        
        if key == ord('q') or key == ord('Q'):
            return False  # Quit game
        elif key == ord('r') or key == ord('R'):
            if self.game_over:
                self.reset_game()
        elif not self.game_over:
            # Movement controls
            if key == curses.KEY_UP or key == ord('w') or key == ord('W'):
                if self.direction != Direction.DOWN:
                    self.direction = Direction.UP
            elif key == curses.KEY_DOWN or key == ord('s') or key == ord('S'):
                if self.direction != Direction.UP:
                    self.direction = Direction.DOWN
            elif key == curses.KEY_LEFT or key == ord('a') or key == ord('A'):
                if self.direction != Direction.RIGHT:
                    self.direction = Direction.LEFT
            elif key == curses.KEY_RIGHT or key == ord('d') or key == ord('D'):
                if self.direction != Direction.LEFT:
                    self.direction = Direction.RIGHT
        
        return True  # Continue game
    
    def update_snake(self):
        """Update snake position and check for collisions"""
        if self.game_over:
            return
            
        # Get the head of the snake
        head_y, head_x = self.snake[0]
        
        # Calculate new head position
        dy, dx = self.direction.value
        new_head = (head_y + dy, head_x + dx)
        
        # Check wall collision
        if (new_head[0] <= 0 or new_head[0] >= self.game_height or
            new_head[1] <= 0 or new_head[1] >= self.game_width):
            self.game_over = True
            if self.score > self.high_score:
                self.high_score = self.score
            return
        
        # Check self collision
        if new_head in self.snake:
            self.game_over = True
            if self.score > self.high_score:
                self.high_score = self.score
            return
        
        # Add new head
        self.snake.insert(0, new_head)
        
        # Check if food is eaten
        if new_head == self.food:
            self.score += 10
            self.food = self.generate_food()
            # Increase speed slightly as score increases
            new_timeout = max(50, 100 - (self.score // 50))
            self.stdscr.timeout(new_timeout)
        else:
            # Remove tail if no food eaten
            self.snake.pop()
    
    def draw_border(self):
        """Draw game border"""
        if curses.has_colors():
            self.stdscr.attron(curses.color_pair(4))
        
        # Draw horizontal borders
        for x in range(self.width - 1):
            self.stdscr.addch(0, x, '═')
            self.stdscr.addch(self.game_height + 1, x, '═')
        
        # Draw vertical borders
        for y in range(self.game_height + 2):
            self.stdscr.addch(y, 0, '║')
            self.stdscr.addch(y, self.game_width + 1, '║')
        
        # Draw corners
        self.stdscr.addch(0, 0, '╔')
        self.stdscr.addch(0, self.game_width + 1, '╗')
        self.stdscr.addch(self.game_height + 1, 0, '╚')
        self.stdscr.addch(self.game_height + 1, self.game_width + 1, '╝')
        
        if curses.has_colors():
            self.stdscr.attroff(curses.color_pair(4))
    
    def draw_snake(self):
        """Draw the snake"""
        if curses.has_colors():
            self.stdscr.attron(curses.color_pair(1))
        
        for i, (y, x) in enumerate(self.snake):
            if i == 0:  # Head
                self.stdscr.addch(y, x, '◉')
            else:  # Body
                self.stdscr.addch(y, x, '●')
        
        if curses.has_colors():
            self.stdscr.attroff(curses.color_pair(1))
    
    def draw_food(self):
        """Draw the food"""
        if curses.has_colors():
            self.stdscr.attron(curses.color_pair(2))
        
        y, x = self.food
        self.stdscr.addch(y, x, '◆')
        
        if curses.has_colors():
            self.stdscr.attroff(curses.color_pair(2))
    
    def draw_score(self):
        """Draw score and game information"""
        if curses.has_colors():
            self.stdscr.attron(curses.color_pair(3))
        
        # Current score
        score_text = f"Score: {self.score}"
        self.stdscr.addstr(self.game_height + 2, 2, score_text)
        
        # High score
        high_score_text = f"High Score: {self.high_score}"
        self.stdscr.addstr(self.game_height + 2, 20, high_score_text)
        
        # Game over message
        if self.game_over:
            game_over_text = "GAME OVER! Press 'R' to restart, 'Q' to quit"
            # Center the game over text
            x = (self.width - len(game_over_text)) // 2
            self.stdscr.addstr(self.game_height + 3, x, game_over_text)
        else:
            # Instructions
            instructions = "Use Arrow Keys or WASD to move, Q to quit"
            x = max(0, (self.width - len(instructions)) // 2)
            self.stdscr.addstr(self.game_height + 3, x, instructions)
        
        if curses.has_colors():
            self.stdscr.attroff(curses.color_pair(3))
    
    def draw_game(self):
        """Draw the entire game"""
        self.stdscr.clear()
        
        # Draw all game elements
        self.draw_border()
        self.draw_snake()
        self.draw_food()
        self.draw_score()
        
        self.stdscr.refresh()
    
    def run(self):
        """Main game loop"""
        while True:
            # Handle input
            if not self.handle_input():
                break  # Quit game
            
            # Update game state
            self.update_snake()
            
            # Draw everything
            self.draw_game()
            
            # Small delay for smooth animation
            time.sleep(0.01)

def main():
    """Main function to initialize and run the game"""
    try:
        # Check terminal size
        import os
        size = os.get_terminal_size()
        if size.columns < 40 or size.lines < 10:
            print("Terminal window too small! Please resize to at least 40x10 characters.")
            return
        
        # Initialize and run the game
        curses.wrapper(lambda stdscr: SnakeGame(stdscr).run())
        
    except KeyboardInterrupt:
        print("\nGame interrupted. Thanks for playing!")
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Make sure your terminal supports curses and has adequate size.")

if __name__ == "__main__":
    print("🐍 Welcome to Terminal Snake Game! 🐍")
    print("Loading game...")
    time.sleep(1)
    main()
