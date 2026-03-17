import pygame
import random
import math

# --- Configuración Inicial ---
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pixel Plague: Defend the Core")
clock = pygame.time.Clock()
FPS = 60

# --- Colores ---
COLOR_BG = (15, 20, 30)       # Azul oscuro profundo
COLOR_PLAYER = (0, 255, 255)  # Cyan
COLOR_PIXEL = (255, 215, 0)   # Oro
COLOR_ZOMBIE = (20, 20, 20)   # Gris muy oscuro
COLOR_BARRIER = (100, 100, 255) # Azul medio
COLOR_TEXT = (255, 255, 255)

# --- Fuentes ---
font_small = pygame.font.SysFont('monospace', 18)
font_large = pygame.font.SysFont('monospace', 36)

# --- Clases ---

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 5)
        self.speed = random.uniform(2, 5)
        self.angle = random.uniform(0, 2 * math.pi)
        self.vx = math.cos(self.angle) * self.speed
        self.vy = math.sin(self.angle) * self.speed
        self.life = 100  # Frames de vida
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        return self.life > 0

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)

class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.radius = 15
        self.speed = 4
        self.pixel_count = 0
        self.barrier_active = False
        self.barrier_timer = 0
        
    def move(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += self.speed
            
        # Límites de pantalla
        self.x = max(self.radius, min(WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(HEIGHT - self.radius, self.y))
        
    def draw(self, surface):
        # Dibujar jugador
        pygame.draw.circle(surface, COLOR_PLAYER, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x), int(self.y)), self.radius, 2)
        
        # Dibujar indicador de píxeles si hay muchos
        if self.pixel_count > 0:
            text = font_small.render(f"Pixels: {self.pixel_count}", True, COLOR_TEXT)
            surface.blit(text, (self.x - text.get_width()//2, self.y - self.radius - 20))

class Pixel:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.radius = 6
        self.size = random.randint(200, 300) # Probabilidad de aparición
        
    def draw(self, surface):
        pygame.draw.circle(surface, COLOR_PIXEL, (int(self.x), int(self.y)), self.radius)
        # Brillo
        pygame.draw.circle(surface, (255, 220, 100), (int(self.x), int(self.y)), self.radius, 1)

class Zombie:
    def __init__(self):
        # Aparecer en los bordes
        if random.choice([True, False]):
            self.x = random.choice([0, WIDTH])
            self.y = random.randint(0, HEIGHT)
        else:
            self.x = random.randint(0, WIDTH)
            self.y = random.choice([0, HEIGHT])
            
        self.target_x = WIDTH // 2
        self.target_y = HEIGHT // 2
        self.speed = random.uniform(1, 2.5)
        self.size = 12
        self.color = COLOR_ZOMBIE
        
    def update(self, player_x, player_y):
        # Calcular vector hacia el jugador
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.hypot(dx, dy)
        
        if distance > 0:
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed
            
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)
        # Ojos rojos
        pygame.draw.circle(surface, (255, 0, 0), (int(self.x) - 4, int(self.y) - 2), 2)
        pygame.draw.circle(surface, (255, 0, 0), (int(self.x) + 4, int(self.y) - 2), 2)

class Barrier:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.radius = 40
        self.active = False
        self.shield_timer = 0
        
    def activate(self):
        self.active = True
        self.shield_timer = 180 # 3 segundos a 60 FPS
        
    def update(self):
        if self.active:
            self.shield_timer -= 1
            if self.shield_timer <= 0:
                self.active = False
        else:
            # Volver al centro si no está activo
            self.x = WIDTH // 2
            self.y = HEIGHT // 2
            
    def draw(self, surface):
        if self.active:
            # Escudo
            pygame.draw.circle(surface, COLOR_BARRIER, (int(self.x), int(self.y)), self.radius, 5)
            # Efecto de brillo
            pygame.draw.circle(surface, (150, 150, 255), (int(self.x), int(self.y)), self.radius, 2)
            
            # Texto de tiempo
            time_left = max(0, self.shield_timer // 60)
            text = font_small.render(f"Escudo: {time_left}", True, (100, 100, 255))
            surface.blit(text, (self.x - text.get_width()//2, self.y - self.radius - 15))

# --- Variables Globales del Juego ---
player = Player()
pixels = []
zombies = []
particles = []
barrier = Barrier()

# Contadores
score = 0
game_over = False
pixel_spawn_timer = 0
zombie_spawn_timer = 0
pixel_spawn_rate = 120 # Frames
zombie_spawn_rate = 300 # Frames

# --- Bucle Principal ---
running = True
while running:
    # 1. Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:
                barrier.activate()
            if event.key == pygame.K_r and game_over:
                # Reiniciar
                player = Player()
                pixels = []
                zombies = []
                particles = []
                barrier = Barrier()
                score = 0
                game_over = False
                pixel_spawn_rate = 120
                zombie_spawn_rate = 300
                
    if game_over:
        continue

    keys = pygame.key.get_pressed()
    player.move(keys)
    
    # 2. Lógica del Juego
    pixel_spawn_timer += 1
    if pixel_spawn_timer >= pixel_spawn_rate:
        pixels.append(Pixel())
        pixel_spawn_timer = 0
        # Aumentar dificultad progresivamente
        if pixel_spawn_rate > 40:
            pixel_spawn_rate -= 1
            
    zombie_spawn_timer += 1
    if zombie_spawn_timer >= zombie_spawn_rate:
        zombies.append(Zombie())
        zombie_spawn_timer = 0
        # Aumentar dificultad
        if zombie_spawn_rate > 100:
            zombie_spawn_rate -= 2

    # Actualizar partículas
    particles = [p for p in particles if p.update()]
    
    # Actualizar píxeles
    for p in pixels:
        # Verificar colisión con jugador
        dist = math.hypot(player.x - p.x, player.y - p.y)
        if dist < player.radius + p.radius:
            player.pixel_count += 10
            # Crear explosión de partículas
            for _ in range(5):
                particles.append(Particle(p.x, p.y, COLOR_PIXEL))
            pixels.remove(p)
            
    # Actualizar zombies
    for z in zombies:
        z.update(player.x, player.y)
        
        # Colisión con jugador
        dist = math.hypot(player.x - z.x, player.y - z.y)
        if dist < player.radius + z.size:
            # Colisionar con escudo?
            dist_to_barrier = math.hypot(player.x - barrier.x, player.y - barrier.y)
            if barrier.active and dist_to_barrier < barrier.radius + player.radius:
                # El escudo protege al jugador, el zombie choca con el escudo
                barrier.shield_timer -= 10 # Escudo se debilita rápido
                if barrier.shield_timer <= 0:
                    barrier.active = False
                # El zombie sigue vivo pero dañado (en este caso simple, solo rebota o desaparece)
                # Para simplificar, el zombie muere si toca el escudo activo
                zombies.remove(z)
                # Efecto visual
                particles.append(Particle(player.x, player.y, (255, 50, 50)))
            else:
                # Muerte del jugador
                game_over = True
                particles.append(Particle(player.x, player.y, COLOR_PLAYER))
                for _ in range(30):
                    particles.append(Particle(player.x, player.y, COLOR_PLAYER))
                break
        
        # Colisión con barreras (si las hubiera, por ahora solo central)
        # Lógica simple: si el zombie toca la barrera central, muere
        dist_barr = math.hypot(z.x - barrier.x, z.y - barrier.y)
        if dist_barr < barrier.radius + z.size:
            if barrier.active:
                zombies.remove(z)
                particles.append(Particle(z.x, z.y, COLOR_BARRIER))
            else:
                # Si la barrera no está activa, el zombie la rompe?
                # Simplificación: si toca el centro sin escudo, es daño a la barrera
                barrier.shield_timer -= 15
                if barrier.shield_timer <= 0:
                    barrier.active = False

    # Actualizar barrera
    barrier.update()
    
    # Actualizar UI
    # Barra de vida (Escudo)
    shield_pct = (barrier.shield_timer / 180) * 100
    pygame.draw.rect(screen, (50, 50, 50), (10, 10, 200, 20))
    pygame.draw.rect(screen, COLOR_BARRIER, (10, 10, 200 * (shield_pct/100), 20))

    # 3. Dibujado
    screen.fill(COLOR_BG)
    
    # Dibujar barrera central siempre (la base)
    pygame.draw.circle(screen, (30, 30, 60), (WIDTH//2, HEIGHT//2), 30)
    
    # Dibujar entidades
    for p in pixels:
        p.draw(screen)
    for z in zombies:
        z.draw(screen)
    for p in particles:
        p.draw(screen)
    barrier.draw(screen)
    player.draw(screen)
    
    # Texto de puntuación
    score_text = font_large.render(f"Score: {score}", True, COLOR_TEXT)
    screen.blit(score_text, (10, 10))
    
    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        go_text = font_large.render("GAME OVER", True, (255, 50, 50))
        sub_text = font_small.render("Presiona 'R' para reiniciar", True, COLOR_TEXT)
        
        screen.blit(go_text, (WIDTH//2 - go_text.get_width()//2, HEIGHT//2 - 50))
        screen.blit(sub_text, (WIDTH//2 - sub_text.get_width()//2, HEIGHT//2 + 10))
        
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
```

<file name="README.md">
```markdown
# Pixel Plague: Defend the Core

## Descripción
Un juego de supervivencia en tiempo real donde debes recolectar píxeles dorados para sobrevivir a una horda de zombies oscuros.

## Controles
- **WASD / Flechas**: Moverse al jugador.
- **ESPACIO**: Activar el escudo temporal de energía (consume tiempo de vida).
- **R**: Reiniciar el juego al perder.

## Objetivo
1. Recoge los círculos dorados ("Pixels") para aumentar tu puntuación.
2. Evita que los zombies (círculos grises oscuros) te toquen.
3. Usa el escudo cuando la horda sea muy numerosa.
4. La dificultad aumenta con el tiempo: aparecen más píxeles y zombies más rápido.

## Requisitos
- Python 3.x
- Librería `pygame` (Instalar con: `pip install pygame`)

## Cómo Jugar
1. Ejecuta `main.py`.
2. Mueve al jugador (círculo cian) hacia los píxeles.
3. Cuando los zombies lleguen, presiona ESPACIO para activar el escudo azul.
4. Intenta sobrevivir el mayor tiempo posible.
```