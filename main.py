import cv2
import numpy as np
import time
import sys
from deteccion_tablero import detectar_tablero, crear_cuadricula, dibujar_tablero
from deteccion_figuras import detectar_circulos, dibujar_x
from logica_juego import verificar_ganador, tablero_lleno, mejor_movimiento_ia, dibujar_linea_ganadora
from visualizacion import dibujar_tablero_visualizacion
from robot_control import RobotArmController  # Importar la clase del controlador del robot

class TicTacToeGame:
    def __init__(self, robot_port=None):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("No se pudo acceder a la cámara")
            exit()

        self.estado_tablero = [' '] * 9
        self.turno_jugador = True
        self.tiempo_espera = 0.5
        self.ultimo_tiempo = time.time()
        self.juego_terminado = False
        self.final_mostrado = False
        self.dibujando_circulo = [False] * 9
        self.tiempo_inicio_dibujo = [0] * 9
        self.historial_movimientos = []
        self.contador_estabilidad = [0] * 9
        self.umbral_estabilidad = 5
        self.tiempo_maximo_espera = 1
        self.tiempo_inicio_espera = [0] * 9
        self.imagen_visualizacion = np.zeros((480, 640, 3), np.uint8)
        self.color_ganador = (0, 255, 255)
        self.grosor_texto = 2
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.dificultad_ia = "facil"  # Dificultad por defecto
        self.seleccionando_dificultad = True
        self.rect_facil = None
        self.rect_dificil = None
        self.rect_imposible = None
        self.mensaje_final = ""
        self.linea_ganadora_posiciones = None
        self.robot_arm = None
        if robot_port:
            try:
                self.robot_arm = RobotArmController(robot_port)
                print("Control del robot inicializado.")
            except Exception as e:
                print(f"Error al inicializar el control del robot: {e}")
                self.robot_arm = None
        else:
            print("Control del robot no habilitado (no se proporcionó el puerto).")

        print("=== Tic Tac Toe con cámara y Robot ===")
        print("Coloca un tablero frente a la cámara")
        if self.robot_arm:
            print("El robot se moverá automáticamente según los movimientos de la IA.")
        else:
            print("El robot no se moverá automáticamente.")

    def reset_game(self):
        self.estado_tablero = [' '] * 9
        self.juego_terminado = False
        self.final_mostrado = False
        self.dibujando_circulo = [False] * 9
        self.tiempo_inicio_dibujo = [0] * 9
        self.historial_movimientos = []
        self.contador_estabilidad = [0] * 9
        self.tiempo_inicio_espera = [0] * 9
        self.seleccionando_dificultad = True
        self.mensaje_final = ""
        self.linea_ganadora_posiciones = None
        if self.dificultad_ia == "imposible":
            self.turno_jugador = False  # La IA empieza en Imposible
            if self.robot_arm:
                ai_move = mejor_movimiento_ia(self.estado_tablero, self.dificultad_ia)
                if ai_move is not None:
                    self.ejecutar_movimiento_robot(ai_move)
                    self.estado_tablero[ai_move] = 'X'
                    self.turno_jugador = True # Después del movimiento de la IA, el turno es del jugador
        else:
            self.turno_jugador = True  # El jugador empieza en otras dificultades
        print("Juego reiniciado")

    def dibujar_botones_dificultad(self, frame):
        h, w, _ = frame.shape
        boton_ancho = 200
        boton_alto = 50
        espacio = 20

        y_facil = h // 2 - boton_alto - espacio
        y_dificil = h // 2
        y_imposible = h // 2 + boton_alto + espacio

        self.rect_facil = (w // 2 - boton_ancho // 2, y_facil, w // 2 + boton_ancho // 2, y_facil + boton_alto)
        self.rect_dificil = (w // 2 - boton_ancho // 2, y_dificil, w // 2 + boton_ancho // 2, y_dificil + boton_alto)
        self.rect_imposible = (w // 2 - boton_ancho // 2, y_imposible, w // 2 + boton_ancho // 2, y_imposible + boton_alto)

        cv2.rectangle(frame, (self.rect_facil[0], self.rect_facil[1]), (self.rect_facil[2], self.rect_facil[3]), (200, 200, 200), -1)
        cv2.putText(frame, "Facil", (self.rect_facil[0] + 70, self.rect_facil[1] + 35), self.font, 1, (0, 0, 0), 2)

        cv2.rectangle(frame, (self.rect_dificil[0], self.rect_dificil[1]), (self.rect_dificil[2], self.rect_dificil[3]), (200, 200, 200), -1)
        cv2.putText(frame, "Dificil", (self.rect_dificil[0] + 60, self.rect_dificil[1] + 35), self.font, 1, (0, 0, 0), 2)

        cv2.rectangle(frame, (self.rect_imposible[0], self.rect_imposible[1]), (self.rect_imposible[2], self.rect_imposible[3]), (200, 200, 200), -1)
        cv2.putText(frame, "Imposible", (self.rect_imposible[0] + 40, self.rect_imposible[1] + 35), self.font, 1, (0, 0, 0), 2)

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            if self.seleccionando_dificultad:
                if self.rect_facil and self.rect_facil[0] < x < self.rect_facil[2] and self.rect_facil[1] < y < self.rect_facil[3]:
                    self.dificultad_ia = "facil"
                    self.seleccionando_dificultad = False
                    self.turno_jugador = True  # Aseguramos que el jugador empiece en Fácil
                    print("Dificultad seleccionada: Facil")
                elif self.rect_dificil and self.rect_dificil[0] < x < self.rect_dificil[2] and self.rect_dificil[1] < y < self.rect_dificil[3]:
                    self.dificultad_ia = "dificil"
                    self.seleccionando_dificultad = False
                    self.turno_jugador = True  # Aseguramos que el jugador empiece en Difícil
                    print("Dificultad seleccionada: Dificil")
                elif self.rect_imposible and self.rect_imposible[0] < x < self.rect_imposible[2] and self.rect_imposible[1] < y < self.rect_imposible[3]:
                    self.dificultad_ia = "imposible"
                    self.seleccionando_dificultad = False
                    self.turno_jugador = False # Forzamos el turno de la IA al seleccionar Imposible
                    print("Dificultad seleccionada: Imposible")
                    if self.robot_arm and not self.juego_terminado:
                        ai_move = mejor_movimiento_ia(self.estado_tablero, self.dificultad_ia)
                        if ai_move is not None:
                            self.ejecutar_movimiento_robot(ai_move)
                            self.estado_tablero[ai_move] = 'X'
                            self.turno_jugador = True # El turno pasa al jugador después del movimiento inicial de la IA
            # No es necesario un else aquí, ya que la selección de dificultad cambia self.seleccionando_dificultad

    def mostrar_turno(self, frame):
        turno_texto = "Tu turno (O)" if self.turno_jugador else "Turno de la IA (X)"
        cv2.putText(frame, turno_texto, (20, frame.shape[0] - 20), self.font, 0.7, (255, 255, 255), self.grosor_texto)

    def handle_player_move(self, frame, frame_procesado, cuadricula):
        nuevo_estado = list(self.estado_tablero)
        tiempo_actual = time.time()
        for i, celda in enumerate(cuadricula):
            circulos, circulo_detectado = detectar_circulos(frame, celda)
            if circulo_detectado:
                if not self.dibujando_circulo[i] and self.estado_tablero[i] == ' ':
                    self.contador_estabilidad[i] += 1
                    if self.contador_estabilidad[i] >= self.umbral_estabilidad:
                        nuevo_estado[i] = 'O'
                        self.dibujando_circulo[i] = True
                        self.contador_estabilidad[i] = 0
                        if self.tiempo_inicio_espera[i] == 0:
                            self.tiempo_inicio_espera[i] = tiempo_actual
            if circulos is not None:
                x, y, r = circulos[0]
                cv2.circle(frame_procesado, (celda[0] + int(x), celda[1] + int(y)), int(r), (255, 0, 0), 2)
            else:
                self.contador_estabilidad[i] = 0
                self.tiempo_inicio_espera[i] = 0

            if self.tiempo_inicio_espera[i] != 0 and tiempo_actual - self.tiempo_inicio_espera[i] > self.tiempo_maximo_espera:
                self.contador_estabilidad[i] = 0
                self.tiempo_inicio_espera[i] = 0

        if nuevo_estado != self.estado_tablero:
            self.estado_tablero = nuevo_estado
            self.ultimo_tiempo = tiempo_actual
            self.historial_movimientos.append((self.estado_tablero[:], cuadricula[:]))
            self.turno_jugador = False
            return True
        return False

    def handle_ai_move(self, frame_procesado, cuadricula):
        if not self.juego_terminado and not self.turno_jugador:
            movimiento_ia = mejor_movimiento_ia(self.estado_tablero, self.dificultad_ia)
            if movimiento_ia is not None and self.estado_tablero[movimiento_ia] == ' ':
                self.estado_tablero[movimiento_ia] = 'X'
                dibujar_x(frame_procesado, cuadricula[movimiento_ia], color=self.color_ganador, grosor=self.grosor_texto)
                self.historial_movimientos.append((self.estado_tablero[:], cuadricula[:]))
                if self.robot_arm:
                    self.ejecutar_movimiento_robot(movimiento_ia)
                self.turno_jugador = True
                return True
        return False

    def ejecutar_movimiento_robot(self, cell_index):
        if self.robot_arm and 0 <= cell_index < 9:
            print(f"Enviando comando al robot para mover a la celda {cell_index}")
            self.robot_arm.move_to_cell(cell_index)
            time.sleep(3) # Esperar a que el robot complete el movimiento

    def check_game_over(self, frame_procesado, cuadricula):
        ganador, posiciones = verificar_ganador(self.estado_tablero)
        if ganador:
            print(f"¡{ganador} ha ganado!")
            self.mensaje_final = f"¡{ganador} gana!"
            self.linea_ganadora_posiciones = posiciones
            self.juego_terminado = True
            return True
        elif tablero_lleno(self.estado_tablero):
            print("¡Empate!")
            self.mensaje_final = "¡Empate!"
            self.juego_terminado = True
            return True
        return False

    def dibujar_linea_ganadora_en_camara(self, frame_procesado, cuadricula, posiciones):
        if posiciones:
            if isinstance(posiciones[0], tuple):
                # Si posiciones contiene tuplas (fila, columna)
                indices_ganadores = [fila * 3 + columna for fila, columna in posiciones]
            else:
                # Si posiciones contiene directamente los índices del tablero
                indices_ganadores = posiciones

            if len(indices_ganadores) == 3:
                puntos_inicio_celda = cuadricula[indices_ganadores[0]]
                puntos_fin_celda = cuadricula[indices_ganadores[-1]]

                inicio_x = (puntos_inicio_celda[0] + puntos_inicio_celda[2]) // 2
                inicio_y = (puntos_inicio_celda[1] + puntos_inicio_celda[3]) // 2
                fin_x = (puntos_fin_celda[0] + puntos_fin_celda[2]) // 2
                fin_y = (puntos_fin_celda[1] + puntos_fin_celda[3]) // 2
                cv2.line(frame_procesado, (inicio_x, inicio_y), (fin_x, fin_y), self.color_ganador, self.grosor_texto + 3)

    def update_display(self, frame, frame_procesado, cuadricula):
        if cuadricula is not None:
            for i, celda in enumerate(cuadricula):
                if self.estado_tablero[i] == 'X':
                    dibujar_x(frame_procesado, celda, color=self.color_ganador, grosor=self.grosor_texto)
                if self.estado_tablero[i] == 'O':
                    circulos, _ = detectar_circulos(frame, celda)
                    if circulos is not None:
                        x, y, r = circulos[0]
                        cv2.circle(frame_procesado, (celda[0] + int(x), celda[1] + int(y)), int(r), (255, 0, 0), self.grosor_texto)

        if cuadricula is not None:
            self.imagen_visualizacion = dibujar_tablero_visualizacion(self.estado_tablero, cuadricula, self.imagen_visualizacion)

    def mostrar_resultado_final(self, frame_procesado, cuadricula):
        cv2.putText(frame_procesado, self.mensaje_final, (20, 40), self.font, 1, self.color_ganador, self.grosor_texto)
        cv2.putText(frame_procesado, "Presiona 'r' para reiniciar", (20, 80), self.font, 0.7, (255, 255, 255), self.grosor_texto)
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
            if self.seleccionando_dificultad:
                self.dibujar_botones_dificultad(frame_procesado)
            elif not self.juego_terminado:  # Solo procesar si el juego no ha terminado
                h_lineas, v_lineas, forma, bordes = detectar_tablero(frame)
                cuadricula = None

                if h_lineas is not None and v_lineas is not None:

                    frame_procesado = dibujar_tablero(frame_procesado, h_lineas, v_lineas)
                    cuadricula = crear_cuadricula(h_lineas, v_lineas, forma)

                    self.mostrar_turno(frame_procesado)

                    tiempo_actual = time.time()
                    if tiempo_actual - self.ultimo_tiempo > self.tiempo_espera:
                        if self.turno_jugador:
                            if self.handle_player_move(frame, frame_procesado, cuadricula):
                                pass # El turno cambia en handle_player_move
                        elif not self.turno_jugador:
                            self.handle_ai_move(frame_procesado, cuadricula)

                    if cuadricula is not None:
                        self.update_display(frame, frame_procesado, cuadricula)
                        self.check_game_over(frame_procesado, cuadricula)

                cv2.imshow("Canny", bordes)
            elif self.juego_terminado:
                h_lineas, v_lineas, forma, _ = detectar_tablero(frame)
                cuadricula = None
                if h_lineas is not None and v_lineas is not None:
                    cuadricula = crear_cuadricula(h_lineas, v_lineas, forma)
                    self.mostrar_resultado_final(frame_procesado, cuadricula)
                else:
                    self.mostrar_resultado_final(frame_procesado, None) # Mostrar mensaje incluso si no se detecta el tablero

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
    # Reemplaza '/dev/ttyACM0' o 'COM5' con el puerto serial de tu Arduino
    robot_port = '/dev/ttyACM0' if sys.platform.startswith('linux') else 'COM5'
    game = TicTacToeGame(robot_port)
    game.run()