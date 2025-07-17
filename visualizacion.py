import cv2
import numpy as np

def dibujar_x_en_visualizacion(img, celda, color=(50, 50, 200), grosor=3): # Azul oscuro
    """Dibuja una 'X' dentro de una celda específica en la imagen."""
    x1, y1, x2, y2 = celda
    pad = (x2 - x1) // 6
    cv2.line(img, (x1 + pad, y1 + pad), (x2 - pad, y2 - pad), color, grosor)
    cv2.line(img, (x2 - pad, y1 + pad), (x1 + pad, y2 - pad), color, grosor)

def dibujar_tablero_visualizacion(tablero, cuadricula, imagen_visualizacion):
    """Dibuja el tablero en la ventana de visualización"""
    imagen_visualizacion[:] = (240, 240, 240)  # Fondo blanco grisáceo

    # Dibujar la cuadrícula del tablero
    for celda in cuadricula:
        cv2.rectangle(imagen_visualizacion, (celda[0], celda[1]), (celda[2], celda[3]), (50, 50, 50), 2) # Líneas más oscuras

    # Dibujar las marcas 'O' y 'X'
    for i, marca in enumerate(tablero):
        if marca == 'O':
            centro_x = (cuadricula[i][0] + cuadricula[i][2]) // 2
            centro_y = (cuadricula[i][1] + cuadricula[i][3]) // 2
            radio = min(cuadricula[i][2] - cuadricula[i][0], cuadricula[i][3] - cuadricula[i][1]) // 3
            cv2.circle(imagen_visualizacion, (centro_x, centro_y), radio, (255, 120, 0), 3) # Naranja vibrante
        elif marca == 'X':
            dibujar_x_en_visualizacion(imagen_visualizacion, cuadricula[i], color=(50, 50, 200), grosor=3) # Azul oscuro

    return imagen_visualizacion