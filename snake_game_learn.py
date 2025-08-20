#!/usr/bin/env python3
# This line tells the computer "Hey, use Python 3 to run this file!"
# It's like saying "This is a Python recipe, not a cooking recipe"

"""
This is a multi-line comment (called a docstring)
Think of it like a big sticky note that explains what this whole file does
Terminal Snake Game
A classic Snake game implemented using Python's curses library.
Controls: Use arrow keys or WASD to move, Q to quit, R to restart.
"""

# These are called "imports" - think of them like borrowing tools from a toolbox
# We're telling Python "Hey, I need to borrow these special tools to make my game work"

import curses
# curses = special tool that lets us draw things in the terminal (like colored text and shapes)

import random  
# random = tool that helps us pick random numbers (like rolling dice)

import time
# time = tool that helps us work with time (like a stopwatch)

from enum import Enum
# Enum = tool that helps us make a list of choices (like North, South, East, West)

from typing import List, Tuple
# typing = tool that helps us tell Python what kind of data we're using
# List = a list of things, Tuple = a pair or group of things that stick together

# Now we're making our own special list of directions the snake can move
# Think of this like the buttons on a game controller
class Direction(Enum):
    # Enum is like making a multiple choice question with 4 answers
    # Each direction has two numbers: (up/down movement, left/right movement)
    UP = (-1, 0)      # Go up 1 space, don't move left/right
    DOWN = (1, 0)     # Go down 1 space, don't move left/right  
    LEFT = (0, -1)    # Don't move up/down, go left 1 space
    RIGHT = (0, 1)    # Don't move up/down, go right 1 space

# This is our main game class - think of it like a blueprint for building our game
# A class is like a cookie cutter - it defines the shape, and we can make cookies (objects) from it
class SnakeGame:
    # This is the __init__ function - it's like the "setup" instructions when we start a new game
    # It runs automatically when we create a new SnakeGame
    def __init__(self, stdscr):
        # stdscr is the terminal screen - think of it like our drawing canvas
        
        # self means "this particular game" - like saying "MY game" vs someone else's game
        self.stdscr = stdscr              # Save our drawing canvas so we can use it later
        self.score = 0                    # Start with 0 points (like starting a video game)
        self.high_score = 0              # Keep track of the best score ever
        
        # Get the size of our drawing canvas (how big is the terminal window?)
        self.height, self.width = stdscr.getmaxyx()
        # This is like asking "How tall and wide is my piece of paper?"
        
        # Calculate how much space we have for the actual game
        # We need to save some space for showing the score and drawing borders
        self.game_height = self.height - 4  # Take away 4 lines for score and instructions
        self.game_width = self.width - 2    # Take away 2 columns for left and right borders
        
        # Start up the game for the first time
        self.reset_game()  # This will set up our snake and food
        
        # Set up the terminal to work the way we want for our game
        curses.curs_set(0)    # Hide the blinking cursor (we don't want to see it during the game)
        stdscr.nodelay(1)     # Don't wait for someone to press a key (keep the game moving)
        stdscr.timeout(100)   # Wait 100 milliseconds between each game update (controls game speed)
        
        # Set up pretty colors for our game (if the terminal can show colors)
        if curses.has_colors():  # Ask: "Can this terminal show colors?"
            curses.start_color()  # Tell the terminal: "Get ready to show colors!"
            
            # Create color pairs - think of these like different colored crayons
            # Each number is a "crayon ID" and we tell it what colors to use
            curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Green snake on black background
            curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)    # Red food on black background  
            curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Yellow score text on black background
            curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)   # Cyan borders on black background
        
    # This function resets everything back to the beginning - like starting a new game
    def reset_game(self):
        """Reset the game to initial state"""
        # Figure out where to put the snake at the start (in the middle of the screen)
        start_y = self.game_height // 2  # // means "divide and round down" - put snake halfway down
        start_x = self.game_width // 2   # Put snake halfway across
        
        # Create our snake - it's a list of body parts (each part has a row and column position)
        # We start with 3 pieces: head, body, tail (all in a horizontal line)
        self.snake = [
            (start_y, start_x),      # Head position
            (start_y, start_x - 1),  # Body position (1 space to the left of head)
            (start_y, start_x - 2)   # Tail position (2 spaces to the left of head)
        ]
        
        self.direction = Direction.RIGHT  # Snake starts moving to the right
        self.food = self.generate_food()  # Put food somewhere random on the screen
        self.game_over = False           # Game is not over yet
        self.score = 0                   # Reset score back to 0
        
    # This function puts food in a random spot where the snake isn't
    def generate_food(self) -> Tuple[int, int]:
        """Generate food at a random position not occupied by the snake"""
        # Keep trying random positions until we find one that's not on the snake
        while True:  # This is an "infinite loop" - keep doing this forever until we say "break"
            # Pick a random row (between 1 and game_height-1 so it's not on the border)
            food_y = random.randint(1, self.game_height - 1)
            # Pick a random column (between 1 and game_width-1 so it's not on the border)  
            food_x = random.randint(1, self.game_width - 1)
            
            # Check if this position is already occupied by the snake
            if (food_y, food_x) not in self.snake:  # If this spot is NOT part of the snake
                return (food_y, food_x)  # Great! Use this spot and exit the function
            # If this spot IS part of the snake, the loop continues and tries again
    
    # This function checks what key the player pressed and decides what to do
    def handle_input(self):
        """Handle keyboard input"""
        key = self.stdscr.getch()  # Get the key that was pressed (or -1 if no key was pressed)
        
        # Check if player wants to quit the game
        if key == ord('q') or key == ord('Q'):  # ord() converts a letter to its number code
            return False  # Return False means "stop the game"
            
        # Check if player wants to restart the game (only works when game is over)
        elif key == ord('r') or key == ord('R'):
            if self.game_over:  # Only restart if the game is actually over
                self.reset_game()  # Start a brand new game
                
        # Handle movement keys (only if the game is still running)
        elif not self.game_over:  # "not" means "if game is NOT over"
            
            # Check for UP movement (arrow key or W key)
            if key == curses.KEY_UP or key == ord('w') or key == ord('W'):
                # Don't let snake immediately reverse into itself
                if self.direction != Direction.DOWN:  # If we're not already going down
                    self.direction = Direction.UP     # Change direction to up
                    
            # Check for DOWN movement (arrow key or S key)
            elif key == curses.KEY_DOWN or key == ord('s') or key == ord('S'):
                if self.direction != Direction.UP:   # If we're not already going up
                    self.direction = Direction.DOWN  # Change direction to down
                    
            # Check for LEFT movement (arrow key or A key)
            elif key == curses.KEY_LEFT or key == ord('a') or key == ord('A'):
                if self.direction != Direction.RIGHT:  # If we're not already going right
                    self.direction = Direction.LEFT    # Change direction to left
                    
            # Check for RIGHT movement (arrow key or D key)
            elif key == curses.KEY_RIGHT or key == ord('d') or key == ord('D'):
                if self.direction != Direction.LEFT:   # If we're not already going left
                    self.direction = Direction.RIGHT   # Change direction to right
        
        return True  # Return True means "keep the game running"
    
    # This function moves the snake and checks if anything bad happened (like hitting a wall)
    def update_snake(self):
        """Update snake position and check for collisions"""
        # If the game is over, don't do anything
        if self.game_over:
            return  # Exit this function early
            
        # Get the current position of the snake's head (the first item in our snake list)
        head_y, head_x = self.snake[0]  # This breaks the tuple into two separate numbers
        
        # Figure out where the head will move next based on the current direction
        dy, dx = self.direction.value  # Get the movement numbers from our Direction enum
        # dy = how much to move up/down, dx = how much to move left/right
        
        new_head = (head_y + dy, head_x + dx)  # Calculate the new head position
        
        # Check if the snake hit a wall (this is bad!)
        if (new_head[0] <= 0 or new_head[0] >= self.game_height or  # Hit top or bottom wall
            new_head[1] <= 0 or new_head[1] >= self.game_width):    # Hit left or right wall
            
            self.game_over = True  # Game over!
            # Check if this score is better than our best score
            if self.score > self.high_score:
                self.high_score = self.score  # Save the new high score
            return  # Exit the function - game is over
        
        # Check if the snake ran into itself (this is also bad!)
        if new_head in self.snake:  # If the new head position is already part of the snake body
            self.game_over = True   # Game over!
            if self.score > self.high_score:
                self.high_score = self.score
            return  # Exit the function - game is over
        
        # If we made it here, the move is safe! Add the new head to the front of the snake
        self.snake.insert(0, new_head)  # insert(0, ...) means "add to the beginning of the list"
        
        # Check if the snake ate the food (this is good!)
        if new_head == self.food:  # If the new head position is the same as the food position
            self.score += 10       # Add 10 points to the score
            self.food = self.generate_food()  # Put new food somewhere else
            
            # Make the game a little bit faster as the player gets better
            new_timeout = max(50, 100 - (self.score // 50))  # Calculate new speed
            # max() means "pick the bigger number" - we don't want it to get TOO fast
            self.stdscr.timeout(new_timeout)  # Update the game speed
            
            # NOTE: We don't remove the tail when food is eaten, so the snake grows longer!
            
        else:
            # The snake didn't eat food, so remove the tail to keep the same length
            self.snake.pop()  # pop() removes the last item from the list (the tail)
    
    # This function draws the border around our game area
    def draw_border(self):
        """Draw game border"""
        # If the terminal supports colors, use the cyan color we set up earlier
        if curses.has_colors():
            self.stdscr.attron(curses.color_pair(4))  # Turn on color pair #4 (cyan)
        
        # Draw the top and bottom horizontal lines
        for x in range(self.width - 1):  # Go from left edge to right edge
            self.stdscr.addch(0, x, '═')                      # Top border
            self.stdscr.addch(self.game_height + 1, x, '═')   # Bottom border
        
        # Draw the left and right vertical lines  
        for y in range(self.game_height + 2):  # Go from top to bottom
            self.stdscr.addch(y, 0, '║')                      # Left border
            self.stdscr.addch(y, self.game_width + 1, '║')    # Right border
        
        # Draw the four corner pieces to make it look nice
        self.stdscr.addch(0, 0, '╔')                                          # Top-left corner
        self.stdscr.addch(0, self.game_width + 1, '╗')                        # Top-right corner
        self.stdscr.addch(self.game_height + 1, 0, '╚')                       # Bottom-left corner
        self.stdscr.addch(self.game_height + 1, self.game_width + 1, '╝')     # Bottom-right corner
        
        # Turn off the color when we're done drawing the border
        if curses.has_colors():
            self.stdscr.attroff(curses.color_pair(4))  # Turn off color pair #4
    
    # This function draws the snake on the screen
    def draw_snake(self):
        """Draw the snake"""
        # If colors work, use green color for the snake
        if curses.has_colors():
            self.stdscr.attron(curses.color_pair(1))  # Turn on color pair #1 (green)
        
        # Go through each piece of the snake and draw it
        for i, (y, x) in enumerate(self.snake):  # enumerate gives us both the position number and the coordinates
            if i == 0:  # If this is the first piece (index 0), it's the head
                self.stdscr.addch(y, x, '◉')  # Draw the head with a special character
            else:       # If this is any other piece, it's part of the body
                self.stdscr.addch(y, x, '●')  # Draw body pieces with a different character
        
        # Turn off green color when done drawing the snake
        if curses.has_colors():
            self.stdscr.attroff(curses.color_pair(1))
    
    # This function draws the food on the screen
    def draw_food(self):
        """Draw the food"""
        # If colors work, use red color for the food
        if curses.has_colors():
            self.stdscr.attron(curses.color_pair(2))  # Turn on color pair #2 (red)
        
        # Get the food's position and draw it
        y, x = self.food  # Break the food position tuple into row and column
        self.stdscr.addch(y, x, '◆')  # Draw the food with a diamond character
        
        # Turn off red color when done
        if curses.has_colors():
            self.stdscr.attroff(curses.color_pair(2))
    
    # This function draws the score and game information at the bottom of the screen
    def draw_score(self):
        """Draw score and game information"""
        # If colors work, use yellow color for the text
        if curses.has_colors():
            self.stdscr.attron(curses.color_pair(3))  # Turn on color pair #3 (yellow)
        
        # Show the current score
        score_text = f"Score: {self.score}"  # f"..." is a "format string" - it puts the score number into the text
        self.stdscr.addstr(self.game_height + 2, 2, score_text)  # addstr() writes a whole string at once
        
        # Show the high score
        high_score_text = f"High Score: {self.high_score}"
        self.stdscr.addstr(self.game_height + 2, 20, high_score_text)
        
        # Show different messages depending on whether the game is over or not
        if self.game_over:
            # Game over message
            game_over_text = "GAME OVER! Press 'R' to restart, 'Q' to quit"
            # Center the message on the screen
            x = (self.width - len(game_over_text)) // 2  # Calculate where to start writing to center it
            self.stdscr.addstr(self.game_height + 3, x, game_over_text)
        else:
            # Instructions for playing
            instructions = "Use Arrow Keys or WASD to move, Q to quit"
            x = max(0, (self.width - len(instructions)) // 2)  # Center it, but don't go past the left edge
            self.stdscr.addstr(self.game_height + 3, x, instructions)
        
        # Turn off yellow color when done
        if curses.has_colors():
            self.stdscr.attroff(curses.color_pair(3))
    
    # This function draws everything on the screen
    def draw_game(self):
        """Draw the entire game"""
        self.stdscr.clear()  # Clear the screen (erase everything that was drawn before)
        
        # Draw all the different parts of the game
        self.draw_border()  # Draw the border first (so it's in the background)
        self.draw_snake()   # Draw the snake
        self.draw_food()    # Draw the food  
        self.draw_score()   # Draw the score and text
        
        self.stdscr.refresh()  # Actually show everything on the screen (like pressing "print")
    
    # This is the main game loop - it keeps running until the player quits
    def run(self):
        """Main game loop"""
        while True:  # Keep doing this forever (until we break out of the loop)
            # Check what keys the player pressed
            if not self.handle_input():  # handle_input() returns False if player wants to quit
                break  # Exit the while loop (and end the game)
            
            # Move the snake and check for collisions
            self.update_snake()
            
            # Draw everything on the screen
            self.draw_game()
            
            # Wait a tiny bit before doing it all again (makes the animation smooth)
            time.sleep(0.01)  # Sleep for 0.01 seconds (10 milliseconds)

# This function sets up everything and starts the game
def main():
    """Main function to initialize and run the game"""
    try:  # "try" means "attempt to do this, but be ready in case something goes wrong"
        
        # Check if the terminal window is big enough for our game
        import os  # Import the os tool to check terminal size
        size = os.get_terminal_size()  # Ask: "How big is the terminal window?"
        
        if size.columns < 40 or size.lines < 10:  # If the window is too small
            print("Terminal window too small! Please resize to at least 40x10 characters.")
            return  # Exit the function early
        
        # Start the game using curses
        # curses.wrapper() sets up the terminal properly and cleans up when we're done
        curses.wrapper(lambda stdscr: SnakeGame(stdscr).run())
        # This line is like saying: "Set up the screen, create a new SnakeGame, and run it"
        
    except KeyboardInterrupt:  # If the player presses Ctrl+C to force quit
        print("\nGame interrupted. Thanks for playing!")
        
    except Exception as e:  # If any other error happens
        print(f"An error occurred: {e}")
        print("Make sure your terminal supports curses and has adequate size.")

# This is the very beginning of our program
# It only runs if someone runs this file directly (not if it's imported by another file)
if __name__ == "__main__":
    print("🐍 Welcome to Terminal Snake Game! 🐍")  # Show a welcome message
    print("Loading game...")
    time.sleep(1)  # Wait 1 second to build suspense
    main()         # Start the main function, which starts the game
