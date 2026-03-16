import pygame
import random
import sys
import time

# Inicializar Pygame
pygame.init()

# --- Colores ---
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
VERDE = (0, 255, 0)
VERDE_OSCURO = (0, 200, 0)
VERDE_BRILLANTE = (0, 255, 128)
ROJO = (255, 0, 0)
AZUL = (0, 0, 255)
AMARILLO = (255, 255, 0)
AZUL_CLARO = (135, 206, 235)
GRIS_OSCURO = (50, 50, 50)

# --- Configuración de la pantalla ---
ANCHO = 600
ALTO = 400
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption('Snake Game V2 - Mejorado')

# Reloj para controlar la velocidad
reloj = pygame.time.Clock()

# Tamaño del bloque del snake
TAMANO_BLOQUE = 20

# --- Direcciones ---
DIR = 'RIGHT'

# --- Snake inicial ---
snake = [(100, 100), (80, 100), (60, 100)]

# Comida
comida = (200, 200)

# Puntuación y Estado del Juego
puntuacion = 0
velocidad = 10  # FPS inicial
estado_juego = 'menu'  # 'menu', 'jugando', 'gameover'

# Fuente de texto
fuente = pygame.font.SysFont('arial', 24)
fuente_grande = pygame.font.SysFont('arial', 48)
fuente_menu = pygame.font.SysFont('arial', 36)
fuente_pequena = pygame.font.SysFont('arial', 20)

# --- Función para generar comida ---
def generar_comida():
    global comida
    while True:
        x = random.randint(0, (ANCHO - TAMANO_BLOQUE) // TAMANO_BLOQUE) * TAMANO_BLOQUE
        y = random.randint(0, (ALTO - TAMANO_BLOQUE) // TAMANO_BLOQUE) * TAMANO_BLOQUE
        comida = (x, y)
        # Asegurar que la comida no aparezca sobre el snake
        if comida not in snake:
            break

# --- Dibujo de la serpiente amigable con ASCII ---
def dibujar_serpiente_ascii():
    texto_serpiente = """
       ,      ,
      /        \
     |          |
      \        /
       `------'
     /        \
    |          |
     |          |
      \        /
       `------'
      |  O  |
      |    |
      |    |
      |    |
      |    |
      |    |
      |    |
      |    |
      |    |
      |    |
    _/      \_
   (          )
    \        /
     `------'
    """
    return texto_serpiente

# --- Menú principal ---
def menu_principal():
    global estado_juego
    while estado_juego == 'menu':
        pantalla.fill(NEGRO)
        
        # Dibujar la serpiente amigable
        texto_serpiente = dibujar_serpiente_ascii()
        lines = texto_serpiente.split('\n')
        y_pos = ALTO // 2 - 20
        for line in lines:
            if line.strip():
                texto = fuente_menu.render(line, True, VERDE_BRILLANTE)
                rect = texto.get_rect(center=(ANCHO // 2, y_pos))
                pantalla.blit(texto, rect)
                y_pos += 30
        
        # Título del juego
        titulo = fuente_grande.render('SNAKE GAME', True, VERDE)
        titulo_rect = titulo.get_rect(center=(ANCHO // 2, 50))
        pantalla.blit(titulo, titulo_rect)
        
        subtitulo = fuente.render('Versión 2.0 - Edición Amigable', True, AMARILLO)
        subtitulo_rect = subtitulo.get_rect(center=(ANCHO // 2, 100))
        pantalla.blit(subtitulo, subtitulo_rect)
        
        # Opciones de menú
        opciones = ['FÁCIL (15 FPS)', 'MEDIO (10 FPS)', 'DIFÍCIL (7 FPS)', 'SALIR (ESC)']
        y_menu = 180
        for opcion in opciones:
            if opcion == 'SALIR (ESC)':
                color = ROJO
            else:
                color = AMARILLO
            texto_opcion = fuente_menu.render(opcion, True, color)
            texto_opcion_rect = texto_opcion.get_rect(center=(ANCHO // 2, y_menu))
            pantalla.blit(texto_opcion, texto_opcion_rect)
            y_menu += 50
        
        # Instrucciones
        instrucciones = fuente_pequena.render('Usa las flechas del teclado para moverte', True, GRIS_OSCURO)
        instrucciones_rect = instrucciones.get_rect(center=(ANCHO // 2, ALTO - 30))
        pantalla.blit(instrucciones, instrucciones_rect)
        
        pygame.display.flip()
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                sys.exit()
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    estado_juego = 'menu'
                    break
                elif evento.key == pygame.K_1:
                    velocidad = 15
                    estado_juego = 'jugando'
                    generar_comida()
                elif evento.key == pygame.K_2:
                    velocidad = 10
                    estado_juego = 'jugando'
                    generar_comida()
                elif evento.key == pygame.K_3:
                    velocidad = 7
                    estado_juego = 'jugando'
                    generar_comida()

# --- Bucle principal del juego ---
def juego():
    global snake, comida, DIR, puntuacion, velocidad, estado_juego

    while True:
        if estado_juego == 'gameover':
            # Pantalla de Game Over
            pantalla.fill(NEGRO)
            texto_gameover = fuente_grande.render('GAME OVER', True, ROJO)
            texto_punt = fuente.render(f'Puntuación: {puntuacion}', True, BLANCO)
            texto_reiniciar = fuente.render('Presiona ENTER para reiniciar', True, AMARILLO)
            texto_salir = fuente.render('O ESC para salir', True, BLANCO)
            
            centro_x = pantalla.get_width() // 2
            centro_y = pantalla.get_height() // 2
            
            pantalla.blit(texto_gameover, (centro_x - 150, centro_y - 50))
            pantalla.blit(texto_punt, (centro_x - 100, centro_y + 10))
            pantalla.blit(texto_reiniciar, (centro_x - 150, centro_y + 60))
            pantalla.blit(texto_salir, (centro_x - 150, centro_y + 100))
            
            pygame.display.flip()
            
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    sys.exit()
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        estado_juego = 'menu'
                    elif evento.key == pygame.K_RETURN:
                        # Reiniciar juego
                        snake = [(100, 100), (80, 100), (60, 100)]
                        puntuacion = 0
                        velocidad = 10
                        estado_juego = 'jugando'
                        generar_comida()
                        continue
        else:
            # Bucle de juego normal
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
                        estado_juego = 'menu'
            
            # Mover el snake
            if DIR == 'UP':
                nueva_cabeza = (snake[0][0], snake[0][1] - TAMANO_BLOQUE)
            elif DIR == 'DOWN':
                nueva_cabeza = (snake[0][0], snake[0][1] + TAMANO_BLOQUE)
            elif DIR == 'LEFT':
                nueva_cabeza = (snake[0][0] - TAMANO_BLOQUE, snake[0][1])
            elif DIR == 'RIGHT':
                nueva_cabeza = (snake[0][0] + TAMANO_BLOQUE, snake[0][1])
            
            snake.insert(0, nueva_cabeza)
            
            # Verificar si comió
            if nueva_cabeza == comida:
                puntuacion += 10
                generar_comida()
            else:
                snake.pop()
            
            # Verificar colisiones
            if (nueva_cabeza[0] < 0 or nueva_cabeza[0] >= ANCHO or 
                nueva_cabeza[1] < 0 or nueva_cabeza[1] >= ALTO or 
                nueva_cabeza in snake[1:]):
                estado_juego = 'gameover'
            
            # Dibujar todo
            pantalla.fill(NEGRO)
            
            # Dibujar comida
            pygame.draw.rect(pantalla, ROJO, (comida[0], comida[1], TAMANO_BLOQUE, TAMANO_BLOQUE))
            pygame.draw.circle(pantalla, AMARILLO, (comida[0] + TAMANO_BLOQUE//2, comida[1] + TAMANO_BLOQUE//2, TAMANO_BLOQUE//3))
            
            # Dibujar snake
            for i, segmento in enumerate(snake):
                color = VERDE if i == 0 else VERDE_OSCURO
                pygame.draw.rect(pantalla, color, (segmento[0], segmento[1], TAMANO_BLOQUE, TAMANO_BLOQUE))
                pygame.draw.rect(pantalla, BLANCO, (segmento[0], segmento[1], TAMANO_BLOQUE, TAMANO_BLOQUE), 1)
            
            # Dibujar puntuación
            texto_punt = fuente.render(f'Puntuación: {puntuacion}', True, AMARILLO)
            pantalla.blit(texto_punt, (10, 10))
            
            pygame.display.flip()
            reloj.tick(velocidad)

# --- Función de bienvenida ---
def bienvenida():
    pantalla.fill(NEGRO)
    texto_bienvenida = fuente_grande.render('¡Bienvenido a Snake Game!', True, VERDE_BRILLANTE)
    pantalla.blit(texto_bienvenida, (ANCHO//2 - 200, ALTO//2 - 30))
    
    texto_instruccion = fuente.render('Presiona ENTER para ver el menú', True, AMARILLO)
    texto_instruccion_rect = texto_instruccion.get_rect(center=(ANCHO // 2, ALTO // 2 + 30))
    pantalla.blit(texto_instruccion, texto_instruccion_rect)
    
    pygame.display.flip()
    
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            sys.exit()
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_RETURN:
                estado_juego = 'menu'
                break

# --- Iniciar el juego ---
if __name__ == '__main__':
    bienvenida()
    menu_principal()
    juego()
