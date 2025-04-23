import cv2
import numpy as np
import time
import random

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

def dibujar_tablero(frame, h_lineas, v_lineas):
    """Dibuja las líneas del tablero en la imagen"""
    resultado = frame.copy()
    
    for x1, y1, x2, y2 in h_lineas:
        cv2.line(resultado, (x1, y1), (x2, y2), (0, 255, 0), 2)
    
    for x1, y1, x2, y2 in v_lineas:
        cv2.line(resultado, (x1, y1), (x2, y2), (0, 255, 0), 2)
    
    return resultado

def dibujar_x(imagen, celda):
    """Dibuja una X en la celda especificada"""
    x_min, y_min, x_max, y_max = celda
    centro_x = (x_min + x_max) // 2
    centro_y = (y_min + y_max) // 2
    lado = min(x_max - x_min, y_max - y_min) // 3
    
    cv2.line(imagen, (centro_x - lado, centro_y - lado), 
             (centro_x + lado, centro_y + lado), (0, 0, 255), 3)
    cv2.line(imagen, (centro_x + lado, centro_y - lado), 
             (centro_x - lado, centro_y + lado), (0, 0, 255), 3)
    
    return imagen

def verificar_ganador(tablero):
    """Verifica si hay un ganador en el tablero actual"""
    matriz = [tablero[i:i+3] for i in range(0, 9, 3)]

    # Verificar filas
    for i in range(3):
        if matriz[i][0] == matriz[i][1] == matriz[i][2] != ' ':
            return matriz[i][0], [(i, 0), (i, 1), (i, 2)]

    # Verificar columnas
    for j in range(3):
        if matriz[0][j] == matriz[1][j] == matriz[2][j] != ' ':
            return matriz[0][j], [(0, j), (1, j), (2, j)]

    # Verificar diagonales
    if matriz[0][0] == matriz[1][1] == matriz[2][2] != ' ':
        return matriz[0][0], [(0, 0), (1, 1), (2, 2)]
    if matriz[0][2] == matriz[1][1] == matriz[2][0] != ' ':
        return matriz[0][2], [(0, 2), (1, 1), (2, 0)]

    # No hay ganador
    return None, []


def tablero_lleno(tablero):
    """Verifica si el tablero está lleno"""
    return ' ' not in tablero

def mejor_movimiento_ia(tablero):
    """Determina el mejor movimiento para la IA usando el algoritmo minimax"""
    for i in range(9):
        if tablero[i] == ' ':
            tablero[i] = 'X'
            ganador, _ = verificar_ganador(tablero)
            tablero[i] = ' '
            
            if ganador == 'X':
                return i
    
    for i in range(9):
        if tablero[i] == ' ':
            tablero[i] = 'O'
            ganador, _ = verificar_ganador(tablero)
            tablero[i] = ' '
            
            if ganador == 'O':
                return i
    
    if tablero[4] == ' ':
        return 4
    
    esquinas = [0, 2, 6, 8]
    esquinas_disponibles = [i for i in esquinas if tablero[i] == ' ']
    if esquinas_disponibles:
        return random.choice(esquinas_disponibles)
    
    lados = [1, 3, 5, 7]
    lados_disponibles = [i for i in lados if tablero[i] == ' ']
    if lados_disponibles:
        return random.choice(lados_disponibles)
    
    return None

def dibujar_linea_ganadora(imagen, cuadricula, posiciones):
    """Dibuja una línea a través de la combinación ganadora"""
    if not posiciones:
        return imagen
    
    p1 = posiciones[0]
    p3 = posiciones[2]
    
    idx1 = p1[0] * 3 + p1[1]
    idx3 = p3[0] * 3 + p3[1]
    
    x1_min, y1_min, _, _ = cuadricula[idx1]
    _, _, x3_max, y3_max = cuadricula[idx3]
    
    centro_x1 = x1_min + (cuadricula[idx1][2] - x1_min) // 2
    centro_y1 = y1_min + (cuadricula[idx1][3] - y1_min) // 2
    centro_x3 = x3_max - (x3_max - cuadricula[idx3][0]) // 2
    centro_y3 = y3_max - (y3_max - cuadricula[idx3][1]) // 2
    
    cv2.line(imagen, (centro_x1, centro_y1), (centro_x3, centro_y3), (0, 255, 255), 3)
    return imagen

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

def main():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("No se pudo acceder a la cámara")
        return

    estado_tablero = [' '] * 9
    turno_jugador = True  # True para jugador, False para IA
    tiempo_espera = 0.5
    ultimo_tiempo = time.time()
    juego_terminado = False
    dibujando_circulo = [False] * 9
    tiempo_inicio_dibujo = [0] * 9
    historial_movimientos = []  # Almacenar el historial de movimientos
    contador_estabilidad = [0] * 9 #contador de estabilidad
    umbral_estabilidad = 5 #umbral de estabilidad
    tiempo_maximo_espera = 1 #tiempo máximo de espera en segundos
    tiempo_inicio_espera = [0] * 9 #tiempo de inicio de espera para cada celda

    # Crear ventana para la visualización del tablero
    imagen_visualizacion = np.zeros((480, 640, 3), np.uint8)

    print("=== Tic Tac Toe con cámara ===")
    print("1. Coloca un tablero frente a la cámara")
    print("2. Dibuja círculos (O) para jugar")
    print("3. La IA dibujará X en la pantalla")
    print("4. Presiona 'r' para reiniciar o 'q' para salir")

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Error al capturar el frame")
            break

        frame_procesado = frame.copy()

        h_lineas, v_lineas, forma, bordes = detectar_tablero(frame)

        if h_lineas is not None and v_lineas is not None:
            frame_procesado = dibujar_tablero(frame_procesado, h_lineas, v_lineas)
            cuadricula = crear_cuadricula(h_lineas, v_lineas, forma)

            tiempo_actual = time.time()
            if not juego_terminado and tiempo_actual - ultimo_tiempo > tiempo_espera:
                nuevo_estado = list(estado_tablero)

                for i, celda in enumerate(cuadricula):
                    circulos, circulo_detectado = detectar_circulos(frame, celda)
                    if circulo_detectado:
                        if not dibujando_circulo[i] and estado_tablero[i] == ' ':  # Verificar si la celda está vacía
                            contador_estabilidad[i] += 1
                            if contador_estabilidad[i] >= umbral_estabilidad:
                                nuevo_estado[i] = 'O'
                                dibujando_circulo[i] = True
                                contador_estabilidad[i] = 0 #resetear contador
                            if tiempo_inicio_espera[i] == 0:
                                tiempo_inicio_espera[i] = tiempo_actual #iniciar tiempo de espera
                        if circulos is not None:
                            x, y, r = circulos[0]
                            x_int, y_int, r_int = int(x), int(y), int(r)
                            cv2.circle(frame_procesado, (celda[0] + x_int, celda[1] + y_int), r_int, (255, 0, 0), 2)
                    else:
                        contador_estabilidad[i] = 0 #resetear contador si no se detecta circulo
                        tiempo_inicio_espera[i] = 0 #resetear tiempo de espera

                    #Verificar tiempo máximo de espera
                    if tiempo_inicio_espera[i] != 0 and tiempo_actual - tiempo_inicio_espera[i] > tiempo_maximo_espera:
                        contador_estabilidad[i] = 0 #resetear contador
                        tiempo_inicio_espera[i] = 0 #resetear tiempo de espera

                if nuevo_estado != estado_tablero:
                    estado_tablero = nuevo_estado
                    ultimo_tiempo = tiempo_actual
                    historial_movimientos.append((estado_tablero[:], cuadricula[:]))  # Guardar el estado del tablero y la cuadrícula

                    ganador, posiciones = verificar_ganador(estado_tablero)
                    if ganador:
                        print(f"¡{ganador} ha ganado!")
                        frame_procesado = dibujar_linea_ganadora(frame_procesado, cuadricula, posiciones)
                        cv2.putText(frame_procesado, f"{ganador} gana!", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                        juego_terminado = True
                    elif tablero_lleno(estado_tablero):
                        print("¡Empate!")
                        cv2.putText(frame_procesado, "Empate!", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                        juego_terminado = True
                    else:
                        if turno_jugador:
                            turno_jugador = False  # Cambiar turno a la IA
                            movimiento_ia = mejor_movimiento_ia(estado_tablero)
                            if movimiento_ia is not None:
                                estado_tablero[movimiento_ia] = 'X'
                                frame_procesado = dibujar_x(frame_procesado, cuadricula[movimiento_ia])
                                turno_jugador = True  # Cambiar turno al jugador
                                historial_movimientos.append((estado_tablero[:], cuadricula[:]))  # Guardar el estado del tablero y la cuadrícula

                                ganador, posiciones = verificar_ganador(estado_tablero)
                                if ganador:
                                    print(f"¡{ganador} ha ganado!")
                                    frame_procesado = dibujar_linea_ganadora(frame_procesado, cuadricula, posiciones)
                                    cv2.putText(frame_procesado, f"{ganador} gana!", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                                    juego_terminado = True
                                elif tablero_lleno(estado_tablero):
                                    print("¡Empate!")
                                    cv2.putText(frame_procesado, "Empate!", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                                    juego_terminado = True

                for i, celda in enumerate(cuadricula):
                    if estado_tablero[i] == 'X':
                        frame_procesado = dibujar_x(frame_procesado, celda)

                if juego_terminado:
                    # Mostrar el tablero final con el resultado en la pantalla de la cámara
                    for i, celda in enumerate(cuadricula):
                        if estado_tablero[i] == 'O':
                            circulos, circulo_detectado = detectar_circulos(frame, celda)
                            if circulo_detectado and circulos is not None:
                                x, y, r = circulos[0]
                                x_int, y_int, r_int = int(x), int(y), int(r)
                                cv2.circle(frame_procesado, (celda[0] + x_int, celda[1] + y_int), r_int, (255, 0, 0), 2)

                    # Actualizar la visualización del tablero antes del retraso
                    imagen_visualizacion = dibujar_tablero_visualizacion(estado_tablero, cuadricula, imagen_visualizacion)
                    cv2.imshow("Visualizacion del tablero", imagen_visualizacion)

                    if ganador:
                        cv2.putText(frame_procesado, f"{ganador} gana!", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                    else:
                        cv2.putText(frame_procesado, "Empate!", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

                    cv2.putText(frame_procesado, "Presiona 'r' para reiniciar", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

                    # Detener la captura de frames y mostrar el tablero final
                    cv2.imshow("Tic Tac Toe con camara", frame_procesado)
                    cv2.imshow("Canny", bordes)

                    time.sleep(10) #Delay de 10 segundos.

                    while True:
                        key = cv2.waitKey(1) & 0xFF
                        #Actualizar la visualización dentro del bucle de retraso
                        imagen_visualizacion = dibujar_tablero_visualizacion(estado_tablero, cuadricula, imagen_visualizacion)
                        cv2.imshow("Visualizacion del tablero", imagen_visualizacion)

                        if key == ord('r'):
                            estado_tablero = [' '] * 9
                            juego_terminado = False
                            dibujando_circulo = [False] * 9
                            tiempo_inicio_dibujo = [0] * 9
                            turno_jugador = True  # Reiniciar el turno al jugador
                            historial_movimientos = [] # Reinicia el historial
                            print("Juego reiniciado")
                            break
                        elif key == ord('q'):
                            cap.release()
                            cv2.destroyAllWindows()
                            return

                    if not juego_terminado:
                        continue  # Volver al bucle principal para reiniciar el juego
                else:
                    turno_texto = "Tu turno (O)" if turno_jugador else "Turno de la IA (X)"
                    cv2.putText(frame_procesado, turno_texto, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            # Actualizar la visualización del tablero
            imagen_visualizacion = dibujar_tablero_visualizacion(estado_tablero, cuadricula, imagen_visualizacion)

            cv2.imshow("Tic Tac Toe con camara", frame_procesado)
            cv2.imshow("Canny", bordes)
            cv2.imshow("Visualizacion del tablero", imagen_visualizacion)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                estado_tablero = [' '] * 9
                juego_terminado = False
                dibujando_circulo = [False] * 9
                tiempo_inicio_dibujo = [0] * 9
                turno_jugador = True  # Reiniciar el turno al jugador
                historial_movimientos = [] # Reinicia el historial
                print("Juego reiniciado")
        else:
            cv2.imshow("Canny", bordes)
            cv2.imshow("Tic Tac Toe con camara", frame_procesado)
            cv2.imshow("Visualizacion del tablero", imagen_visualizacion)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                estado_tablero = [' '] * 9
                juego_terminado = False
                dibujando_circulo = [False] * 9
                tiempo_inicio_dibujo = [0] * 9
                turno_jugador = True  # Reiniciar el turno al jugador
                historial_movimientos = [] # Reinicia el historial
                print("Juego reiniciado")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()