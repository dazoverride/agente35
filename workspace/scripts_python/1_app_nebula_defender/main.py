import pygame
import math
import random

# --- Configuración Inicial ---
pygame.init()
WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Nebulosa Defender - Arquitecto Python")
CLOCK = pygame.time.Clock()

# Colores
BLACK = (10, 10, 20)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
RED = (255, 50, 50)
YELLOW = (255, 255, 0)
DARK_BLUE = (0, 0, 50)

# Fuentes
font = pygame.font.SysFont("arial", 24)
small_font = pygame.font.SysFont("arial", 18)

class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 100
        self.radius = 20
        self.angle = 0
        self.color = CYAN
        
    def draw(self, surface):
        # Dibujar el núcleo
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.radius)
        # Dibujar el láser (triángulo rotado)
        laser_length = 150
        laser_width = 15
        laser_points = [
            (self.x, self.y),
            (self.x - laser_length * math.cos(self.angle), self.y - laser_length * math.sin(self.angle)),
            (self.x + laser_length * math.cos(self.angle), self.y - laser_length * math.sin(self.angle))
        ]
        pygame.draw.polygon(surface, YELLOW, laser_points)
        
    def rotate(self, direction):
        self.angle += direction * 0.05
        
    def handle_events(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rotate(-1)
        if keys[pygame.K_RIGHT]:
            self.rotate(1)

class Asteroid:
    def __init__(self):
        self.radius = random.randint(10, 25)
        self.x = random.randint(0, WIDTH)
        self.y = -self.radius
        self.speed = random.randint(2, 5)
        self.color = (random.randint(50, 150), random.randint(50, 150), random.randint(50, 150))
        
    def update(self):
        self.y += self.speed
        
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        # Detalle interior
        pygame.draw.circle(surface, (50, 50, 50), (int(self.x), int(self.y)), self.radius - 5)

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        self.life = 1.0
        self.color = (random.randint(200, 255), random.randint(200, 255), random.randint(200, 255))
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 0.02
        
    def draw(self, surface):
        alpha = int(self.life * 255)
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), 3)

class Game:
    def __init__(self):
        self.player = Player()
        self.asteroids = []
        self.particles = []
        self.score = 0
        self.game_over = False
        self.spawn_timer = 0
        self.spawn_rate = 60 # Frames
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.game_over:
                    # Disparo automático con tecla espacio (opcional, aquí usamos rotación para disparo)
                    pass
                elif event.key == pygame.K_r and self.game_over:
                    self.restart()
        return True

    def spawn_asteroid(self):
        self.asteroids.append(Asteroid())
        
    def check_collisions(self):
        for asteroid in self.asteroids[:]:
            # Colisión simple circulo-circulo
            dist = math.hypot(self.player.x - asteroid.x, self.player.y - asteroid.y)
            if dist < self.player.radius + asteroid.radius:
                # Si el láser está apuntando al asteroide
                angle_to_asteroid = math.atan2(asteroid.y - self.player.y, asteroid.x - self.player.x)
                angle_diff = abs(angle_to_asteroid - self.player.angle)
                
                # Normalizar ángulo a -PI a PI
                while angle_diff > math.pi: angle_diff -= 2 * math.pi
                while angle_diff < -math.pi: angle_diff += 2 * math.pi
                
                # Si el ángulo es pequeño (dentro del cono del láser)
                if abs(angle_diff) < 0.3: 
                    self.create_explosion(asteroid.x, asteroid.y)
                    self.asteroids.remove(asteroid)
                    self.score += 10
                else:
                    self.game_over = True
                    
    def create_explosion(self, x, y):
        for _ in range(10):
            self.particles.append(Particle(x, y))
            
    def restart(self):
        self.player = Player()
        self.asteroids = []
        self.particles = []
        self.score = 0
        self.game_over = False
        
    def update(self):
        self.spawn_timer += 1
        if self.spawn_timer > self.spawn_rate:
            self.spawn_asteroid()
            self.spawn_timer = 0
            # Aumentar dificultad
            if self.spawn_rate > 20:
                self.spawn_rate -= 1
                
        self.player.handle_events() # Lógica de rotación continua si se presionan teclas
        
        for asteroid in self.asteroids:
            asteroid.update()
            
        for particle in self.particles[:]:
            particle.update()
            if particle.life <= 0:
                self.particles.remove(particle)
                
        self.check_collisions()
        
        # Limpiar asteroides fuera de pantalla
        self.asteroids = [a for a in self.asteroids if a.y < HEIGHT]

    def draw(self):
        SCREEN.fill(BLACK)
        
        # Dibujar estrellas de fondo
        for _ in range(50):
            sx = random.randint(0, WIDTH)
            sy = random.randint(0, HEIGHT)
            s_size = random.randint(1, 2)
            pygame.draw.circle(SCREEN, (random.randint(200, 255), 200, 200), (sx, sy), s_size)
            
        self.player.draw(SCREEN)
        
        for asteroid in self.asteroids:
            asteroid.draw(SCREEN)
            
        for particle in self.particles:
            particle.draw(SCREEN)
            
        # UI
        score_text = font.render(f"Puntos: {self.score}", True, WHITE)
        SCREEN.blit(score_text, (10, 10))
        
        if self.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            SCREEN.blit(overlay, (0, 0))
            
            go_text = font.render("GAME OVER", True, RED)
            restart_text = small_font.render("Presiona 'R' para reiniciar", True, WHITE)
            SCREEN.blit(go_text, (WIDTH//2 - go_text.get_width()//2, HEIGHT//2 - 50))
            SCREEN.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 10))
            
        pygame.display.flip()

def main():
    game = Game()
    running = True
    while running:
        running = game.handle_events()
        game.update()
        game.draw()
        CLOCK.tick(60)
    pygame.quit()

if __name__ == "__main__":
    main()