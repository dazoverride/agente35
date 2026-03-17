import pygame
import random
import math

# --- Configuración Inicial ---
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Explorador Espacial: Busca Tesoros")
clock = pygame.time.Clock()
FPS = 60

# Colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
GRAY = (100, 100, 100)
ORANGE = (255, 165, 0)

# Fuentes
font = pygame.font.SysFont("Arial", 24, bold=True)
small_font = pygame.font.SysFont("Arial", 18)

# --- Clases ---

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        # Dibujar una nave simple (triángulo invertido)
        pygame.draw.polygon(self.image, BLUE, [(20, 0), (0, 40), (40, 40)])
        # Motor de fuego
        self.rect = self.image.get_rect()
        self.speed = 5
        self.score = 0
        self.fuel = 100
        self.max_fuel = 100
        self.shoot_delay = 15
        self.last_shot = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += self.speed

        # Límites de pantalla
        self.rect.x = max(0, min(self.rect.x, WIDTH - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, HEIGHT - self.rect.height))

        # Consumo de combustible
        if keys[pygame.K_SPACE]:
            self.fuel -= 0.2
        else:
            self.fuel += 0.1
        if self.fuel > self.max_fuel:
            self.fuel = self.max_fuel

        # Disparo
        if keys[pygame.K_SPACE] and pygame.time.get_ticks() - self.last_shot > self.shoot_delay:
            self.shoot()
            self.last_shot = pygame.time.get_ticks()

    def shoot(self):
        # Lanza un láser hacia el centro de la nave
        laser = Laser(self.rect.centerx, self.rect.centery)
        all_sprites.add(laser)
        # Efecto visual simple de disparo
        screen.blit(self.image, (self.rect.x, self.rect.y)) # Para limpiar si hubiera animación

    def draw_fuel(self):
        # Barra de combustible sobre la nave
        fuel_width = int(self.rect.width * (self.fuel / self.max_fuel))
        pygame.draw.rect(self.image, RED, (0, 0, self.rect.width, 5))
        pygame.draw.rect(self.image, GREEN, (0, 0, fuel_width, 5))

class Laser(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((10, 20))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = -10

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()

class Planet(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.size = random.randint(20, 50)
        self.image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        # Dibujar planeta
        pygame.draw.circle(self.image, random.choice([GREEN, BLUE, ORANGE]), (self.size, self.size), self.size)
        pygame.draw.circle(self.image, GRAY, (self.size, self.size), self.size, 3)
        
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.size * 2)
        self.rect.y = -self.size * 2 # Empieza arriba fuera de pantalla
        self.speed = random.uniform(2, 5)
        self.type = 'fuel' if random.random() < 0.3 else 'planet'

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.rect.y = -self.size * 2
            self.rect.x = random.randint(0, WIDTH - self.size * 2)

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, RED, [(15, 0), (30, 15), (15, 30), (0, 15)])
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = -50
        self.speed = random.uniform(3, 6)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

class Star(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((4, 4))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH)
        self.rect.y = random.randint(0, HEIGHT)
        self.speed = random.uniform(1, 3)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.rect.y = 0
            self.rect.x = random.randint(0, WIDTH)

# --- Grupos de Sprites ---
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
lasers = pygame.sprite.Group()
planets = pygame.sprite.Group()
stars = pygame.sprite.Group()

# --- Funciones de Utilidad ---

def draw_background():
    screen.fill(BLACK)
    # Fondo estrellado
    for star in stars:
        screen.blit(star.image, star.rect)
    
    # Información del jugador
    info_text = f"Puntuación: {player.score} | Combustible: {int(player.fuel)}%"
    text_surf = font.render(info_text, True, WHITE)
    screen.blit(text_surf, (10, 10))

def draw_ui():
    # Barra de combustible
    fuel_bar_rect = pygame.Rect(10, HEIGHT - 20, 200, 20)
    pygame.draw.rect(screen, RED, fuel_bar_rect)
    pygame.draw.rect(screen, GREEN, fuel_bar_rect, width=0)
    pygame.draw.rect(screen, GREEN, pygame.Rect(fuel_bar_rect.x, fuel_bar_rect.y, int(fuel_bar_rect.width * (player.fuel / player.max_fuel)), fuel_bar_rect.height))
    
    # Mensaje de juego
    if player.fuel <= 0:
        game_over_text = font.render("¡AGOTADO! Presiona R para reiniciar", True, RED)
        screen.blit(game_over_text, (WIDTH/2 - game_over_text.get_width()/2, HEIGHT/2))

# --- Configuración de Entidades ---
player = Player()
all_sprites.add(player)

# Estrellas de fondo
for _ in range(50):
    star = Star()
    all_sprites.add(star)
    stars.add(star)

# Generadores de entidades
def add_planet():
    planet = Planet()
    all_sprites.add(planet)
    planets.add(planet)

def add_enemy():
    enemy = Enemy()
    all_sprites.add(enemy)
    enemies.add(enemy)

# --- Bucle Principal ---
running = True
game_state = "PLAYING" # PLAYING, GAMEOVER

while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if game_state == "GAMEOVER" and event.key == pygame.K_r:
                # Reiniciar juego
                player.score = 0
                player.fuel = 100
                player.rect.x = WIDTH // 2 - 20
                player.rect.y = HEIGHT // 2 - 20
                all_sprites.empty()
                lasers.empty()
                enemies.empty()
                planets.empty()
                stars.empty()
                
                # Volver a añadir estrellas
                for _ in range(50):
                    s = Star()
                    all_sprites.add(s)
                    stars.add(s)
                
                add_planet()
                game_state = "PLAYING"

    if game_state == "PLAYING":
        # Actualizar
        player.update()
        all_sprites.update()

        # Generación aleatoria
        if random.random() < 0.02: # Probabilidad de planeta
            add_planet()
        if random.random() < 0.03: # Probabilidad de enemigo
            add_enemy()

        # Detectar colisiones
        # 1. Jugador choca con enemigo -> Perder combustible
        hits = pygame.sprite.spritecollide(player, enemies, False)
        for enemy in hits:
            player.fuel -= 20
            enemy.kill()
            # Efecto visual de choque (opcional, aquí simple)
        
        # 2. Jugador choca con planeta -> Recargar combustible
        hits = pygame.sprite.spritecollide(player, planets, False)
        for planet in hits:
            player.fuel = min(player.fuel + 30, player.max_fuel)
            player.score += 50
            planet.kill() # El planeta se consume al tocarlo

        # 3. Láser choca con enemigo -> Puntos y eliminar enemigo
        hits = pygame.sprite.groupcollide(lasers, enemies, True, True)
        if hits:
            # groupcollide devuelve un dict {laser: [enemigos_impactados]}, sumamos puntos por cada láser que impactó
            player.score += 10 * len(hits)
            player.score += 10

        # Limpiar láseres fuera de pantalla
        lasers.remove([l for l in lasers if l.rect.bottom < 0])

        # Verificar Game Over
        if player.fuel <= 0:
            game_state = "GAMEOVER"

    # Dibujar todo
    draw_background()
    
    # Dibujar entidades
    for sprite in all_sprites:
        if hasattr(sprite, 'draw_fuel'):
            sprite.draw_fuel()
        else:
            screen.blit(sprite.image, sprite.rect)
    
    draw_ui()

    pygame.display.flip()

pygame.quit()