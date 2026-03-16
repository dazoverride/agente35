import pygame
import random
import sys

# Inicializar Pygame
pygame.init()

# Colores
BLANC0 = (255, 255, 255)
NEGRO = (0, 0, 0)
VERDE = (0, 255, 0)
ROJO = (255, 0, 0)
AZUL = (0, 0, 255)

# Configuración de la pantalla
ANCHO = 600
ALTO = 400
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption('Snake - Dani Edition')

# Reloj para controlar la velocidad
reloj = pygame.time.Clock()
FPS = 10

# Tamaño del bloque del snake
TAMANO_BLOQUE = 20

# Dirección inicial
DIR = 'RIGHT'

# Snake inicial
snake = [(100, 100), (80, 100), (60, 100)]

# Comida
comida = (200, 200)

# Puntuación
puntuacion = 0

# Fuente de texto
fuente = pygame.font.SysFont('arial', 24)

# Función para generar comida en posición aleatoria
def generar_comida():
    global comida
    while True:
        x = random.randint(0, (ANCHO - TAMANO_BLOQUE) // TAMANO_BLOQUE) * TAMANO_BLOQUE
        y = random.randint(0, (ALTO - TAMANO_BLOQUE) // TAMANO_BLOQUE) * TAMANO_BLOQUE
        comida = (x, y)
        # Asegurar que la comida no aparezca sobre el snake
        if comida not in snake:
            break

# Función principal del juego
def juego():
    global snake, comida, DIR, puntuacion
    
    while True:
        # Eventos
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                sys.exit()
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_UP and DIR != 'DOWN':
                    DIR = 'UP'
                elif evento.key == pygame.K_DOWN and DIR != 'UP':
                    DIR = 'DOWN'
                elif evento.key == pygame.K_LEFT and DIR != 'RIGHT':
                    DIR = 'LEFT'
                elif evento.key == pygame.K_RIGHT and DIR != 'LEFT':
                    DIR = 'RIGHT'
                elif evento.key == pygame.K_ESCAPE:
                    sys.exit()
        
        # Mover el snake
        cabeza = snake[0]
        if DIR == 'UP':
            nueva_cabeza = (cabeza[0], cabeza[1] - TAMANO_BLOQUE)
        elif DIR == 'DOWN':
            nueva_cabeza = (cabeza[0], cabeza[1] + TAMANO_BLOQUE)
        elif DIR == 'LEFT':
            nueva_cabeza = (cabeza[0] - TAMANO_BLOQUE, cabeza[1])
        elif DIR == 'RIGHT':
            nueva_cabeza = (cabeza[0] + TAMANO_BLOQUE, cabeza[1])
        
        snake.insert(0, nueva_cabeza)
        
        # Comprobar si come la comida
        if nueva_cabeza == comida:
            puntuacion += 10
            generar_comida()
        else:
            snake.pop()
        
        # Comprobar colisiones con paredes
        if (nueva_cabeza[0] < 0 or nueva_cabeza[0] >= ANCHO or
            nueva_cabeza[1] < 0 or nueva_cabeza[1] >= ALTO or
            nueva_cabeza in snake[1:]):
            pygame.display.quit()
            pygame.quit()
            print(f'¡Juego terminado! Puntuación final: {puntuacion}')
            sys.exit()
        
        # Dibujar
        pantalla.fill(NEGRO)
        
        # Dibujar snake
        for i, segmento in enumerate(snake):
            color = VERDE if i == 0 else (0, 200, 0)
            pygame.draw.rect(pantalla, color, (*segmento, TAMANO_BLOQUE, TAMANO_BLOQUE))
            pygame.draw.rect(pantalla, BLANC0, (*segmento, TAMANO_BLOQUE, TAMANO_BLOQUE), 1)
        
        # Dibujar comida
        pygame.draw.rect(pantalla, ROJO, (*comida, TAMANO_BLOQUE, TAMANO_BLOQUE))
        pygame.draw.rect(pantalla, BLANC0, (*comida, TAMANO_BLOQUE, TAMANO_BLOQUE), 1)
        
        # Dibujar puntuación
        texto_puntuacion = fuente.render(f'Puntuación: {puntuacion}', True, BLANC0)
        pantalla.blit(texto_puntuacion, (10, 10))
        
        # Actualizar pantalla
        pygame.display.flip()
        
        # Controlar velocidad
        reloj.tick(FPS)

# Iniciar el juego
if __name__ == '__main__':
    generar_comida()
    juego()
