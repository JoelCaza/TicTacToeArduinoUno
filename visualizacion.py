# visualizacion.py
import cv2
import numpy as np
from deteccion_figuras import dibujar_x

def dibujar_tablero_visualizacion(tablero, cuadricula, imagen_visualizacion):
    """Dibuja el tablero en la ventana de visualización"""
    imagen_visualizacion[:] = (255, 255, 255)  # Fondo blanco

    for celda in cuadricula:
        cv2.rectangle(imagen_visualizacion, (celda[0], celda[1]), (celda[2], celda[3]), (0, 0, 0), 2)

    for i, marca in enumerate(tablero):
        if marca == 'O':
            centro_x = (cuadricula[i][0] + cuadricula[i][2]) // 2
            centro_y = (cuadricula[i][1] + cuadricula[i][3]) // 2
            radio = min(cuadricula[i][2] - cuadricula[i][0], cuadricula[i][3] - cuadricula[i][1]) // 3
            cv2.circle(imagen_visualizacion, (centro_x, centro_y), radio, (255, 0, 0), 2)
        elif marca == 'X':
            dibujar_x(imagen_visualizacion, cuadricula[i])

    return imagen_visualizacion