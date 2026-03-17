import pygame
import random
import sys
import time

# Inicialización de Pygame
pygame.init()

# --- Configuración y Constantes ---
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
NEON_BLUE = (0, 255, 255)
NEON_PINK = (255, 105, 180)
NEON_GREEN = (50, 255, 50)
NEON_RED = (255, 50, 50)
NEON_YELLOW = (255, 255, 0)

# Configuración de la pista (Teclas)
# Definimos 4 carriles principales
LANES = [
    {"key": "a", "color": NEON_BLUE, "x_offset": 100},
    {"key": "s", "color": NEON_PINK, "x_offset": 300},
    {"key": "d", "color": NEON_GREEN, "x_offset": 500},
    {"key": "f", "color": NEON_YELLOW, "x_offset": 700},
]

# --- Clases ---

class Note:
    def __init__(self, lane_index):
        self.lane_index = lane_index
        self.y = -50
        self.speed = random.randint(4, 8)
        self.color = LANES[lane_index]["color"]
        self.hit = False
        self.missed = False
        self.width = 40
        self.height = 20

    def update(self):
        self.y += self.speed

    def draw(self, screen):
        # Efecto de brillo (glow)
        glow_color = self.color
        s = 10
        pygame.draw.rect(screen, glow_color, 
                         (LANES[self.lane_index]["x_offset"] - self.width//2 - s, self.y - s, self.width + 2*s, self.height + 2*s), 
                         border_radius=5)
        
        # Nota principal
        pygame.draw.rect(screen, WHITE, 
                         (LANES[self.lane_index]["x_offset"] - self.width//2, self.y, self.width, self.height), 
                         border_radius=5)

class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.target_x = self.x
        self.y = HEIGHT - 100
        self.width = 60
        self.height = 30
        self.color = WHITE
        self.score = 0
        self.lives = 3
        self.score_text = 0
        self.shake_time = 0
        self.shake_x = 0
        self.shake_y = 0

    def move(self, key):
        # Movimiento suave hacia el carril seleccionado
        for lane in LANES:
            if lane["key"] == key:
                self.target_x = lane["x_offset"] - self.width // 2
                break
        
        # Interpolación lineal para movimiento suave
        self.x += (self.target_x - self.x) * 0.2
        # Limites de pantalla
        if self.x < 0: self.x = 0
        if self.x > WIDTH - self.width: self.x = WIDTH - self.width

    def draw(self, screen):
        # Efecto de vibración si hubo error
        if self.shake_time > 0:
            self.shake_x = random.randint(-10, 10)
            self.shake_y = random.randint(-10, 10)
            self.shake_time -= 1
            shake_offset = (self.shake_x, self.shake_y)
        else:
            shake_offset = (0, 0)

        # Cuerpo del jugador
        pygame.draw.rect(screen, self.color, 
                         (self.x + shake_offset[0], self.y + shake_offset[1], self.width, self.height), 
                         border_radius=10)
        
        # Detalles visuales
        pygame.draw.rect(screen, NEON_BLUE, 
                         (self.x + shake_offset[0], self.y + shake_offset[1], self.width, 5), 
                         border_radius=10)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Neon Rhythm Racer")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24, bold=True)
        self.large_font = pygame.font.SysFont("Arial", 60, bold=True)
        self.reset_game()

    def reset_game(self):
        self.notes = []
        self.player = Player()
        self.notes_to_spawn = 0
        self.spawn_timer = 0
        self.game_over = False
        self.menu = True
        self.restart = False
        self.spawn_rate = 60  # Frames entre notas

    def spawn_note(self):
        if self.spawn_timer >= self.spawn_rate:
            lane = random.randint(0, len(LANES) - 1)
            self.notes.append(Note(lane))
            self.spawn_timer = 0
        else:
            self.spawn_timer += 1

    def check_hits(self):
        for note in self.notes[:]:
            # Verificar si la nota está en la zona de acierto (cerca del jugador)
            target_y = self.player.y - 15
            tolerance = 30

            # Verificar colisión con el jugador en el carril correcto
            player_lane_x = self.player.x + self.player.width // 2
            note_lane_x = LANES[note.lane_index]["x_offset"]
            
            # Distancia vertical
            if abs(note.y - target_y) < tolerance:
                # Distancia horizontal (ancho de la nota vs ancho del jugador)
                if abs(note_lane_x - player_lane_x) < 40:
                    # HIT!
                    self.player.score += 100
                    self.player.score_text = 100
                    self.player.shake_time = 0
                    self.notes.remove(note)
                    continue
            
            # Si la nota pasa el jugador y no fue acertada
            if note.y > self.player.y + 40 and not note.missed:
                # MISS
                self.player.lives -= 1
                self.player.shake_time = 30
                self.player.shake_x = 0
                self.player.shake_y = 0
                self.player.score_text = -100
                note.missed = True
        
        # Eliminar notas muy abajo
        self.notes = [n for n in self.notes if n.y < HEIGHT + 50]

    def draw_ui(self):
        # UI Superior
        score_text = self.font.render(f"Puntos: {self.player.score}", True, WHITE)
        lives_text = self.font.render(f"Vidas: {self.player.lives}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (WIDTH - 150, 10))

        # Texto de feedback (Hit/Miss)
        if self.player.score_text != 0:
            color = NEON_GREEN if self.player.score_text > 0 else NEON_RED
            feedback = self.large_font.render(str(self.player.score_text), True, color)
            self.screen.blit(feedback, (WIDTH // 2 - feedback.get_width() // 2, HEIGHT // 2))

        # Menú Principal
        if self.menu:
            title = self.large_font.render("NEON RHYTHM RACER", True, NEON_BLUE)
            subtitle = self.font.render("Presiona ESPACIO para jugar", True, WHITE)
            self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 50))
            self.screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, HEIGHT // 2 + 20))

        # Game Over
        if self.game_over:
            title = self.large_font.render("GAME OVER", True, NEON_RED)
            score_final = self.font.render(f"Puntuación Final: {self.player.score}", True, WHITE)
            restart = self.font.render("Presiona ESPACIO para reiniciar", True, NEON_GREEN)
            self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 100))
            self.screen.blit(score_final, (WIDTH // 2 - score_final.get_width() // 2, HEIGHT // 2))
            self.screen.blit(restart, (WIDTH // 2 - restart.get_width() // 2, HEIGHT // 2 + 50))

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    
                    if self.menu:
                        if event.key == pygame.K_SPACE:
                            self.reset_game()
                            self.menu = False
                    
                    if self.game_over:
                        if event.key == pygame.K_SPACE:
                            self.reset_game()
                            self.game_over = False
                            self.menu = False
                    
                    # Movimiento durante el juego
                    if not self.game_over and not self.menu:
                        self.player.move(event.key)

            if not self.game_over:
                self.spawn_note()
                # self.player.update() # No es necesario en este juego
                self.check_hits()

                # Game Over conditions
                if self.player.lives <= 0:
                    self.game_over = True
                elif self.player.score >= 2000:
                    self.game_over = True # Victoria temprana
                    # Reiniciar automáticamente o mostrar mensaje
                    self.game_over = True 
                    self.player.lives = 3 # Resetear vidas para reinicio

            # Dibujado
            self.screen.fill(BLACK)
            
            # Dibujar carriles de guía (suaves)
            for lane in LANES:
                pygame.draw.line(self.screen, (50, 50, 50), (lane["x_offset"], 0), (lane["x_offset"], HEIGHT), 2)
                pygame.draw.line(self.screen, (30, 30, 30), (lane["x_offset"] - 10, 0), (lane["x_offset"] - 10, HEIGHT), 2)
                pygame.draw.line(self.screen, (30, 30, 30), (lane["x_offset"] + 10, 0), (lane["x_offset"] + 10, HEIGHT), 2)

            if not self.game_over:
                # Dibujamos las notas (es una lista, no un Group)
                for note in self.notes:
                    note.draw(self.screen)
                self.player.draw(self.screen)

            self.draw_ui()
            pygame.display.flip()

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()