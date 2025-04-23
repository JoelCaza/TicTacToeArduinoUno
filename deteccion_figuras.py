# deteccion_figuras.py
import cv2
import numpy as np

def detectar_circulos(frame, celda):
    """Detecta si hay un círculo en una celda específica"""
    x_min, y_min, x_max, y_max = celda
    celda_img = frame[y_min:y_max, x_min:x_max]

    if celda_img.size == 0:
        return None, False

    gris = cv2.cvtColor(celda_img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gris, (5, 5), 0)

    circulos = cv2.HoughCircles(
        blur, cv2.HOUGH_GRADIENT, dp=1, minDist=20,
        param1=50, param2=30,
        minRadius=min(celda_img.shape[0], celda_img.shape[1])//6,
        maxRadius=min(celda_img.shape[0], celda_img.shape[1])//2
    )

    if circulos is not None:
        return circulos[0], True

    return None, False

def dibujar_x(imagen, celda, color=(0, 0, 255), grosor=3):
    """Dibuja una X en la celda especificada"""
    x_min, y_min, x_max, y_max = celda
    centro_x = (x_min + x_max) // 2
    centro_y = (y_min + y_max) // 2
    lado = min(x_max - x_min, y_max - y_min) // 3

    cv2.line(imagen, (centro_x - lado, centro_y - lado),
             (centro_x + lado, centro_y + lado), color, grosor)
    cv2.line(imagen, (centro_x + lado, centro_y - lado),
             (centro_x - lado, centro_y + lado), color, grosor)

    return imagen