import cv2
import numpy as np
import time
import sys

# Asegúrate de que estas importaciones existen y funcionan
from deteccion_tablero import detectar_tablero, crear_cuadricula, dibujar_tablero
from deteccion_figuras import detectar_circulos, dibujar_x
from logica_juego import verificar_ganador, tablero_lleno, mejor_movimiento_ia
from visualizacion import dibujar_tablero_visualizacion
from robot_control import RobotArmController


class TicTacToeGame:
    def __init__(self, robot_port=None):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("No se pudo acceder a la camara")
            exit()

        self.estado_tablero = [' '] * 9
        self.turno_jugador = True
        self.tiempo_espera = 0.5
        self.ultimo_tiempo = time.time()
        self.juego_terminado = False
        self.final_mostrado = False
        self.historial_movimientos = []
        self.contador_estabilidad = [0] * 9
        self.umbral_estabilidad = 5
        self.tiempo_inicio_espera = [0] * 9
        self.imagen_visualizacion = np.zeros((480, 640, 3), np.uint8)

        # UI/UX Mejoras: Paleta de Colores y Estilos más profesionales
        self.color_primario = (255, 120, 0)      # Naranja vibrante para 'O' (similar a algunos iconos de iOS)
        self.color_secundario = (50, 50, 200)    # Azul oscuro para 'X' (contraste con naranja)
        self.color_fondo_ui = (25, 25, 25)       # Gris muy oscuro
        self.color_borde_ui = (70, 70, 70)       # Gris oscuro para bordes
        self.color_texto_claro = (230, 230, 230) # Blanco grisaceo para texto principal
        self.color_texto_oscuro = (0, 0, 0)      # Negro para texto sobre botones claros
        self.color_exito = (0, 200, 0)           # Verde para mensajes de exito
        self.color_alerta = (0, 165, 255)        # Naranja para el robot moviendose
        self.color_ganador = (0, 255, 255)       # Amarillo brillante para el ganador

        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.grosor_linea_juego = 4 # Lineas del tablero mas gruesas
        self.grosor_texto = 2      # Grosor general del texto

        # Dificultad
        self.dificultad_ia = "facil"
        self.seleccionando_dificultad = True
        self.rect_facil = None
        self.rect_dificil = None
        self.rect_imposible = None
        self.mensaje_final = ""
        self.linea_ganadora_posiciones = None

        # Robot Arm
        self.robot_arm = None
        self.robot_moviendo = False
        if robot_port:
            try:
                self.robot_arm = RobotArmController(robot_port)
                print("Control del robot inicializado.")
            except Exception as e:
                print(f"Error al inicializar el control del robot: {e}")
                self.robot_arm = None
        else:
            print("Control del robot no habilitado (no se proporciono el puerto).")

        # Contador al inicio del juego
        self.mostrar_countdown = False
        self.countdown_start_time = 0
        self.countdown_value = 3 # Empieza en 3

        print("=== Tic Tac Toe Robotico ===")
        print("Prepara el tablero y la camara.")
        if self.robot_arm:
            print("El robot se movera automaticamente.")
        else:
            print("El robot no se movera.")

    def reset_game(self):
        self.estado_tablero = [' '] * 9
        self.juego_terminado = False
        self.final_mostrado = False
        self.historial_movimientos = []
        self.contador_estabilidad = [0] * 9
        self.tiempo_inicio_espera = [0] * 9
        self.seleccionando_dificultad = True
        self.mensaje_final = ""
        self.linea_ganadora_posiciones = None
        self.robot_moviendo = False

        self.mostrar_countdown = False
        self.countdown_start_time = 0
        self.countdown_value = 3

        self.turno_jugador = True # Por defecto, el jugador comienza (salvo en Imposible)
        print("Juego reiniciado. Selecciona nueva dificultad.")

    def draw_rounded_rect(self, img, rect_coords, color, thickness, radius_factor=0.1):
        x1, y1, x2, y2 = rect_coords
        width = x2 - x1
        height = y2 - y1
        radius = int(min(width, height) * radius_factor)

        # Dibujar rectangulos con esquinas redondeadas
        cv2.ellipse(img, (x1 + radius, y1 + radius), (radius, radius), 180, 0, 90, color, thickness)
        cv2.ellipse(img, (x2 - radius, y1 + radius), (radius, radius), 270, 0, 90, color, thickness)
        cv2.ellipse(img, (x1 + radius, y2 - radius), (radius, radius), 90, 0, 90, color, thickness)
        cv2.ellipse(img, (x2 - radius, y2 - radius), (radius, radius), 0, 0, 90, color, thickness)

        cv2.line(img, (x1 + radius, y1), (x2 - radius, y1), color, thickness)
        cv2.line(img, (x1 + radius, y2), (x2 - radius, y2), color, thickness)
        cv2.line(img, (x1, y1 + radius), (x1, y2 - radius), color, thickness)
        cv2.line(img, (x2, y1 + radius), (x2, y2 - radius), color, thickness)

    def fill_rounded_rect(self, img, rect_coords, color, radius_factor=0.1):
        x1, y1, x2, y2 = rect_coords
        width = x2 - x1
        height = y2 - y1
        radius = int(min(width, height) * radius_factor)

        # Usar un contorno grueso para simular el relleno
        contours = np.array([
            (x1 + radius, y1), (x2 - radius, y1),
            (x2, y1 + radius), (x2, y2 - radius),
            (x2 - radius, y2), (x1 + radius, y2),
            (x1, y2 - radius), (x1, y1 + radius)
        ])
        cv2.fillPoly(img, [contours], color)

        # Rellenar las esquinas con circulos
        cv2.circle(img, (x1 + radius, y1 + radius), radius, color, -1)
        cv2.circle(img, (x2 - radius, y1 + radius), radius, color, -1)
        cv2.circle(img, (x1 + radius, y2 - radius), radius, color, -1)
        cv2.circle(img, (x2 - radius, y2 - radius), radius, color, -1)
        
        cv2.rectangle(img, (x1, y1 + radius), (x2, y2 - radius), color, -1)
        cv2.rectangle(img, (x1 + radius, y1), (x2 - radius, y2), color, -1)


    def draw_countdown(self, frame):
        if self.mostrar_countdown:
            tiempo_transcurrido = time.time() - self.countdown_start_time
            current_countdown = max(0, 3 - int(tiempo_transcurrido))

            if current_countdown > 0:
                text = str(current_countdown)
                (text_w, text_h), baseline = cv2.getTextSize(text, self.font, 5, 10)
                x = (frame.shape[1] - text_w) // 2
                y = (frame.shape[0] + text_h) // 2

                # Efecto de "salto" y tamaño dinamico
                scale_factor = 1 + (tiempo_transcurrido % 1) * 0.4 # Crece y se encoge
                grosor_borde = 12 + int((tiempo_transcurrido % 1) * 8) # Borde mas dinamico

                # Dibujar un fondo sutil para el contador
                overlay = frame.copy()
                cv2.circle(overlay, (frame.shape[1] // 2, frame.shape[0] // 2), 150, self.color_fondo_ui, -1)
                cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
                self.draw_rounded_rect(frame, (frame.shape[1] // 2 - 150, frame.shape[0] // 2 - 150,
                                               frame.shape[1] // 2 + 150, frame.shape[0] // 2 + 150),
                                       self.color_borde_ui, 3, radius_factor=0.5)

                cv2.putText(frame, text, (x, y), self.font, 5 * scale_factor, (0, 0, 255), grosor_borde, cv2.LINE_AA) # Rojo vibrante
                cv2.putText(frame, text, (x, y), self.font, 5 * scale_factor, (255, 255, 255), grosor_borde // 2, cv2.LINE_AA) # Blanco interior

                return True
            else:
                self.mostrar_countdown = False
                if self.dificultad_ia == "imposible":
                    self.turno_jugador = False
                else:
                    self.turno_jugador = True
                return False
        return False

    def dibujar_botones_dificultad(self, frame):
        h, w, _ = frame.shape
        boton_ancho = 250
        boton_alto = 70
        espacio = 25

        # Fondo semi-transparente para la seccion de dificultad
        overlay = frame.copy()
        rect_bg = (w // 2 - boton_ancho // 2 - espacio, h // 2 - boton_alto * 2 - espacio * 2 - 40,
                   w // 2 + boton_ancho // 2 + espacio, h // 2 + boton_alto * 2 + espacio * 2 + 20)
        self.fill_rounded_rect(overlay, rect_bg, self.color_fondo_ui, radius_factor=0.1)
        cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)
        self.draw_rounded_rect(frame, rect_bg, self.color_borde_ui, 3, radius_factor=0.1)

        # Titulo para la seleccion de dificultad
        texto_titulo = "Selecciona la Dificultad"
        (text_w, text_h), _ = cv2.getTextSize(texto_titulo, self.font, 1, self.grosor_texto + 1)
        cv2.putText(frame, texto_titulo, (w // 2 - text_w // 2, h // 2 - boton_alto * 2 - espacio * 2), self.font, 1, self.color_texto_claro, self.grosor_texto + 1)

        y_facil = h // 2 - boton_alto - espacio
        y_dificil = h // 2
        y_imposible = h // 2 + boton_alto + espacio

        self.rect_facil = (w // 2 - boton_ancho // 2, y_facil, w // 2 + boton_ancho // 2, y_facil + boton_alto)
        self.rect_dificil = (w // 2 - boton_ancho // 2, y_dificil, w // 2 + boton_ancho // 2, y_dificil + boton_alto)
        self.rect_imposible = (w // 2 - boton_ancho // 2, y_imposible, w // 2 + boton_ancho // 2, y_imposible + boton_alto)

        # Colores de los botones
        color_normal_boton = (60, 60, 60) # Gris oscuro
        color_seleccionado = self.color_exito # Verde vibrante

        def draw_button(rect, text, difficulty_name):
            color = color_seleccionado if self.dificultad_ia == difficulty_name and not self.seleccionando_dificultad else color_normal_boton
            self.fill_rounded_rect(frame, rect, color, radius_factor=0.25)
            self.draw_rounded_rect(frame, rect, self.color_borde_ui, 2, radius_factor=0.25)

            (text_w, text_h), _ = cv2.getTextSize(text, self.font, 1, 2)
            cv2.putText(frame, text, (rect[0] + (boton_ancho - text_w) // 2, rect[1] + (boton_alto + text_h) // 2 - 5), self.font, 1, self.color_texto_claro, 2)

        draw_button(self.rect_facil, "Facil", "facil")
        draw_button(self.rect_dificil, "Dificil", "dificil")
        draw_button(self.rect_imposible, "Imposible", "imposible")

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            if self.seleccionando_dificultad:
                if self.rect_facil and self.rect_facil[0] < x < self.rect_facil[2] and self.rect_facil[1] < y < self.rect_facil[3]:
                    self.dificultad_ia = "facil"
                    self.seleccionando_dificultad = False
                    self.mostrar_countdown = True
                    self.countdown_start_time = time.time()
                    print("Dificultad seleccionada: Facil")
                elif self.rect_dificil and self.rect_dificil[0] < x < self.rect_dificil[2] and self.rect_dificil[1] < y < self.rect_dificil[3]:
                    self.dificultad_ia = "dificil"
                    self.seleccionando_dificultad = False
                    self.mostrar_countdown = True
                    self.countdown_start_time = time.time()
                    print("Dificultad seleccionada: Dificil")
                elif self.rect_imposible and self.rect_imposible[0] < x < self.rect_imposible[2] and self.rect_imposible[1] < y < self.rect_imposible[3]:
                    self.dificultad_ia = "imposible"
                    self.seleccionando_dificultad = False
                    self.mostrar_countdown = True
                    self.countdown_start_time = time.time()
                    print("Dificultad seleccionada: Imposible")

    def mostrar_turno(self, frame):
        overlay = frame.copy()
        alpha = 0.7 # Mas opaco para mejor lectura
        color_fondo = self.color_fondo_ui
        color_texto_jugador = self.color_primario
        color_texto_ia = self.color_secundario
        color_robot_moviendo = self.color_alerta

        turno_texto = ""
        color_texto_actual = self.color_texto_claro

        if self.robot_moviendo:
            turno_texto = "Robot moviendo..."
            color_texto_actual = color_robot_moviendo
        elif self.turno_jugador:
            turno_texto = "Tu Turno (O)"
            color_texto_actual = color_texto_jugador
        else:
            turno_texto = "Turno de la IA (X)"
            color_texto_actual = color_texto_ia

        (text_w, text_h), baseline = cv2.getTextSize(turno_texto, self.font, 0.8, self.grosor_texto + 1) # Texto mas grande
        
        pad = 20 # Mas relleno
        x1, y1 = 20, frame.shape[0] - 20 - text_h - pad
        x2, y2 = 20 + text_w + pad*2, frame.shape[0] - 20 + pad - baseline

        self.fill_rounded_rect(overlay, (x1, y1, x2, y2), color_fondo, radius_factor=0.2)
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        self.draw_rounded_rect(frame, (x1, y1, x2, y2), self.color_borde_ui, 2, radius_factor=0.2)
        
        cv2.putText(frame, turno_texto, (20 + pad, frame.shape[0] - 20 - baseline), self.font, 0.8, color_texto_actual, self.grosor_texto + 1)

    def handle_player_move(self, frame, frame_procesado, cuadricula):
        nuevo_estado = list(self.estado_tablero)
        tiempo_actual = time.time()
        movimiento_detectado_y_confirmado = False

        for i, celda in enumerate(cuadricula):
            circulos, circulo_detectado = detectar_circulos(frame, celda)
            
            # Dibujar el circulo detectado temporalmente para feedback visual (semi-transparente)
            if circulos is not None and not self.juego_terminado and self.estado_tablero[i] == ' ':
                x, y, r = circulos[0]
                overlay = frame_procesado.copy()
                cv2.circle(overlay, (celda[0] + int(x), celda[1] + int(y)), int(r), self.color_primario, -1)
                cv2.addWeighted(overlay, 0.3, frame_procesado, 0.7, 0, frame_procesado)
                cv2.circle(frame_procesado, (celda[0] + int(x), celda[1] + int(y)), int(r), self.color_primario, 2)
                
            if circulo_detectado and self.estado_tablero[i] == ' ':
                self.contador_estabilidad[i] += 1
                if self.contador_estabilidad[i] >= self.umbral_estabilidad:
                    if self.tiempo_inicio_espera[i] == 0:
                        self.tiempo_inicio_espera[i] = tiempo_actual

                    if tiempo_actual - self.tiempo_inicio_espera[i] > self.tiempo_espera:
                        nuevo_estado[i] = 'O'
                        movimiento_detectado_y_confirmado = True
                        self.contador_estabilidad[i] = 0
                        self.tiempo_inicio_espera[i] = 0
                        break
            else:
                self.contador_estabilidad[i] = 0
                self.tiempo_inicio_espera[i] = 0

        if movimiento_detectado_y_confirmado:
            self.estado_tablero = nuevo_estado
            self.ultimo_tiempo = tiempo_actual
            self.historial_movimientos.append((self.estado_tablero[:], cuadricula[:]))
            self.turno_jugador = False
            return True
        return False

    def handle_ai_move(self, frame_procesado, cuadricula):
        if not self.juego_terminado and not self.turno_jugador and not self.robot_moviendo:
            self.robot_moviendo = True

            movimiento_ia = mejor_movimiento_ia(self.estado_tablero, self.dificultad_ia)
            if movimiento_ia is not None and self.estado_tablero[movimiento_ia] == ' ':
                self.estado_tablero[movimiento_ia] = 'X'
                self.historial_movimientos.append((self.estado_tablero[:], cuadricula[:]))
                
                if self.robot_arm:
                    self.ejecutar_movimiento_robot(movimiento_ia)
                
                self.turno_jugador = True
                self.robot_moviendo = False
                return True
            self.robot_moviendo = False
        return False

    def ejecutar_movimiento_robot(self, cell_index):
        if self.robot_arm and 0 <= cell_index < 9:
            print(f"Enviando comando al robot para mover a la celda {cell_index}")
            self.robot_arm.move_to_cell(cell_index)
            time.sleep(3) # Bloquear para simular el tiempo del robot

    def check_game_over(self, frame_procesado, cuadricula):
        ganador, posiciones = verificar_ganador(self.estado_tablero)
        if ganador:
            print(f"¡{ganador} ha ganado!")
            self.mensaje_final = f"{ganador.upper()} GANA!" # Sin tilde
            self.linea_ganadora_posiciones = posiciones
            self.juego_terminado = True
            return True
        elif tablero_lleno(self.estado_tablero):
            print("¡Empate!")
            self.mensaje_final = "EMPATE!" # Sin tilde
            self.juego_terminado = True
            return True
        return False

    def dibujar_linea_ganadora_en_camara(self, frame_procesado, cuadricula, posiciones):
        if posiciones:
            # `posiciones` from `verificar_ganador` should already be the flat indices (0-8)
            if isinstance(posiciones[0], tuple):
                indices_ganadores = [fila * 3 + columna for fila, columna in posiciones]
            else:
                indices_ganadores = posiciones

            if len(indices_ganadores) == 3:
                puntos_inicio_celda = cuadricula[indices_ganadores[0]]
                puntos_fin_celda = cuadricula[indices_ganadores[-1]]

                inicio_x = (puntos_inicio_celda[0] + puntos_inicio_celda[2]) // 2
                inicio_y = (puntos_inicio_celda[1] + puntos_inicio_celda[3]) // 2
                fin_x = (puntos_fin_celda[0] + puntos_fin_celda[2]) // 2
                fin_y = (puntos_fin_celda[1] + puntos_fin_celda[3]) // 2
                
                # Linea ganadora con mas grosor y color vibrante
                cv2.line(frame_procesado, (inicio_x, inicio_y), (fin_x, fin_y), self.color_ganador, self.grosor_linea_juego + 6)

    def update_display(self, frame, frame_procesado, cuadricula):
        if cuadricula is not None:
            # Dibujar las fichas ya confirmadas con el nuevo estilo
            for i, celda in enumerate(cuadricula):
                if self.estado_tablero[i] == 'X':
                    dibujar_x(frame_procesado, celda, color=self.color_secundario, grosor=self.grosor_linea_juego + 2)
                elif self.estado_tablero[i] == 'O':
                    centro_x = (celda[0] + celda[2]) // 2
                    centro_y = (celda[1] + celda[3]) // 2
                    radio = min(celda[2] - celda[0], celda[3] - celda[1]) // 3
                    cv2.circle(frame_procesado, (centro_x, centro_y), radio, self.color_primario, self.grosor_linea_juego + 2)

            self.imagen_visualizacion = dibujar_tablero_visualizacion(self.estado_tablero, cuadricula, self.imagen_visualizacion)


    def mostrar_resultado_final(self, frame_procesado, cuadricula):
        overlay = frame_procesado.copy()
        alpha = 0.85
        color_fondo_mensaje = self.color_fondo_ui

        (text_w_final, text_h_final), _ = cv2.getTextSize(self.mensaje_final, self.font, 1.8, self.grosor_texto + 2)
        x_final = (frame_procesado.shape[1] - text_w_final) // 2
        y_final = (frame_procesado.shape[0] // 2) - text_h_final // 2 - 20

        texto_reiniciar = "Presiona 'R' para reiniciar" # Usar mayuscula
        (text_w_reiniciar, text_h_reiniciar), _ = cv2.getTextSize(texto_reiniciar, self.font, 0.9, self.grosor_texto)
        x_reiniciar = (frame_procesado.shape[1] - text_w_reiniciar) // 2
        y_reiniciar = y_final + text_h_final + 40

        total_height = text_h_final + text_h_reiniciar + 80
        total_width = max(text_w_final, text_w_reiniciar) + 80
        rect_x1 = (frame_procesado.shape[1] - total_width) // 2
        rect_y1 = (frame_procesado.shape[0] - total_height) // 2
        rect_x2 = rect_x1 + total_width
        rect_y2 = rect_y1 + total_height
        
        self.fill_rounded_rect(overlay, (rect_x1, rect_y1, rect_x2, rect_y2), color_fondo_mensaje, radius_factor=0.1)
        cv2.addWeighted(overlay, alpha, frame_procesado, 1 - alpha, 0, frame_procesado)
        self.draw_rounded_rect(frame_procesado, (rect_x1, rect_y1, rect_x2, rect_y2), self.color_borde_ui, 3, radius_factor=0.1)

        cv2.putText(frame_procesado, self.mensaje_final, (x_final, y_final), self.font, 1.8, self.color_ganador, self.grosor_texto + 2)
        cv2.putText(frame_procesado, texto_reiniciar, (x_reiniciar, y_reiniciar), self.font, 0.9, self.color_texto_claro, self.grosor_texto)
        
        if self.linea_ganadora_posiciones and cuadricula is not None:
            self.dibujar_linea_ganadora_en_camara(frame_procesado, cuadricula, self.linea_ganadora_posiciones)

    def run(self):
        cv2.namedWindow("Tic Tac Toe con camara")
        cv2.setMouseCallback("Tic Tac Toe con camara", self.mouse_callback)

        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Error al capturar el frame")
                break

            frame = cv2.flip(frame, -1)
            frame_procesado = frame.copy()
            cuadricula = None

            if self.seleccionando_dificultad:
            
                self.dibujar_botones_dificultad(frame_procesado)
            elif self.mostrar_countdown:
                # El countdown se encarga de cambiar self.mostrar_countdown a False
                # y de establecer el turno_jugador o iniciar el primer movimiento de la IA
                self.draw_countdown(frame_procesado)
                # Si el countdown ha terminado y es turno de la IA, iniciar su movimiento
                if not self.mostrar_countdown and self.dificultad_ia == "imposible" and not self.turno_jugador:
                    ai_move = mejor_movimiento_ia(self.estado_tablero, self.dificultad_ia)
                    if ai_move is not None:
                        self.robot_moviendo = True
                        self.estado_tablero[ai_move] = 'X'
                        self.ejecutar_movimiento_robot(ai_move)
                        self.turno_jugador = True
                        self.robot_moviendo = False
            elif not self.juego_terminado:
                h_lineas, v_lineas, forma, bordes = detectar_tablero(frame)
                
                if h_lineas is not None and v_lineas is not None:
                    # Dibujar el tablero con lineas detectadas
                    frame_procesado = dibujar_tablero(frame_procesado, h_lineas, v_lineas)
                    cuadricula = crear_cuadricula(h_lineas, v_lineas, forma)
                    self.update_display(frame, frame_procesado, cuadricula)
                    self.mostrar_turno(frame_procesado)

                    tiempo_actual = time.time()
                    if tiempo_actual - self.ultimo_tiempo > self.tiempo_espera:
                        if self.turno_jugador:
                            self.handle_player_move(frame, frame_procesado, cuadricula)
                        elif not self.turno_jugador:
                            self.handle_ai_move(frame_procesado, cuadricula)

                    self.check_game_over(frame_procesado, cuadricula)
                else:
                    # Mensaje cuando no se detecta el tablero
                    cv2.putText(frame_procesado, "Esperando tablero...", (frame_procesado.shape[1] // 2 - 100, frame_procesado.shape[0] // 2), self.font, 1, self.color_alerta, self.grosor_texto + 1)

                if bordes is not None:
                    cv2.imshow("Canny Edges", bordes) # Nombre de ventana mas descriptivo
                else:
                    try:
                        cv2.destroyWindow("Canny Edges")
                    except:
                        pass
            elif self.juego_terminado:
                h_lineas, v_lineas, forma, _ = detectar_tablero(frame)
                if h_lineas is not None and v_lineas is not None:
                    cuadricula = crear_cuadricula(h_lineas, v_lineas, forma)
                    self.update_display(frame, frame_procesado, cuadricula)
                    self.mostrar_resultado_final(frame_procesado, cuadricula)
                else:
                    self.mostrar_resultado_final(frame_procesado, None)

            cv2.imshow("Tic Tac Toe con camara", frame_procesado)
            cv2.imshow("Visualizacion del tablero", self.imagen_visualizacion)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                self.reset_game()

        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    robot_port = '/dev/ttyACM0' if sys.platform.startswith('linux') else 'COM5'
    # robot_port = None # Descomenta para probar sin robot
    game = TicTacToeGame(robot_port)
    game.run()