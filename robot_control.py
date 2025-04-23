# robot_control.py
import serial
import time
import re
import sys  # Importar la librería sys para salir del programa

class RobotArmController:
    def __init__(self, port, baudrate=9600, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_connection = None
        # Las coordenadas ahora están principalmente en el Arduino
        self.cell_coordinates = {i: None for i in range(9)}
        self.servo_positions = {"cintura": None, "hombro": None, "codo": None, "pinzas": None}
        self.joystick_active = False  # Bandera para indicar si el control por joystick está activo
        self.connect()
        if self.serial_connection:
            self._move_to_initial_position()

    def connect(self):
        try:
            self.serial_connection = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            print(f"Conexión serial establecida en el puerto {self.port}")
            time.sleep(2)  # Esperar a que el Arduino se reinicie después de la conexión
        except serial.SerialException as e:
            print(f"Error al conectar con el puerto {self.port}: {e}")
            self.serial_connection = None

    def send_command(self, command):
        if self.serial_connection:
            try:
                command_bytes = command.encode('utf-8') + b'\n'  # Codificar y añadir newline
                self.serial_connection.write(command_bytes)
                print(f"Comando enviado: {command.strip()}")
                time.sleep(0.1) # Pequeña pausa para asegurar el envío
            except serial.SerialException as e:
                print(f"Error al enviar el comando '{command.strip()}': {e}")
        else:
            print("No hay conexión serial activa para enviar el comando.")

    def close(self):
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            print("Conexión serial cerrada.")
            self.serial_connection = None

    def move_to_cell(self, cell_index):
        if 0 <= cell_index < 9:
            command = f"ir_celda {cell_index}"
            self.send_command(command)
            print(f"Solicitando movimiento a la celda {cell_index}")
        else:
            print(f"Índice de celda inválido: {cell_index}")

    def _set_servo_angles(self, cintura_deg, hombro_deg, codo_deg, pinzas_deg):
        command = f"C{int(cintura_deg)}H{int(hombro_deg)}E{int(codo_deg)}P{int(pinzas_deg)}"
        self.send_command(command)

    def read_servo_angles(self):
        if self.serial_connection:
            try:
                line = self.serial_connection.readline().decode('utf-8').rstrip()
                match = re.match(r"Cintura: (\d+), Hombro: (\d+), Codo: (\d+), Pinzas: (\d+)", line)
                if match:
                    cintura, hombro, codo, pinzas = map(int, match.groups())
                    self.servo_positions["cintura"] = cintura
                    self.servo_positions["hombro"] = hombro
                    self.servo_positions["codo"] = codo
                    self.servo_positions["pinzas"] = pinzas
                    return self.servo_positions.copy()
                elif line.startswith("Recibido de Python:") or line.startswith("Moviendo a celda:") or line.startswith("Joystick -") or line.startswith("Cambiando a"):
                    print(f"Mensaje del Arduino: {line}")
                elif line:
                    print(f"Mensaje sin procesar del Arduino: {line}")
            except serial.SerialException as e:
                print(f"Error al leer del puerto: {e}")
        return None

    def get_servo_positions(self):
        """Devuelve la última lectura de las posiciones de los servos."""
        return self.servo_positions.copy()

    def run_cell_test(self, delay_seconds=2):
        print("Iniciando recorrido de prueba de celdas paso a paso...")
        try:
            for i in range(9):
                print(f"\n--- Celda {i} ---")
                self.move_to_cell(i)
                print(f"Solicitando movimiento a la celda {i}")
                time.sleep(delay_seconds) # Espera para que el Arduino se mueva
                servo_angles = self.read_servo_angles()
                if servo_angles:
                    print(f"Posiciones de los servos: Cintura={servo_angles['cintura']}, Hombro={servo_angles['hombro']}, Codo={servo_angles['codo']}, Pinzas={servo_angles['pinzas']}")

                user_input = input("Presiona Enter para continuar a la siguiente celda o 'q' para salir...")
                if user_input.lower() == 'q':
                    print("Saliendo del recorrido de prueba.")
                    break
        except KeyboardInterrupt:
            print("\nPrueba de recorrido de celdas interrumpida por el usuario.")
        finally:
            if self.serial_connection and self.serial_connection.is_open:
                self.close()

    def move_to_specific_cell(self):
        while True:
            try:
                cell_number_str = input("Introduce el número de celda (0-8) a la que mover o 'q' para salir: ")
                if cell_number_str.lower() == 'q':
                    print("Saliendo del control de celda específica.")
                    break
                cell_index = int(cell_number_str)
                if 0 <= cell_index < 9:
                    self.move_to_cell(cell_index)
                    time.sleep(2)  # Espera para que el Arduino se mueva
                    servo_angles = self.read_servo_angles()
                    if servo_angles:
                        print(f"Posiciones de los servos: Cintura={servo_angles['cintura']}, Hombro={servo_angles['hombro']}, Codo={servo_angles['codo']}, Pinzas={servo_angles['pinzas']}")
                else:
                    print("Número de celda inválido. Debe estar entre 0 y 8.")
            except ValueError:
                print("Entrada inválida. Por favor, introduce un número entero o 'q'.")

    def _move_to_initial_position(self):
        central_cell_index = 4
        print(f"Solicitando movimiento a la posición inicial (celda {central_cell_index})...")
        self.move_to_cell(central_cell_index)
        time.sleep(2) # Esperar a que la mano se mueva
        servo_angles = self.read_servo_angles()
        if servo_angles:
            print(f"Posiciones iniciales de los servos: Cintura={servo_angles['cintura']}, Hombro={servo_angles['hombro']}, Codo={servo_angles['codo']}, Pinzas={servo_angles['pinzas']}")

    def enable_joystick_control(self):
        self.send_command("control_joystick")
        print("Control por joystick habilitado.")
        self.joystick_active = True
        self._read_joystick_servo_positions() # Iniciar la lectura continua

    def enable_python_control(self):
        self.send_command("control_python")
        print("Control por Python habilitado.")
        self.joystick_active = False

    def _read_joystick_servo_positions(self):
        """Lee y muestra las posiciones de los servos mientras el control por joystick esté activo."""
        while self.joystick_active and self.serial_connection and self.serial_connection.is_open:
            servo_positions = self.read_servo_angles()
            if servo_positions and all(v is not None for v in servo_positions.values()):
                print(f"\rPosiciones de los servos (Joystick): Cintura={servo_positions['cintura']}, Hombro={servo_positions['hombro']}, Codo={servo_positions['codo']}, Pinzas={servo_positions['pinzas']}", end="")
            time.sleep(0.1) # Pequeña pausa para no saturar la lectura


if __name__ == "__main__":
    arduino_port = 'COM5'  # Puerto del Arduino (ajustar según sea necesario)
    robot_arm = RobotArmController(arduino_port)

    if robot_arm.serial_connection:
        try:
            print("Moviendo a la celda central primero...")
            robot_arm.move_to_cell(4)
            time.sleep(5)  # Esperar 5 segundos para observar
            servo_angles = robot_arm.read_servo_angles()
            if servo_angles:
                print(f"Posiciones actuales de los servos: Cintura={servo_angles['cintura']}, Hombro={servo_angles['hombro']}, Codo={servo_angles['codo']}, Pinzas={servo_angles['pinzas']}")

            while True:
                user_choice = input("\nElige una opción:\n1. Ejecutar prueba de recorrido de celdas.\n2. Mover a una celda específica.\n3. Habilitar control por joystick.\n4. Habilitar control por Python.\n5. Mostrar posiciones de los servos.\n6. Salir.\nIntroduce el número de la opción: ")

                if user_choice == '1':
                    robot_arm.run_cell_test()
                elif user_choice == '2':
                    robot_arm.move_to_specific_cell()
                elif user_choice == '3':
                    robot_arm.enable_joystick_control()
                    # La lectura continua ahora se maneja en _read_joystick_servo_positions
                elif user_choice == '4':
                    robot_arm.enable_python_control()
                elif user_choice == '5':
                    servo_positions = robot_arm.get_servo_positions()
                    if servo_positions["cintura"] is not None:
                        print(f"Posiciones actuales de los servos: Cintura={servo_positions['cintura']}, Hombro={servo_positions['hombro']}, Codo={servo_positions['codo']}, Pinzas={servo_positions['pinzas']}")
                    else:
                        print("Aún no se han leído las posiciones de los servos.")
                elif user_choice == '6':
                    print("Saliendo del programa.")
                    break
                else:
                    print("Opción inválida. Por favor, introduce un número del 1 al 6.")

        finally:
            if robot_arm.serial_connection and robot_arm.serial_connection.is_open:
                robot_arm.close()