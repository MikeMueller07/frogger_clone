import os
import pygame
import random

# Einstellungen
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 750
PLAYER_SIZE = 50
FPS = 60
ENEMY_INTERVAL = 500  # Spawn-Intervall in Millisekunden
ENEMY_SPEED = 1  # Gegnergeschwindigkeit
ESCAPE_DOUBLE_PRESS_TIME = 500  # Zeitfenster in Millisekunden für Doppeldruck
FILE_PATH = os.path.dirname(os.path.abspath(__file__))
IMAGE_PATH = os.path.join(FILE_PATH, "images")

# Initialisierung
os.environ["SDL_VIDEO_WINDOW_POS"] = "10,50"
pygame.init()

# Fenster und Clock
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("leck eier")
clock = pygame.time.Clock()

# Schriftarten
font = pygame.font.SysFont(None, 36)

# Spieler-Setup
player_image = pygame.image.load(os.path.join(IMAGE_PATH, "player.jpeg")).convert()
player_image = pygame.transform.scale(player_image, (PLAYER_SIZE, PLAYER_SIZE))
player_rect = pygame.Rect(WINDOW_WIDTH // 2, WINDOW_HEIGHT - PLAYER_SIZE, PLAYER_SIZE, PLAYER_SIZE)

# Gegner-Setup
enemy_image = pygame.image.load(os.path.join(IMAGE_PATH, "enemy.jpeg")).convert()
enemy_image = pygame.transform.scale(enemy_image, (PLAYER_SIZE, PLAYER_SIZE))
enemies = []
next_enemy_time = pygame.time.get_ticks() + ENEMY_INTERVAL

# Variablen für Escape-Doppeldruck
last_escape_time = 0

# Spielstatus
running = True
paused = False

# Punktestand
score = 0

def draw_board(screen, tile_size):
    """Zeichnet ein Schachbrettmuster mit grüner oberer und unterer Reihe."""
    for row in range(0, WINDOW_HEIGHT // tile_size):
        for col in range(0, WINDOW_WIDTH // tile_size):
            if row == 0:  # Oberste Reihe
                color = (0, 255, 0)  # Grün
            elif row == (WINDOW_HEIGHT // tile_size) - 1:  # Unterste Reihe
                color = (0, 255, 0)  # Grün
            elif (row + col) % 2 == 0:
                color = (200, 200, 200)  # Hellgrau
            else:
                color = (100, 100, 100)  # Dunkelgrau
            pygame.draw.rect(screen, color, (col * tile_size, row * tile_size, tile_size, tile_size))

def spawn_enemy():
    """Erzeugt einen neuen Gegner an einer zufälligen Position und Richtung."""
    row = random.randint(1, (WINDOW_HEIGHT // PLAYER_SIZE) - 2)  # Keine grünen Reihen
    direction = random.randint(1, 2)
    if direction == 1:
        x_pos = WINDOW_WIDTH
        speed = -ENEMY_SPEED
    else:
        x_pos = -PLAYER_SIZE
        speed = ENEMY_SPEED
    y_pos = row * PLAYER_SIZE
    return pygame.Rect(x_pos, y_pos, PLAYER_SIZE, PLAYER_SIZE), speed

def draw_pause_overlay():
    """Zeichnet den Pause-Bildschirm mit grauem Schleier."""
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    overlay.fill((50, 50, 50))  # Grau
    screen.blit(overlay, (0, 0))
    pause_text = font.render("PAUSE - Press 'P' to Resume", True, (255, 255, 255))
    screen.blit(pause_text, (WINDOW_WIDTH // 2 - pause_text.get_width() // 2, WINDOW_HEIGHT // 2))

# Haupt-Spielschleife
while running:
    current_time = pygame.time.get_ticks()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if current_time - last_escape_time <= ESCAPE_DOUBLE_PRESS_TIME:
                    running = False
                else:
                    last_escape_time = current_time
            elif event.key == pygame.K_p:
                paused = not paused
            elif not paused:  # Eingaben nur, wenn nicht pausiert
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    if player_rect.right + PLAYER_SIZE <= WINDOW_WIDTH:
                        player_rect.x += PLAYER_SIZE
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    if player_rect.left - PLAYER_SIZE >= 0:
                        player_rect.x -= PLAYER_SIZE
                elif event.key == pygame.K_UP or event.key == pygame.K_w:
                    if player_rect.top - PLAYER_SIZE >= 0:
                        player_rect.y -= PLAYER_SIZE
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    if player_rect.bottom + PLAYER_SIZE <= WINDOW_HEIGHT:
                        player_rect.y += PLAYER_SIZE

    if not paused:
        # Neustart des Spielers, wenn die oberste Reihe erreicht wird
        if player_rect.top <= 0:
            player_rect.x = WINDOW_WIDTH // 2
            player_rect.y = WINDOW_HEIGHT - PLAYER_SIZE
            ENEMY_INTERVAL = max(100, ENEMY_INTERVAL - 50)
            ENEMY_SPEED += 0.5
            enemies = []
            score += 1

        # Spawne einen neuen Gegner, wenn die Zeit gekommen ist
        if current_time >= next_enemy_time:
            enemy_rect, enemy_speed = spawn_enemy()
            enemies.append((enemy_rect, enemy_speed))
            next_enemy_time = current_time + ENEMY_INTERVAL

        # Aktualisiere Gegnerpositionen und entferne Gegner, die das Fenster verlassen
        for enemy in enemies[:]:
            enemy[0].x += enemy[1]
            if enemy[0].right < 0 or enemy[0].left > WINDOW_WIDTH:
                enemies.remove(enemy)

        # Überprüfen auf Kollision zwischen Spieler und Gegner
        for enemy_rect, _ in enemies:
            if player_rect.colliderect(enemy_rect):
                player_rect.x = WINDOW_WIDTH // 2
                player_rect.y = WINDOW_HEIGHT - PLAYER_SIZE

        # Spielfläche aktualisieren
        draw_board(screen, PLAYER_SIZE)
        screen.blit(player_image, player_rect)
        for enemy_rect, _ in enemies:
            screen.blit(enemy_image, enemy_rect)

        # Punktestand anzeigen
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
    else:
        draw_pause_overlay()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
