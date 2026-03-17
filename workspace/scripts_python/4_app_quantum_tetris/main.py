import pygame
import random
import math
import sys

# --- Configuración Inicial ---
pygame.init()
WIDTH, HEIGHT = 800, 600
BLOCK_SIZE = 20
GRID_WIDTH = 10
GRID_HEIGHT = 20
FPS = 60

# Colores
BLACK = (10, 10, 15)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
RED = (255, 50, 50)
BLUE = (50, 50, 255)
GREEN = (50, 255, 50)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
GRAY = (100, 100, 100)

# Definición de Piezas (Tetrominos)
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[0, 1, 0], [1, 1, 1]],  # T
    [[1, 0, 0], [1, 1, 1]],  # L
    [[0, 0, 1], [1, 1, 1]],  # J
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]]   # Z
]

COLORS = [CYAN, YELLOW, PURPLE, ORANGE, BLUE, GREEN, RED]

class QuantumPiece:
    def __init__(self):
        self.reset()
    
    def reset(self):
        shape_idx = random.randint(0, len(SHAPES) - 1)
        self.shape = SHAPES[shape_idx]
        self.color = COLORS[shape_idx]
        self.x = (GRID_WIDTH // 2) - (len(self.shape[0]) // 2)
        self.y = 0
        self.rotation = 0
        self.superposition = False
        self.collapsing = False
        
    def get_grid(self):
        # Retorna la forma actual basada en la rotación
        rotated = [list(row) for row in self.shape]
        for _ in range(self.rotation):
            rotated = [list(col)[::-1] for col in zip(*rotated)]
        return rotated

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def rotate(self):
        # Rotación simple 90 grados
        self.rotation = (self.rotation + 1) % 4
        # Aplicar rotación a la matriz
        self.shape = [list(row) for row in zip(*self.shape[::-1])]
        
        # Lógica cuántica: Al rotar, hay una pequeña probabilidad de superposición
        if not self.superposition and random.random() < 0.1:
            self.superposition = True
            # Cambiar ligeramente la forma visualmente (simulada por color o tamaño en lógica futura)
            # Aquí simulamos que la pieza es "inestable"
            self.color = WHITE  # Luz blanca de superposición

    def collapse(self):
        """Colapsa la superposición a un estado definido (forma y color fijos)."""
        self.superposition = False
        # Re-evaluar forma y color aleatoriamente para el estado colapsado
        shape_idx = random.randint(0, len(SHAPES) - 1)
        self.shape = SHAPES[shape_idx]
        self.color = COLORS[shape_idx]
        self.rotation = 0

class TetrisGrid:
    def __init__(self):
        self.grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.locked_pieces = [] # Piezas que ya se han colapsado y permanecen
    
    def add_piece(self, piece):
        shape = piece.get_grid()
        for y, row in enumerate(shape):
            for x, value in enumerate(row):
                if value:
                    grid_x = piece.x + x
                    grid_y = piece.y + y
                    if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
                        # Lógica cuántica: Si la celda está superpuesta y la pieza colapsa
                        # o si choca con otra pieza existente.
                        if self.grid[grid_y][grid_x] is not None:
                            if piece.superposition:
                                # Colisión: El estado superpuesto debe colapsar y fundirse
                                self.grid[grid_y][grid_x] = (piece.color, piece.shape) # Fusiona colores
                                piece.collapse()
                                piece.y = grid_y - len(shape) + 1
                                piece.x = grid_x - len(shape[0]) + 1
                                return True # Colisión exitosa (absorbida)
                            else:
                                # Colisión normal
                                piece.collapse()
                                piece.y = grid_y - len(shape) + 1
                                piece.x = grid_x - len(shape[0]) + 1
                                return True
                        else:
                            self.grid[grid_y][grid_x] = (piece.color, piece.shape)
        return False

    def can_move(self, piece, dx, dy):
        shape = piece.get_grid()
        for y, row in enumerate(shape):
            for x, value in enumerate(row):
                if value:
                    new_x = piece.x + x + dx
                    new_y = piece.y + y + dy
                    if 0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT:
                        if self.grid[new_y][new_x] is not None:
                            return False
        return True

    def lock_piece(self, piece):
        shape = piece.get_grid()
        for y, row in enumerate(shape):
            for x, value in enumerate(row):
                if value:
                    grid_x = piece.x + x
                    grid_y = piece.y + y
                    if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
                        self.grid[grid_y][grid_x] = (piece.color, piece.shape)

    def clear_lines(self):
        lines_cleared = 0
        for y in range(GRID_HEIGHT):
            if all(cell is not None for cell in self.grid[y]):
                del self.grid[y]
                self.grid.insert(0, [None for _ in range(GRID_WIDTH)])
                lines_cleared += 1
        return lines_cleared

    def spawn_new_piece(self):
        piece = QuantumPiece()
        if not self.can_move(piece, 0, 0):
            return None
        return piece

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Quantum Tetris")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.reset_game()

    def reset_game(self):
        self.grid = TetrisGrid()
        self.piece = self.grid.spawn_new_piece()
        self.score = 0
        self.level = 1
        self.fall_time = 0
        self.fall_speed = 500 # ms
        self.game_over = False

    def draw_grid(self):
        # Dibujar fondo
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                rect = pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                pygame.draw.rect(self.screen, BLACK, rect, 1)
                
                if self.grid.grid[y][x] is not None:
                    color, shape = self.grid.grid[y][x]
                    # Dibujar bloque colapsado
                    pygame.draw.rect(self.screen, color, rect)
                    # Efecto de "onda" si es superpuesto (simulado por transparencia o borde)
                    # Aquí dibujamos el bloque sólido ya que el colapso lo hace fijo.
                elif self.piece and self.piece.superposition and self.piece.y == y and self.piece.x == x:
                    # Dibujar pieza en superposición (efecto fantasma)
                    alpha = 50
                    if self.piece.shape[y - self.piece.y][x - self.piece.x]:
                        surface = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
                        surface.set_alpha(alpha)
                        surface.fill(self.piece.color)
                        self.screen.blit(surface, (x * BLOCK_SIZE, y * BLOCK_SIZE))

    def draw_piece(self):
        if not self.piece:
            return
        
        shape = self.piece.get_grid()
        for y, row in enumerate(shape):
            for x, value in enumerate(row):
                if value:
                    px = self.piece.x * BLOCK_SIZE
                    py = self.piece.y * BLOCK_SIZE
                    bx = x * BLOCK_SIZE
                    by = y * BLOCK_SIZE
                    
                    rect = pygame.Rect(px + bx, py + by, BLOCK_SIZE, BLOCK_SIZE)
                    
                    if self.piece.superposition:
                        # Dibujar borde brillante para indicar superposición
                        pygame.draw.rect(self.screen, self.piece.color, rect, 3)
                        pygame.draw.circle(self.screen, WHITE, (px + bx + BLOCK_SIZE//2, py + by + BLOCK_SIZE//2), 4)
                    else:
                        pygame.draw.rect(self.screen, self.piece.color, rect)
                        pygame.draw.rect(self.screen, GRAY, rect, 1)

    def draw_score(self):
        score_text = self.font.render(f"Puntos: {self.score}", True, WHITE)
        level_text = self.font.render(f"Nivel: {self.level}", True, WHITE)
        superposition_text = self.font.render(f"Estados Cuánticos: {sum(1 for r in self.grid.grid for c in r if c is not None and isinstance(c, tuple) and c[0] == WHITE)}", True, MAGENTA)
        
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(level_text, (10, 50))
        self.screen.blit(superposition_text, (10, 90))

    def draw_game_over(self):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        text = self.font.render("GAME OVER - Presiona R para reiniciar", True, RED)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(text, text_rect)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if self.grid.can_move(self.piece, -1, 0):
                        self.piece.move(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    if self.grid.can_move(self.piece, 1, 0):
                        self.piece.move(1, 0)
                elif event.key == pygame.K_DOWN:
                    if self.grid.can_move(self.piece, 0, 1):
                        self.piece.move(0, 1)
                elif event.key == pygame.K_UP:
                    self.piece.rotate()
                    if not self.grid.can_move(self.piece, 0, 0):
                        # Intentar colapsar si la rotación es inválida
                        self.piece.collapse()
                elif event.key == pygame.K_SPACE:
                    # Bajar rápido
                    while self.grid.can_move(self.piece, 0, 1):
                        self.piece.move(0, 1)
                elif event.key == pygame.K_r and self.game_over:
                    self.reset_game()
        return True

    def update(self, dt):
        if self.game_over:
            return

        self.fall_time += dt
        if self.fall_time >= self.fall_speed:
            self.fall_time = 0
            if not self.grid.can_move(self.piece, 0, 1):
                self.grid.lock_piece(self.piece)
                self.grid.clear_lines()
                
                new_piece = self.grid.spawn_new_piece()
                if new_piece is None:
                    self.game_over = True
                else:
                    self.piece = new_piece

    def draw(self):
        self.screen.fill(BLACK)
        self.draw_grid()
        self.draw_piece()
        self.draw_score()
        if self.game_over:
            self.draw_game_over()
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS)
            running = self.handle_events()
            self.update(dt)
            self.draw()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()