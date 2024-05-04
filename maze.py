import pygame
import random
import sys

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRAVITY = 1
JUMP_STRENGTH = 15
PLAYER_SPEED = 5
PLATFORM_WIDTH = 100
PLATFORM_HEIGHT = 20
ENEMY_SIZE = 30
ITEM_SIZE = 20
BULLET_SPEED = 10
ENEMY_SPEED = 2
ENEMY_JUMP_CHANCE = 0.05  # 5% chance to jump
PLAYER_MAX_HP = 10

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Platform class
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width=PLATFORM_WIDTH, height=PLATFORM_HEIGHT):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Player class with shooting and health
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.midbottom = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20)
        self.velocity = 0
        self.jumps = 0
        self.direction = 1  # 1 for right, -1 for left
        self.bullets = pygame.sprite.Group()  # Bullet group for the player
        self.hp = PLAYER_MAX_HP

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

        if self.rect.left < 0:
            self.rect.left = 0
            self.direction = 1  # Face right

        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            self.direction = -1  # Face left

    def jump(self):
        if self.jumps < 2:
            self.velocity = -JUMP_STRENGTH
            self.jumps += 1

    def update(self, platforms):
        self.velocity += GRAVITY
        self.rect.y += self.velocity

        # Collision with platforms
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity > 0:  # Landing on a platform
                    self.rect.bottom = platform.rect.top
                    self.velocity = 0
                    self.jumps = 0  # Reset jumps after landing

        # Boundaries
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.velocity = 0
            self.jumps = 0

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.centery, self.direction * BULLET_SPEED)
        self.bullets.add(bullet)

# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speed = speed

    def update(self):
        self.rect.x += self.speed
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

# Enemy class with movement, jumping, and platform handling

# Enemy class with movement, gravity, and limited jumping
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((ENEMY_SIZE, ENEMY_SIZE))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.velocity = 0
        self.direction = random.choice([1, -1])
        self.can_jump = True  # Limit jumping to when grounded or on a platform

    def update(self, platforms):
        # Apply gravity
        self.velocity += GRAVITY
        self.rect.y += self.velocity

        # Horizontal movement
        self.rect.x += self.direction * ENEMY_SPEED

        # Random jump if on the ground or a platform
        if self.can_jump and random.random() < ENEMY_JUMP_CHANCE:
            self.velocity = -JUMP_STRENGTH
            self.can_jump = False  # Can't jump until landing

        # Collision with platforms
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity > 0:  # Landing on a platform
                    self.rect.bottom = platform.rect.top
                    self.velocity = 0
                    self.can_jump = True  # Reset jump status upon landing

        # Boundaries
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.direction *= -1  # Reverse direction
            self.rect.left = max(0, self.rect.left)
            self.rect.right = min(SCREEN_WIDTH, self.rect.right)

        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.velocity = 0
            self.can_jump = True  # Reset jump status if landing on the ground
# Main game setup
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Platformer Game with Shooting")

# Platform setup
platforms = pygame.sprite.Group()
for i in range(6):
    x = random.randint(0, SCREEN_WIDTH - PLATFORM_WIDTH)
    y = random.randint(SCREEN_HEIGHT // 2, SCREEN_HEIGHT - PLATFORM_HEIGHT)
    platforms.add(Platform(x, y))

# Player setup
player = Player()

# Enemy setup
enemies = pygame.sprite.Group()
for i in range(3):
    x = random.randint(0, SCREEN_WIDTH - ENEMY_SIZE)
    y = random.randint(SCREEN_HEIGHT // 2, SCREEN_HEIGHT - ENEMY_SIZE)
    enemies.add(Enemy(x, y))

# Game loop
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Player movement
    keys = pygame.key.get_pressed()
    dx = 0
    if keys[pygame.K_LEFT]:
        dx -= PLAYER_SPEED
        player.direction = -1  # Facing left
    if keys[pygame.K_RIGHT]:
        dx += PLAYER_SPEED
        player.direction = 1  # Facing right
    if keys[pygame.K_SPACE]:
        player.jump()
    if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:  # Shoot with Ctrl
        player.shoot()

    player.move(dx, 0)

    # Update player, bullets, and enemies
    player.update(platforms)
    player.bullets.update()

    enemies.update(platforms)

    # Check for bullet-enemy collisions
    for bullet in player.bullets:
        hit_enemies = pygame.sprite.spritecollide(bullet, enemies, True)
        if hit_enemies:
            bullet.kill()  # If a bullet hits an enemy, remove the bullet
            player.hp += 1  # Gain health when an enemy is defeated

            # Summon two more enemies when one is killed
            for _ in range(2):
                x = random.randint(0, SCREEN_WIDTH - ENEMY_SIZE)
                y = random.randint(SCREEN_HEIGHT // 2, SCREEN_HEIGHT - ENEMY_SIZE)
                enemies.add(Enemy(x, y))

    # Check for enemy collisions with the player
    hit_by_enemies = pygame.sprite.spritecollide(player, enemies, False)
    if hit_by_enemies:
        player.hp -= 1  # Decrease health if player collides with an enemy
        if player.hp <= 0:  # If health drops to zero, game over
            pygame.quit()
            sys.exit()

    # Drawing
    screen.fill(BLACK)
    platforms.draw(screen)
    enemies.draw(screen)
    player.bullets.draw(screen)  # Draw bullets
    screen.blit(player.image, player.rect.topleft)

    # Display health
    font = pygame.font.Font(None, 36)
    text = font.render(f"HP: {player.hp}", True, WHITE)
    screen.blit(text, (10, 10))

    pygame.display.flip()
    clock.tick(30)  # 30 FPS
