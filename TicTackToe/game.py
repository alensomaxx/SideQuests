import pygame as pg
import sys
import time

class Game:
    def __init__(self):
        # --- Constants ---
        self.WIDTH = 400
        self.HEIGHT = 500 # Extra 100px for status bar
        self.LINE_WIDTH = 15
        self.BOARD_ROWS = 3
        self.BOARD_COLS = 3
        self.SQUARE_SIZE = self.WIDTH // self.BOARD_COLS
        self.CIRCLE_RADIUS = self.SQUARE_SIZE // 3
        self.CIRCLE_WIDTH = 15
        self.CROSS_WIDTH = 25
        
        # --- Colors ---
        self.BG_COLOR = (28, 170, 156)
        self.LINE_COLOR = (23, 145, 135)
        self.CIRCLE_COLOR = (239, 231, 200)
        self.CROSS_COLOR = (66, 66, 66)
        self.STATUS_BG_COLOR = (0, 0, 0)
        self.TEXT_COLOR = (255, 255, 255)
        self.WIN_LINE_COLOR = (255, 0, 0)

        # --- Pygame Setup ---
        pg.init()
        self.screen = pg.display.set_mode((self.WIDTH, self.HEIGHT))
        pg.display.set_caption('Tic Tac Toe')
        self.font = pg.font.Font(None, 40)
        self.clock = pg.time.Clock()
        
        # --- Game Variables ---
        self.reset_game()

    def reset_game(self):
        """ Resets the game to its initial state. """
        self.board = [[None] * self.BOARD_COLS for _ in range(self.BOARD_ROWS)]
        self.turn = 'X'
        self.winner = None
        self.draw = False
        self.win_line = None

    def draw_lines(self):
        """ Draws the grid lines for the board. """
        self.screen.fill(self.BG_COLOR)
        # Horizontal
        pg.draw.line(self.screen, self.LINE_COLOR, (0, self.SQUARE_SIZE), (self.WIDTH, self.SQUARE_SIZE), self.LINE_WIDTH)
        pg.draw.line(self.screen, self.LINE_COLOR, (0, 2 * self.SQUARE_SIZE), (self.WIDTH, 2 * self.SQUARE_SIZE), self.LINE_WIDTH)
        # Vertical
        pg.draw.line(self.screen, self.LINE_COLOR, (self.SQUARE_SIZE, 0), (self.SQUARE_SIZE, self.WIDTH), self.LINE_WIDTH)
        pg.draw.line(self.screen, self.LINE_COLOR, (2 * self.SQUARE_SIZE, 0), (2 * self.SQUARE_SIZE, self.WIDTH), self.LINE_WIDTH)

    def draw_figures(self):
        """ Draws the X's and O's on the board. """
        for row in range(self.BOARD_ROWS):
            for col in range(self.BOARD_COLS):
                if self.board[row][col] == 'O':
                    center = (int(col * self.SQUARE_SIZE + self.SQUARE_SIZE / 2), int(row * self.SQUARE_SIZE + self.SQUARE_SIZE / 2))
                    pg.draw.circle(self.screen, self.CIRCLE_COLOR, center, self.CIRCLE_RADIUS, self.CIRCLE_WIDTH)
                elif self.board[row][col] == 'X':
                    x_pos = col * self.SQUARE_SIZE
                    y_pos = row * self.SQUARE_SIZE
                    margin = self.SQUARE_SIZE // 4
                    pg.draw.line(self.screen, self.CROSS_COLOR, (x_pos + margin, y_pos + margin), (x_pos + self.SQUARE_SIZE - margin, y_pos + self.SQUARE_SIZE - margin), self.CROSS_WIDTH)
                    pg.draw.line(self.screen, self.CROSS_COLOR, (x_pos + margin, y_pos + self.SQUARE_SIZE - margin), (x_pos + self.SQUARE_SIZE - margin, y_pos + margin), self.CROSS_WIDTH)

    def make_move(self, row, col):
        """ Marks a square on the board for the current player. """
        if self.board[row][col] is None and self.winner is None:
            self.board[row][col] = self.turn
            self.turn = 'O' if self.turn == 'X' else 'X'
            self.check_win()

    def check_win(self):
        """ Checks for a win or a draw. """
        # Check rows
        for row in range(self.BOARD_ROWS):
            if self.board[row][0] == self.board[row][1] == self.board[row][2] and self.board[row][0] is not None:
                self.winner = self.board[row][0]
                y = row * self.SQUARE_SIZE + self.SQUARE_SIZE / 2
                self.win_line = ((0, y), (self.WIDTH, y))
                return

        # Check columns
        for col in range(self.BOARD_COLS):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] and self.board[0][col] is not None:
                self.winner = self.board[0][col]
                x = col * self.SQUARE_SIZE + self.SQUARE_SIZE / 2
                self.win_line = ((x, 0), (x, self.WIDTH))
                return

        # Check diagonals
        if self.board[0][0] == self.board[1][1] == self.board[2][2] and self.board[0][0] is not None:
            self.winner = self.board[0][0]
            self.win_line = ((self.SQUARE_SIZE / 4, self.SQUARE_SIZE / 4), (self.WIDTH - self.SQUARE_SIZE / 4, self.WIDTH - self.SQUARE_SIZE / 4))
            return
        if self.board[0][2] == self.board[1][1] == self.board[2][0] and self.board[0][2] is not None:
            self.winner = self.board[0][2]
            self.win_line = ((self.SQUARE_SIZE / 4, self.WIDTH - self.SQUARE_SIZE / 4), (self.WIDTH - self.SQUARE_SIZE / 4, self.SQUARE_SIZE / 4))
            return
            
        # Check for a draw
        if all(all(cell is not None for cell in row) for row in self.board) and self.winner is None:
            self.draw = True

    def draw_status(self):
        """ Displays the game status (Turn, Winner, or Draw). """
        if self.winner:
            message = f"{self.winner} has won!"
        elif self.draw:
            message = "It's a Draw!"
        else:
            message = f"{self.turn}'s Turn"

        text = self.font.render(message, True, self.TEXT_COLOR)
        text_rect = text.get_rect(center=(self.WIDTH / 2, self.HEIGHT - 50))
        
        # Draw a black rectangle for the status bar background
        pg.draw.rect(self.screen, self.STATUS_BG_COLOR, (0, self.WIDTH, self.WIDTH, 100))
        self.screen.blit(text, text_rect)

        if self.winner or self.draw:
            # Add a "Click to play again" message
            restart_text = self.font.render("Click to play again", True, self.TEXT_COLOR)
            restart_rect = restart_text.get_rect(center=(self.WIDTH / 2, self.HEIGHT - 20))
            self.screen.blit(restart_text, restart_rect)


    def run(self):
        """ Main game loop. """
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == pg.MOUSEBUTTONDOWN:
                    if self.winner or self.draw:
                        time.sleep(0.5) # Brief pause before reset
                        self.reset_game()
                    else:
                        mouseX, mouseY = event.pos
                        if mouseY < self.WIDTH: # Ensure click is on the board
                            clicked_row = int(mouseY // self.SQUARE_SIZE)
                            clicked_col = int(mouseX // self.SQUARE_SIZE)
                            self.make_move(clicked_row, clicked_col)
            
            self.draw_lines()
            self.draw_figures()
            if self.winner and self.win_line:
                 pg.draw.line(self.screen, self.WIN_LINE_COLOR, self.win_line[0], self.win_line[1], self.LINE_WIDTH)
            self.draw_status()
            
            pg.display.update()
            self.clock.tick(30)

if __name__ == '__main__':
    game = Game()
    game.run()