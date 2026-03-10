import pygame
import sys
import os
import random

pygame.init()

# ---------------- Herní Okno ----------------
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pyformer")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 40)

# ---------------- Barvy ----------------
WHITE = (255,255,255)
BLACK = (0,0,0)
GREEN = (50,200,50)
BLUE = (50,50,200)
YELLOW = (240,200,50)
RED = (200,50,50)
PURPLE = (200,100,200)
GOLD = (255,215,0)

# ---------------- Gamemody ----------------
DRAW_MODE = 0
GAME_MODE = 1
DIFFICULTY_SELECT = 2

mode = DIFFICULTY_SELECT

# ---------------- Obtížnosti ----------------
difficulty = "Normal"

def set_difficulty(diff):
    global gravity, PLATFORM_WIDTH, PLATFORM_GAP, move_speed, upgrade_chance

    if diff == "Easy":
        gravity = 0.5
        PLATFORM_WIDTH = 150
        PLATFORM_GAP = 100
        move_speed = 5
        upgrade_chance = 0.35

    elif diff == "Normal":
        gravity = 0.6
        PLATFORM_WIDTH = 120
        PLATFORM_GAP = 120
        move_speed = 5
        upgrade_chance = 0.2

    elif diff == "Hard":
        gravity = 0.75
        PLATFORM_WIDTH = 90
        PLATFORM_GAP = 150
        move_speed = 6
        upgrade_chance = 0.05


# ---------------- Drawing ----------------
drawing = False
brush_size = 5
character_surface = pygame.Surface((300,300))
character_surface.fill(WHITE)

# ---------------- Player ----------------
player = None
player_rect = None
velocity_y = 0
jump_strength = -14
max_jumps = 2
jump_count = 0
adms = False
hearts = 3

# ---------------- Camera ----------------
camera_y = 0

# ---------------- Platforms ----------------
platforms = []
PLATFORM_HEIGHT = 20

def generate_platform(y):
    x = random.randint(0, WIDTH - PLATFORM_WIDTH)
    return pygame.Rect(x,y,PLATFORM_WIDTH,PLATFORM_HEIGHT)

# ---------------- Rescue platform ----------------
helper_platform = pygame.Rect(WIDTH//2 - 60,500,120,20)
helper_speed_factor = 0.01
rescue_y_offset = 50

# ---------------- Upgrades ----------------
class Upgrade:
    def __init__(self,x,y,kind):
        self.rect = pygame.Rect(x,y,30,30)
        self.kind = kind

        if kind == "jump_strength":
            self.color = PURPLE
        elif kind == "triple_jump":
            self.color = GOLD

upgrades = []

def spawn_upgrade(platform):
    kind = random.choice(["jump_strength","triple_jump"])
    x = platform.x + platform.width//2 - 15
    y = platform.y - 30
    upgrades.append(Upgrade(x,y,kind))

# ---------------- Main Loop ----------------
while True:

    screen.fill(BLUE)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # ---------------- DIFFICULTY SELECT ----------------
        if mode == DIFFICULTY_SELECT:

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_1:
                    difficulty = "Easy"
                    set_difficulty(difficulty)

                if event.key == pygame.K_2:
                    difficulty = "Normal"
                    set_difficulty(difficulty)

                if event.key == pygame.K_3:
                    difficulty = "Hard"
                    set_difficulty(difficulty)

                if event.key in [pygame.K_1,pygame.K_2,pygame.K_3]:

                    platforms.clear()

                    for i in range(6):
                        platforms.append(generate_platform(500 - i * PLATFORM_GAP))

                    mode = DRAW_MODE


        # ---------------- DRAW MODE ----------------
        elif mode == DRAW_MODE:

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                drawing = True

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                drawing = False

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_s:
                    pygame.image.save(character_surface,"my_character.png")

                if event.key == pygame.K_RETURN:

                    if os.path.exists("my_character.png"):

                        player = pygame.image.load("my_character.png").convert_alpha()
                        player = pygame.transform.scale(player,(60,60))
                        player_rect = player.get_rect()

                        player_rect.center = (WIDTH//2,400)

                        mode = GAME_MODE


        # ---------------- GAME MODE INPUT ----------------
        elif mode == GAME_MODE:

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_F8:
                    adms = not adms

                if event.key == pygame.K_SPACE:

                    if adms:
                        velocity_y = jump_strength

                    elif jump_count < max_jumps:
                        velocity_y = jump_strength
                        jump_count += 1


    # ---------------- DIFFICULTY SCREEN ----------------
    if mode == DIFFICULTY_SELECT:

        t1 = font.render("Choose Difficulty",True,WHITE)
        t2 = font.render("1 - Easy",True,WHITE)
        t3 = font.render("2 - Normal",True,WHITE)
        t4 = font.render("3 - Hard",True,WHITE)

        screen.blit(t1,(WIDTH//2-120,200))
        screen.blit(t2,(WIDTH//2-80,260))
        screen.blit(t3,(WIDTH//2-80,300))
        screen.blit(t4,(WIDTH//2-80,340))


    # ---------------- DRAW ----------------
    elif mode == DRAW_MODE:

        if drawing:
            mouse_pos = pygame.mouse.get_pos()
            adjusted_pos = (mouse_pos[0]-250, mouse_pos[1]-150)
            pygame.draw.circle(character_surface,BLACK,adjusted_pos,brush_size)

        screen.blit(character_surface,(250,150))


    # ---------------- GAME MODE ----------------
    elif mode == GAME_MODE:

        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:
            player_rect.x -= move_speed

        if keys[pygame.K_d]:
            player_rect.x += move_speed

        velocity_y += gravity
        player_rect.y += velocity_y

        grounded = False

        for platform in platforms:

            if player_rect.colliderect(platform) and velocity_y > 0:
                player_rect.bottom = platform.top
                velocity_y = 0
                grounded = True

        if grounded:
            jump_count = 0

        rescue_platform_y = camera_y + HEIGHT - rescue_y_offset
        helper_platform.top = rescue_platform_y

        helper_platform.centerx += (player_rect.centerx - helper_platform.centerx) * helper_speed_factor

        if player_rect.colliderect(helper_platform) and velocity_y > 0:

            player_rect.bottom = helper_platform.top
            velocity_y = 0
            jump_count = 0

        if player_rect.top > helper_platform.top + 50:

            hearts -= 1

            if hearts <= 0:
                pygame.quit()
                sys.exit()

            player_rect.bottom = helper_platform.top
            velocity_y = 0
            jump_count = 0


        # CAMERA
        if player_rect.top < camera_y + HEIGHT//3:
            camera_y = player_rect.top - HEIGHT//3


        # PLATFORM GENERATION
        highest_platform = min(platform.y for platform in platforms)

        while highest_platform > camera_y - HEIGHT:

            new_platform = generate_platform(highest_platform - PLATFORM_GAP)
            platforms.append(new_platform)

            if random.random() < upgrade_chance:
                spawn_upgrade(new_platform)

            highest_platform = new_platform.y

        platforms = [p for p in platforms if p.y < camera_y + HEIGHT + 100]


        # UPGRADES
        for upgrade in upgrades[:]:

            if player_rect.colliderect(upgrade.rect):

                if upgrade.kind == "jump_strength":
                    jump_strength -= 0.4

                if upgrade.kind == "triple_jump":
                    max_jumps += 1

                upgrades.remove(upgrade)

        if max_jumps > 5:
            max_jumps = 5


        # DRAW PLATFORMS
        for platform in platforms:
            pygame.draw.rect(screen,GREEN,(platform.x,platform.y-camera_y,PLATFORM_WIDTH,PLATFORM_HEIGHT))


        # DRAW UPGRADES
        for upgrade in upgrades:
            pygame.draw.rect(screen,upgrade.color,(upgrade.rect.x,upgrade.rect.y-camera_y,30,30))


        # RESCUE PLATFORM
        pygame.draw.rect(screen,YELLOW,(helper_platform.x,helper_platform.y-camera_y,120,20))


        # PLAYER
        screen.blit(player,(player_rect.x,player_rect.y-camera_y))


        # HEARTS
        for i in range(hearts):
            pygame.draw.rect(screen,RED,(20+i*35,20,30,30))


    pygame.display.flip()
    clock.tick(60)
    