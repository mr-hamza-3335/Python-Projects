import pygame
import random
import sys
import os

# Initialize pygame
pygame.init()

# Ensure assets path works correctly
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# Load Sounds
try:
    pygame.mixer.music.load(os.path.join(ASSETS_DIR, "background_music.wav"))  # Background music
    pygame.mixer.music.set_volume(0.5)
    game_over_sound = pygame.mixer.Sound(os.path.join(ASSETS_DIR, "game_over.wav"))
except pygame.error:
    print("Error: Sound files missing. Please check 'assets' folder.")
    sys.exit()

# Game Constants
WIDTH, HEIGHT = 300, 600
GRID_SIZE = 30
COLS, ROWS = WIDTH // GRID_SIZE, HEIGHT // GRID_SIZE
WHITE, BLACK, RED, GREEN, BLUE = (255, 255, 255), (0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255)
SPEED = 500  # Milliseconds per move
FONT = pygame.font.Font(None, 36)
SMALL_FONT = pygame.font.Font(None, 20)  # Slightly larger font for "Created by Hamza"

# Tetromino Shapes & Colors
SHAPES = [
    [[1, 1, 1, 1]],  # I Shape
    [[1, 1], [1, 1]],  # O Shape
    [[0, 1, 0], [1, 1, 1]],  # T Shape
    [[1, 0, 0], [1, 1, 1]],  # L Shape
    [[0, 0, 1], [1, 1, 1]],  # J Shape
    [[0, 1, 1], [1, 1, 0]],  # S Shape
    [[1, 1, 0], [0, 1, 1]],  # Z Shape
]
COLORS = [RED, GREEN, BLUE, (255, 165, 0), (128, 0, 128), (0, 255, 255), (255, 255, 0)]

grid = [[None for _ in range(COLS)] for _ in range(ROWS)]


def reset_game():
    global grid
    grid = [[None for _ in range(COLS)] for _ in range(ROWS)]
    main()


class Tetromino:
    def __init__(self, shape, color):
        self.shape = shape
        self.color = color
        self.x, self.y = COLS // 2 - len(shape[0]) // 2, 0
        self.locked = False

    def move(self, dx, dy):
        if not self.locked and not check_collision(self, dx, dy):
            self.x += dx
            self.y += dy

    def rotate(self):
        if not self.locked:
            rotated_shape = [list(row) for row in zip(*self.shape[::-1])]
            original_x = self.x
            self.shape = rotated_shape
            if check_collision(self):
                self.x = original_x
                self.shape = [list(row) for row in zip(*self.shape[::-1])][::-1]  # Revert rotation


def check_collision(piece, dx=0, dy=0):
    for i, row in enumerate(piece.shape):
        for j, cell in enumerate(row):
            if cell:
                new_x, new_y = piece.x + j + dx, piece.y + i + dy
                if new_x < 0 or new_x >= COLS or new_y >= ROWS or (new_y >= 0 and grid[new_y][new_x]):
                    return True
    return False


def draw_piece(piece):
    for i, row in enumerate(piece.shape):
        for j, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, piece.color, ((piece.x + j) * GRID_SIZE, (piece.y + i) * GRID_SIZE, GRID_SIZE, GRID_SIZE), border_radius=5)
                pygame.draw.rect(screen, BLACK, ((piece.x + j) * GRID_SIZE, (piece.y + i) * GRID_SIZE, GRID_SIZE, GRID_SIZE), 2, border_radius=5)


def lock_piece(piece):
    for i, row in enumerate(piece.shape):
        for j, cell in enumerate(row):
            if cell:
                grid[piece.y + i][piece.x + j] = piece.color
    return Tetromino(random.choice(SHAPES), random.choice(COLORS))


def draw_grid():
    for y in range(ROWS):
        for x in range(COLS):
            if grid[y][x]:
                pygame.draw.rect(screen, grid[y][x], (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE), border_radius=5)
                pygame.draw.rect(screen, BLACK, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE), 2, border_radius=5)


def check_game_over():
    for x in range(COLS):
        if grid[0][x]:
            return True
    return False


def game_over_screen():
    pygame.mixer.music.stop()  # Stop background music
    game_over_sound.play()  # Play game over sound
    screen.fill(BLACK)
    text = FONT.render("Game Over", True, WHITE)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text, text_rect)

    pygame.display.flip()
    pygame.time.delay(2000)

    restart_text = FONT.render("Press R to Restart", True, WHITE)
    restart_text_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
    screen.blit(restart_text, restart_text_rect)
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                waiting = False
                reset_game()


def main():
    global last_move
    pygame.mixer.music.play(-1)  # Start background music
    piece = Tetromino(random.choice(SHAPES), random.choice(COLORS))
    running = True
    last_move = pygame.time.get_ticks()

    while running:
        screen.fill(BLACK)
        draw_grid()
        draw_piece(piece)
        screen.blit(creator_text, creator_text_rect)  # Draw "Created by Hamza"

        if check_game_over():
            game_over_screen()
            return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and not piece.locked:
                if event.key == pygame.K_LEFT:
                    piece.move(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    piece.move(1, 0)
                elif event.key == pygame.K_DOWN:
                    piece.move(0, 1)
                elif event.key == pygame.K_UP:
                    piece.rotate()

        if pygame.time.get_ticks() - last_move > SPEED:
            if not check_collision(piece, 0, 1):
                piece.move(0, 1)
            else:
                piece.locked = True
                piece = lock_piece(piece)
            last_move = pygame.time.get_ticks()

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    
    creator_text = SMALL_FONT.render("Created by Hamza", True, WHITE)
    creator_text_rect = creator_text.get_rect(topleft=(5, 5))  # Move to top left corner

    main()
