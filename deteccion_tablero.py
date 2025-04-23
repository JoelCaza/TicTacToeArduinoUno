# deteccion_tablero.py
import cv2
import numpy as np

def detectar_tablero(frame):
    """Detecta las líneas del tablero de Tic Tac Toe"""
    gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gris, (5, 5), 0)
    bordes = cv2.Canny(blur, 50, 150)
    bordes = cv2.dilate(bordes, np.ones((2, 2), np.uint8), iterations=1)
    lineas = cv2.HoughLinesP(bordes, 1, np.pi/180, threshold=100, minLineLength=100, maxLineGap=10)

    if lineas is None:
        return None, None, None, bordes

    h_lineas = []
    v_lineas = []

    for linea in lineas:
        x1, y1, x2, y2 = linea[0]
        if abs(x2 - x1) > abs(y2 - y1):
            h_lineas.append((x1, y1, x2, y2))
        else:
            v_lineas.append((x1, y1, x2, y2))

    h_agrupadas = agrupar_lineas(h_lineas)
    v_agrupadas = agrupar_lineas(v_lineas)

    h_finales = seleccionar_lineas_tablero(h_agrupadas, frame.shape[0])
    v_finales = seleccionar_lineas_tablero(v_agrupadas, frame.shape[1], eje='x')

    return h_finales, v_finales, frame.shape, bordes

def agrupar_lineas(lineas, umbral_distancia=30):
    """Agrupa líneas similares"""
    if not lineas:
        return []

    if abs(lineas[0][2] - lineas[0][0]) > abs(lineas[0][3] - lineas[0][1]):
        lineas_ordenadas = sorted(lineas, key=lambda l: (l[1] + l[3]) / 2)
    else:
        lineas_ordenadas = sorted(lineas, key=lambda l: (l[0] + l[2]) / 2)

    grupos = []
    grupo_actual = [lineas_ordenadas[0]]

    for i in range(1, len(lineas_ordenadas)):
        l1 = lineas_ordenadas[i-1]
        l2 = lineas_ordenadas[i]

        if abs(l1[2] - l1[0]) > abs(l1[3] - l1[1]):
            dist = abs((l1[1] + l1[3]) / 2 - (l2[1] + l2[3]) / 2)
        else:
            dist = abs((l1[0] + l1[2]) / 2 - (l2[0] + l2[2]) / 2)

        if dist < umbral_distancia:
            grupo_actual.append(lineas_ordenadas[i])
        else:
            grupos.append(grupo_actual)
            grupo_actual = [lineas_ordenadas[i]]

    grupos.append(grupo_actual)

    lineas_promediadas = []
    for grupo in grupos:
        x1_prom = sum(l[0] for l in grupo) / len(grupo)
        y1_prom = sum(l[1] for l in grupo) / len(grupo)
        x2_prom = sum(l[2] for l in grupo) / len(grupo)
        y2_prom = sum(l[3] for l in grupo) / len(grupo)
        lineas_promediadas.append((int(x1_prom), int(y1_prom), int(x2_prom), int(y2_prom)))

    return lineas_promediadas

def seleccionar_lineas_tablero(lineas, dimension_max, eje='y'):
    """Selecciona las dos líneas óptimas para formar un tablero 3x3"""
    if not lineas or len(lineas) < 2:
        if eje == 'y':
            tercio = dimension_max // 3
            return [(0, tercio, dimension_max, tercio),
                    (0, 2*tercio, dimension_max, 2*tercio)]
        else:
            tercio = dimension_max // 3
            return [(tercio, 0, tercio, dimension_max),
                    (2*tercio, 0, 2*tercio, dimension_max)]

    if eje == 'y':
        y_tercio = dimension_max / 3
        y_dos_tercios = 2 * dimension_max / 3

        mejor_linea1 = lineas[0]
        mejor_linea2 = lineas[-1]
        mejor_dist1 = float('inf')
        mejor_dist2 = float('inf')

        for linea in lineas:
            y_medio = (linea[1] + linea[3]) / 2
            dist1 = abs(y_medio - y_tercio)
            dist2 = abs(y_medio - y_dos_tercios)

            if dist1 < mejor_dist1:
                mejor_dist1 = dist1
                mejor_linea1 = linea

            if dist2 < mejor_dist2:
                mejor_dist2 = dist2
                mejor_linea2 = linea

        if (mejor_linea1[1] + mejor_linea1[3]) > (mejor_linea2[1] + mejor_linea2[3]):
            mejor_linea1, mejor_linea2 = mejor_linea2, mejor_linea1

        return [mejor_linea1, mejor_linea2]

    else:
        x_tercio = dimension_max / 3
        x_dos_tercios = 2 * dimension_max / 3

        mejor_linea1 = lineas[0]
        mejor_linea2 = lineas[-1]
        mejor_dist1 = float('inf')
        mejor_dist2 = float('inf')

        for linea in lineas:
            x_medio = (linea[0] + linea[2]) / 2
            dist1 = abs(x_medio - x_tercio)
            dist2 = abs(x_medio - x_dos_tercios)

            if dist1 < mejor_dist1:
                mejor_dist1 = dist1
                mejor_linea1 = linea

            if dist2 < mejor_dist2:
                mejor_dist2 = dist2
                mejor_linea2 = linea

        if (mejor_linea1[0] + mejor_linea1[2]) > (mejor_linea2[0] + mejor_linea2[2]):
            mejor_linea1, mejor_linea2 = mejor_linea2, mejor_linea1

        return [mejor_linea1, mejor_linea2]

def crear_cuadricula(h_lineas, v_lineas, forma_imagen):
    """Crea una cuadrícula 3x3 a partir de las líneas detectadas"""
    altura, ancho = forma_imagen[:2]

    y_coords = [0]
    for linea in h_lineas:
        y_coords.append((linea[1] + linea[3]) // 2)
    y_coords.append(altura)

    x_coords = [0]
    for linea in v_lineas:
        x_coords.append((linea[0] + linea[2]) // 2)
    x_coords.append(ancho)

    celdas = []
    for i in range(3):
        for j in range(3):
            celda = (x_coords[j], y_coords[i], x_coords[j+1], y_coords[i+1])
            celdas.append(celda)

    return celdas

def dibujar_tablero(frame, h_lineas, v_lineas):
    """Dibuja las líneas del tablero en la imagen"""
    resultado = frame.copy()

    for x1, y1, x2, y2 in h_lineas:
        cv2.line(resultado, (x1, y1), (x2, y2), (0, 255, 0), 2)

    for x1, y1, x2, y2 in v_lineas:
        cv2.line(resultado, (x1, y1), (x2, y2), (0, 255, 0), 2)

    return resultado