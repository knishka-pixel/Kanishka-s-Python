import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 150, 0)
RED = (255, 0, 0)
BLUE = (0, 120, 255)
BLACK = (0, 0, 0)
GRAY = (40, 40, 40)
YELLOW = (255, 255, 0)

# Screen dimensions
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 600
GRID_SIZE = 20  # Size of each grid square

# Calculate grid dimensions
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Create game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Kanishka's Python")

# Game clock
clock = pygame.time.Clock()

# Fonts
font_large = pygame.font.SysFont('Arial', 50, bold=True)
font_medium = pygame.font.SysFont('Arial', 36, bold=True)
font_small = pygame.font.SysFont('Arial', 24)

class Snake:
    def __init__(self):
        self.reset()
    
    def reset(self):
        # Start in the middle of the screen
        self.length = 3
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        # Create initial body
        for i in range(1, self.length):
            self.positions.append((self.positions[0][0] - i, self.positions[0][1]))
        
        self.direction = (1, 0)  # Start moving right
        self.score = 0
        self.speed = 8  # Initial speed
        self.grow_pending = 0
        self.alive = True
    
    def get_head_position(self):
        return self.positions[0]
    
    def turn(self, point):
        # Prevent 180-degree turns (can't go directly opposite)
        if (point[0] * -1, point[1] * -1) == self.direction:
            return
        self.direction = point
    
    def move(self):
        if not self.alive:
            return
        
        head = self.get_head_position()
        new_x = (head[0] + self.direction[0]) % GRID_WIDTH
        new_y = (head[1] + self.direction[1]) % GRID_HEIGHT
        new_position = (new_x, new_y)
        
        # Check for collision with self
        if new_position in self.positions[1:]:
            self.alive = False
            return
        
        # Add new head position
        self.positions.insert(0, new_position)
        
        # Grow if needed
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            # Remove tail if not growing
            self.positions.pop()
    
    def grow(self):
        self.grow_pending += 1
        self.length += 1
    
    def draw(self, surface):
        for i, pos in enumerate(self.positions):
            # Convert grid position to pixel coordinates
            rect = pygame.Rect(pos[0] * GRID_SIZE, pos[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            
            # Draw snake segment with gradient from head to tail
            if i == 0:  # Head
                pygame.draw.rect(surface, GREEN, rect)
                pygame.draw.rect(surface, DARK_GREEN, rect, 1)
                
                # Draw eyes on the head
                eye_size = GRID_SIZE // 5
                # Determine eye positions based on direction
                if self.direction == (1, 0):  # Right
                    pygame.draw.circle(surface, BLACK, (rect.right - eye_size, rect.top + eye_size * 2), eye_size)
                    pygame.draw.circle(surface, BLACK, (rect.right - eye_size, rect.bottom - eye_size * 2), eye_size)
                elif self.direction == (-1, 0):  # Left
                    pygame.draw.circle(surface, BLACK, (rect.left + eye_size, rect.top + eye_size * 2), eye_size)
                    pygame.draw.circle(surface, BLACK, (rect.left + eye_size, rect.bottom - eye_size * 2), eye_size)
                elif self.direction == (0, 1):  # Down
                    pygame.draw.circle(surface, BLACK, (rect.left + eye_size * 2, rect.bottom - eye_size), eye_size)
                    pygame.draw.circle(surface, BLACK, (rect.right - eye_size * 2, rect.bottom - eye_size), eye_size)
                elif self.direction == (0, -1):  # Up
                    pygame.draw.circle(surface, BLACK, (rect.left + eye_size * 2, rect.top + eye_size), eye_size)
                    pygame.draw.circle(surface, BLACK, (rect.right - eye_size * 2, rect.top + eye_size), eye_size)
            else:  # Body
                # Color gradient from head to tail
                color_factor = max(0.3, 1.0 - (i / self.length) * 0.7)
                body_color = (
                    int(GREEN[0] * color_factor),
                    int(GREEN[1] * color_factor),
                    int(GREEN[2] * color_factor)
                )
                pygame.draw.rect(surface, body_color, rect)
                pygame.draw.rect(surface, DARK_GREEN, rect, 1)

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.color = RED
        self.randomize_position()
    
    def randomize_position(self):
        self.position = (random.randint(0, GRID_WIDTH - 1), 
                         random.randint(0, GRID_HEIGHT - 1))
    
    def draw(self, surface):
        rect = pygame.Rect(
            self.position[0] * GRID_SIZE,
            self.position[1] * GRID_SIZE,
            GRID_SIZE, GRID_SIZE
        )
        
        # Draw food with a shine effect
        pygame.draw.rect(surface, self.color, rect)
        pygame.draw.rect(surface, YELLOW, rect, 1)
        
        # Draw a small shine effect
        shine_rect = pygame.Rect(
            self.position[0] * GRID_SIZE + GRID_SIZE // 4,
            self.position[1] * GRID_SIZE + GRID_SIZE // 4,
            GRID_SIZE // 4, GRID_SIZE // 4
        )
        pygame.draw.ellipse(surface, (255, 200, 200), shine_rect)

class Game:
    def __init__(self):
        self.snake = Snake()
        self.food = Food()
        self.game_over = False
        self.speed_increase = 1.0  # How much speed increases per food
    
    def update(self):
        if not self.game_over:
            self.snake.move()
            
            # Check if snake ate the food
            if self.snake.get_head_position() == self.food.position:
                self.snake.grow()
                self.snake.score += 1
                self.snake.speed += self.speed_increase  # Increase speed
                
                # Ensure food doesn't spawn on snake
                while True:
                    self.food.randomize_position()
                    if self.food.position not in self.snake.positions:
                        break
            
            # Check if snake hit itself
            if not self.snake.alive:
                self.game_over = True
    
    def draw(self, surface):
        # Draw grid background
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            pygame.draw.line(surface, GRAY, (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            pygame.draw.line(surface, GRAY, (0, y), (SCREEN_WIDTH, y), 1)
        
        # Draw game elements
        self.food.draw(surface)
        self.snake.draw(surface)
        
        # Draw score
        score_text = font_medium.render(f"Score: {self.snake.score}", True, BLUE)
        surface.blit(score_text, (10, 10))
        
        # Draw length
        length_text = font_medium.render(f"Length: {self.snake.length}", True, GREEN)
        surface.blit(length_text, (10, 50))
        
        # Draw speed
        speed_text = font_medium.render(f"Speed: {self.snake.speed:.1f}", True, RED)
        surface.blit(speed_text, (10, 90))
        
        # Draw game over message
        if self.game_over:
            # Semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            surface.blit(overlay, (0, 0))
            
            game_over_text = font_large.render("GAME OVER", True, RED)
            score_text = font_medium.render(f"Final Score: {self.snake.score}", True, YELLOW)
            restart_text = font_small.render("Press SPACE to restart or ESC to quit", True, WHITE)
            
            surface.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 
                                         SCREEN_HEIGHT // 2 - 80))
            surface.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 
                                     SCREEN_HEIGHT // 2 - 10))
            surface.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 
                                       SCREEN_HEIGHT // 2 + 50))
    
    def reset(self):
        self.snake.reset()
        self.game_over = False
        self.food.randomize_position()
        
        # Ensure food doesn't spawn on snake
        while self.food.position in self.snake.positions:
            self.food.randomize_position()

def draw_title_screen():
    screen.fill(BLACK)
    
    # Draw title - "Kanishka's Python" on screen
    title_text = font_large.render("Kanishka's Python", True, GREEN)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 80))
    
    # Draw instructions
    instructions = [
        "Use ARROW KEYS to move the snake",
        "Eat the red food to grow and increase speed",
        "Avoid hitting yourself",
        "The game gets faster as you eat more!",
        "",
        "Press SPACE to start the game",
        "Press ESC to quit"
    ]
    
    for i, line in enumerate(instructions):
        text = font_small.render(line, True, WHITE)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 200 + i * 40))
    
    pygame.display.update()

def main():
    game = Game()
    in_title_screen = True
    
    # Main game loop
    while True:
        # Title screen loop
        while in_title_screen:
            draw_title_screen()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        in_title_screen = False
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
            
            clock.tick(30)
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if game.game_over:
                    if event.key == pygame.K_SPACE:
                        game.reset()
                    elif event.key == pygame.K_ESCAPE:
                        in_title_screen = True
                else:
                    # Handle directional controls
                    if event.key == pygame.K_RIGHT:
                        game.snake.turn((1, 0))
                    elif event.key == pygame.K_LEFT:
                        game.snake.turn((-1, 0))
                    elif event.key == pygame.K_UP:
                        game.snake.turn((0, -1))
                    elif event.key == pygame.K_DOWN:
                        game.snake.turn((0, 1))
                    elif event.key == pygame.K_ESCAPE:
                        in_title_screen = True
        
        # Update game state
        game.update()
        
        # Draw everything
        screen.fill(BLACK)
        game.draw(screen)
        pygame.display.update()
        
        # Control game speed
        clock.tick(game.snake.speed)

if __name__ == "__main__":
    main()