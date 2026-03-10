import pygame
import sys
import os
import random

pygame.init()

# ---------------- Window ----------------
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Draw & Play - Upgrades Demo")
clock = pygame.time.Clock()

# ---------------- Colors ----------------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (50, 200, 50)
BLUE = (50, 50, 200)
YELLOW = (240, 200, 50)
RED = (200, 50, 50)
PURPLE = (200, 100, 200)
GOLD = (255, 215, 0)

# ---------------- Modes ----------------
DRAW_MODE = 0
GAME_MODE = 1
mode = DRAW_MODE

# ---------------- Drawing ----------------
drawing = False
brush_size = 5
character_surface = pygame.Surface((300, 300))
character_surface.fill(WHITE)

# ---------------- Player ----------------
player = None
player_rect = None
velocity_y = 0
gravity = 0.6
jump_strength = -14
move_speed = 5
max_jumps = 2
jump_count = 0
adms = False  # F8 infinite jump
hearts = 3

# ---------------- Camera ----------------
camera_y = 0

# ---------------- Platforms ----------------
platforms = []
PLATFORM_WIDTH = 120
PLATFORM_HEIGHT = 20
PLATFORM_GAP = 120

def generate_platform(y):
    x = random.randint(0, WIDTH - PLATFORM_WIDTH)
    return pygame.Rect(x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT)

for i in range(6):
    platforms.append(generate_platform(500 - i * PLATFORM_GAP))

# ---------------- Rescue platform ----------------
helper_platform = pygame.Rect(WIDTH//2 - 60, 500, 120, 20)
helper_speed_factor = 0.01
rescue_y_offset = 50

# ---------------- Upgrades ----------------
class Upgrade:
    def __init__(self, x, y, kind):
        self.rect = pygame.Rect(x, y, 30, 30)
        self.kind = kind
        if kind == "jump_strength":
            self.color = PURPLE
        elif kind == "triple_jump":
            self.color = GOLD

upgrades = []

def spawn_upgrade(platform):
    kind = random.choice(["jump_strength", "triple_jump"])
    x = platform.x + platform.width // 2 - 15
    y = platform.y - 30
    upgrades.append(Upgrade(x, y, kind))

# ---------------- Main Loop ----------------
while True:
    screen.fill(BLUE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # ---------------- DRAW MODE ----------------
        if mode == DRAW_MODE:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                drawing = True
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                drawing = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    pygame.image.save(character_surface, "my_character.png")
                if event.key == pygame.K_RETURN:
                    if os.path.exists("my_character.png"):
                        player = pygame.image.load("my_character.png").convert_alpha()
                        player = pygame.transform.scale(player, (60, 60))
                        player_rect = player.get_rect()
                        player_rect.center = (WIDTH // 2, 400)
                        mode = GAME_MODE

        # ---------------- GAME MODE INPUT ----------------
        elif mode == GAME_MODE:
            if event.type == pygame.KEYDOWN:
                # Toggle infinite jump
                if event.key == pygame.K_F8:
                    adms = not adms
                    print("Infinite Jump:", adms)
                # Jump
                if event.key == pygame.K_SPACE:
                    if adms:
                        velocity_y = jump_strength
                    elif jump_count < max_jumps:
                        velocity_y = jump_strength
                        jump_count += 1

    # ---------------- DRAW ----------------
    if mode == DRAW_MODE:
        if drawing:
            mouse_pos = pygame.mouse.get_pos()
            adjusted_pos = (mouse_pos[0] - 250, mouse_pos[1] - 150)
            pygame.draw.circle(character_surface, BLACK, adjusted_pos, brush_size)
        screen.blit(character_surface, (250, 150))

    # ---------------- GAME MODE ----------------
    elif mode == GAME_MODE:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            player_rect.x -= move_speed
        if keys[pygame.K_d]:
            player_rect.x += move_speed

        # Gravity
        velocity_y += gravity
        player_rect.y += velocity_y
        grounded = False

        # Collision with platforms
        for platform in platforms:
            if player_rect.colliderect(platform) and velocity_y > 0:
                player_rect.bottom = platform.top
                velocity_y = 0
                grounded = True

        # Reset jump count when grounded
        if grounded:
            jump_count = 0

        # ---------------- Solid rescue platform ----------------
        rescue_platform_y = camera_y + HEIGHT - rescue_y_offset
        helper_platform.top = rescue_platform_y
        helper_platform.centerx += (player_rect.centerx - helper_platform.centerx) * helper_speed_factor

        if player_rect.colliderect(helper_platform) and velocity_y > 0:
            player_rect.bottom = helper_platform.top
            velocity_y = 0
            jump_count = 0

        if player_rect.top > helper_platform.top + 50:
            hearts -= 1
            print("Player hit! Hearts left:", hearts)
            if hearts <= 0:
                print("Game Over!")
                pygame.quit()
                sys.exit()
            player_rect.bottom = helper_platform.top
            velocity_y = 0
            jump_count = 0

        # ---------------- CAMERA ----------------
        if player_rect.top < camera_y + HEIGHT // 3:
            camera_y = player_rect.top - HEIGHT // 3

        # ---------------- Platform generation ----------------
        highest_platform = min(platform.y for platform in platforms)
        while highest_platform > camera_y - HEIGHT:
            new_platform = generate_platform(highest_platform - PLATFORM_GAP)
            platforms.append(new_platform)
            # 20% chance to spawn upgrade
            if random.random() < 0.2:
                spawn_upgrade(new_platform)
            highest_platform = new_platform.y

        platforms = [p for p in platforms if p.y < camera_y + HEIGHT + 100]

        # ---------------- Upgrade collection ----------------
        for upgrade in upgrades[:]:
            if player_rect.colliderect(upgrade.rect):
                if upgrade.kind == "jump_strength":
                    jump_strength += -0.4
                elif upgrade.kind == "triple_jump":
                    max_jumps += 1
                upgrades.remove(upgrade)
        if max_jumps >= 5:
            max_jumps = 5
        # ---------------- DRAW ----------------
        for platform in platforms:
            pygame.draw.rect(screen, GREEN, (platform.x, platform.y - camera_y, PLATFORM_WIDTH, PLATFORM_HEIGHT))

        for upgrade in upgrades:
            pygame.draw.rect(screen, upgrade.color,
                             (upgrade.rect.x, upgrade.rect.y - camera_y, upgrade.rect.width, upgrade.rect.height))

        pygame.draw.rect(screen, YELLOW,
                         (helper_platform.x, helper_platform.y - camera_y, helper_platform.width,
                          helper_platform.height))

        screen.blit(player, (player_rect.x, player_rect.y - camera_y))

        # Draw hearts
        for i in range(hearts):
            pygame.draw.rect(screen, RED, (20 + i * 35, 20, 30, 30))

    pygame.display.flip()
    clock.tick(60)