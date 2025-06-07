```python
import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 600
CELL_SIZE = 30
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
PINK = (255, 105, 180)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
BLUE = (0, 0, 255)
YELLOW = (255,255,0)

# Maze representation (0 = empty, 1 = wall)
maze = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]


# Game classes
class PacMan:
    def __init__(self):
        self.x = 1
        self.y = 1
        self.direction = "right"
        self.score = 0
        self.lives = 3

    def move(self, dx, dy):
        new_x = self.x + dx
        new_y = self.y + dy
        if 0 <= new_x < len(maze[0]) and 0 <= new_y < len(maze) and maze[new_y][new_x] == 0:
            self.x = new_x
            self.y = new_y

    def draw(self, screen):
        pygame.draw.circle(screen, YELLOW, (self.x * CELL_SIZE + CELL_SIZE // 2, self.y * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 2)


class Ghost:
    def __init__(self, color, x, y):
        self.x = x
        self.y = y
        self.color = color
        self.frightened = False
        self.frightened_timer = 0

    def move(self):
        # Simple AI for Blinky (moves towards Pac-Man)
        if not self.frightened:
            dx, dy = 0, 0
            if pacman.x > self.x:
                dx = 1
            elif pacman.x < self.x:
                dx = -1
            if pacman.y > self.y:
                dy = 1
            elif pacman.y < self.y:
                dy = -1
            self.move_safe(dx, dy)

    def move_safe(self, dx, dy):
        new_x = self.x + dx
        new_y = self.y + dy
        if 0 <= new_x < len(maze[0]) and 0 <= new_y < len(maze) and maze[new_y][new_x] == 0:
            self.x = new_x
            self.y = new_y

    def draw(self, screen):
        color = BLUE if self.frightened else self.color
        pygame.draw.rect(screen, color, (self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE))


# Game initialization
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pac-Man")
clock = pygame.time.Clock()

pacman = PacMan()
ghosts = [
    Ghost(RED, 10, 10),
    Ghost(PINK, 10, 12),
    Ghost(CYAN, 12, 10),
    Ghost(ORANGE, 12, 12),
]

pellets = []
power_pellets = [(0, 0), (0, len(maze) -1), (len(maze[0])-1, 0), (len(maze[0])-1, len(maze)-1)] #Four corners

for y in range(len(maze)):
    for x in range(len(maze[0])):
        if maze[y][x] == 0:
            pellets.append((x, y))


# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        pacman.move(-1, 0)
    if keys[pygame.K_RIGHT]:
        pacman.move(1, 0)
    if keys[pygame.K_UP]:
        pacman.move(0, -1)
    if keys[pygame.K_DOWN]:
        pacman.move(0, 1)


    #Ghost Movement
    for ghost in ghosts:
        ghost.move()

    #Collision Detection (simplified)
    for ghost in ghosts:
        if not ghost.frightened and pacman.x == ghost.x and pacman.y == ghost.y:
            pacman.lives -= 1
            if pacman.lives == 0:
                running = False

    #Pellet and Power Pellet Consumption
    for i in range(len(pellets) - 1, -1, -1):
        pellet_x, pellet_y = pellets[i]
        if pacman.x == pellet_x and pacman.y == pellet_y:
            pacman.score += 10
            del pellets[i]

    for i in range(len(power_pellets) - 1, -1, -1):
        pellet_x, pellet_y = power_pellets[i]
        if pacman.x == pellet_x and pacman.y == pellet_y:
            pacman.score += 50
            del power_pellets[i]
            for ghost in ghosts:
                ghost.frightened = True
                ghost.frightened_timer = pygame.time.get_ticks()


    #Warp Tunnels
    if pacman.x == -1:
        pacman.x = len(maze[0]) -1
    if pacman.x == len(maze[0]):
        pacman.x = 0


    #Drawing
    screen.fill(BLACK)
    for y in range(len(maze)):
        for x in range(len(maze[0])):
            if maze[y][x] == 1:
                pygame.draw.rect(screen, WHITE, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    for pellet_x, pellet_y in pellets:
        pygame.draw.circle(screen, WHITE, (pellet_x * CELL_SIZE + CELL_SIZE // 2, pellet_y * CELL_SIZE + CELL_SIZE // 2), 3)
    for pellet_x, pellet_y in power_pellets:
        pygame.draw.circle(screen, WHITE, (pellet_x * CELL_SIZE + CELL_SIZE // 2, pellet_y * CELL_SIZE + CELL_SIZE // 2), 8)
    pacman.draw(screen)
    for ghost in ghosts:
        ghost.draw(screen)
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {pacman.score}", True, WHITE)
    lives_text = font.render(f"Lives: {pacman.lives}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (10, 50))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
```