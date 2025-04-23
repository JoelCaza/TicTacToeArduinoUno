# logica_juego.py
import random
import math
import cv2

def verificar_ganador(tablero):
    lineas_ganadoras = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Filas
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columnas
        [0, 4, 8], [2, 4, 6]             # Diagonales
    ]
    for linea in lineas_ganadoras:
        if tablero[linea[0]] == tablero[linea[1]] == tablero[linea[2]] and tablero[linea[0]] != ' ':
            # Devolver el ganador y la línea ganadora (índices del tablero)
            return tablero[linea[0]], linea
    return None, None

def tablero_lleno(tablero):
    return ' ' not in tablero

def movimientos_disponibles(tablero):
    return [i for i, espacio in enumerate(tablero) if espacio == ' ']

def mejor_movimiento_ia(tablero, dificultad):
    if dificultad == "facil":
        return movimiento_aleatorio(tablero)
    elif dificultad == "dificil":
        return movimiento_inteligente(tablero)
    elif dificultad == "imposible":
        return movimiento_minimax(tablero)
    return movimiento_aleatorio(tablero)

def movimiento_aleatorio(tablero):
    return random.choice(movimientos_disponibles(tablero))

def movimiento_inteligente(tablero):
    # Primero intenta ganar
    for movimiento in movimientos_disponibles(tablero):
        tablero_temporal = list(tablero)
        tablero_temporal[movimiento] = 'X'
        if verificar_ganador(tablero_temporal)[0] == 'X':
            return movimiento
    # Luego intenta bloquear al jugador
    for movimiento in movimientos_disponibles(tablero):
        tablero_temporal = list(tablero)
        tablero_temporal[movimiento] = 'O'
        if verificar_ganador(tablero_temporal)[0] == 'O':
            return movimiento
    # Si no hay movimientos para ganar o bloquear, elige aleatoriamente
    return movimiento_aleatorio(tablero)

def movimiento_minimax(tablero):
    mejor_puntaje = -math.inf
    mejor_movimiento = None
    for movimiento in movimientos_disponibles(tablero):
        tablero[movimiento] = 'X'
        puntaje = minimax(tablero, 0, False, -math.inf, math.inf)
        tablero[movimiento] = ' '
        if puntaje > mejor_puntaje:
            mejor_puntaje = puntaje
            mejor_movimiento = movimiento
    return mejor_movimiento

def minimax(tablero, profundidad, es_maximizando, alfa, beta):
    ganador, _ = verificar_ganador(tablero)
    if ganador == 'X':
        return 1
    if ganador == 'O':
        return -1
    if tablero_lleno(tablero):
        return 0

    if es_maximizando:
        mejor_puntaje = -math.inf
        for movimiento in movimientos_disponibles(tablero):
            tablero[movimiento] = 'X'
            puntaje = minimax(tablero, profundidad + 1, False, alfa, beta)
            tablero[movimiento] = ' '
            mejor_puntaje = max(mejor_puntaje, puntaje)
            alfa = max(alfa, mejor_puntaje)
            if beta <= alfa:
                break
        return mejor_puntaje
    else:
        mejor_puntaje = math.inf
        for movimiento in movimientos_disponibles(tablero):
            tablero[movimiento] = 'O'
            puntaje = minimax(tablero, profundidad + 1, True, alfa, beta)
            tablero[movimiento] = ' '
            mejor_puntaje = min(mejor_puntaje, puntaje)
            beta = min(beta, mejor_puntaje)
            if beta <= alfa:
                break
        return mejor_puntaje

def dibujar_linea_ganadora(frame, cuadricula, linea_indices, color, grosor):
    if linea_indices:
        puntos_inicio_celda = cuadricula[linea_indices[0]]
        puntos_fin_celda = cuadricula[linea_indices[-1]]

        inicio_x = (puntos_inicio_celda[0] + puntos_inicio_celda[2]) // 2
        inicio_y = (puntos_inicio_celda[1] + puntos_inicio_celda[3]) // 2
        fin_x = (puntos_fin_celda[0] + puntos_fin_celda[2]) // 2
        fin_y = (puntos_fin_celda[1] + puntos_fin_celda[3]) // 2
        cv2.line(frame, (inicio_x, inicio_y), (fin_x, fin_y), color, grosor)