# Proyecto Tic Tac Toe con Cámara, IA y Control de Robot

Este proyecto implementa un juego de Tic Tac Toe interactivo que utiliza una cámara para detectar los movimientos del jugador, una inteligencia artificial para jugar contra el humano y un brazo robótico para realizar los movimientos de la IA en un tablero físico.

## Componentes del Proyecto

El proyecto se divide en varios módulos principales:

1.  **`main.py`**: El script principal que orquesta el juego. Captura video de la cámara, detecta el tablero y las figuras, gestiona los turnos, la lógica del juego, la interacción con la IA y el control del robot. También incluye una interfaz para seleccionar la dificultad de la IA.

2.  **`deteccion_tablero.py`**: Contiene funciones para detectar las líneas del tablero en la imagen de la cámara y crear una cuadrícula que representa las celdas del tablero.

3.  **`deteccion_figuras.py`**: Incluye funciones para detectar círculos (movimientos del jugador 'O') y dibujar cruces ('X' - movimientos de la IA) en el frame procesado.

4.  **`logica_juego.py`**: Implementa la lógica del juego Tic Tac Toe, incluyendo la verificación de un ganador, si el tablero está lleno y la función minimax (con poda alfa-beta para la dificultad "imposible") para determinar el mejor movimiento de la IA.

5.  **`visualizacion.py`**: Contiene funciones para dibujar el estado actual del tablero en una ventana separada para una visualización más clara.

6.  **`robot_control.py`**: Define la clase `RobotArmController` para comunicarse con un brazo robótico a través de un puerto serial. Permite enviar comandos para mover el brazo a diferentes celdas del tablero y leer las posiciones de los servos.

## Requisitos

Antes de ejecutar el proyecto, asegúrate de tener instaladas las siguientes dependencias:

* **Python 3**
* **OpenCV (`cv2`)**: Para el procesamiento de imágenes y la captura de video.
    ```bash
    pip install opencv-python
    ```
* **NumPy**: Para operaciones numéricas.
    ```bash
    pip install numpy
    ```
* **PySerial (`serial`)**: Para la comunicación serial con el Arduino/brazo robótico.
    ```bash
    pip install pyserial
    ```

También necesitarás:

* Una **cámara web** conectada a tu computadora.
* Un **brazo robótico** compatible con el control serial (configurado para recibir comandos y enviar información de posición en el formato esperado).
* Un **tablero de Tic Tac Toe** físico que pueda ser detectado por la cámara.
* Un **Arduino** (u otro microcontrolador) programado para controlar el brazo robótico y comunicarse serialmente con la computadora.

## Configuración

1.  **Puerto Serial del Robot:** En el script `main.py`, asegúrate de que la variable `robot_port` esté configurada con el puerto serial correcto al que está conectado tu Arduino (por ejemplo, `/dev/ttyACM0` en Linux o `COM5` en Windows).

    ```python
    # main.py
    robot_port = '/dev/ttyACM0' if sys.platform.startswith('linux') else 'COM5'
    game = TicTacToeGame(robot_port)
    ```

2.  **Código del Arduino:** Necesitarás tener un código cargado en tu Arduino que:
    * Reciba comandos seriales para mover el brazo a las celdas del tablero (por ejemplo, `ir_celda 0` a `ir_celda 8`).
    * Controle los servos del brazo robótico para alcanzar las posiciones deseadas para cada celda.
    * (Opcional pero recomendado) Envíe las posiciones actuales de los servos al puerto serial en el formato: `"Cintura: <valor>, Hombro: <valor>, Codo: <valor>, Pinzas: <valor>"`.
    * (Opcional) Implemente un modo de control por joystick y envíe las posiciones de los servos durante este modo.

3.  **Calibración:** Es posible que necesites calibrar la posición del brazo robótico para que corresponda correctamente a las celdas detectadas por la cámara. Esto podría implicar ajustar las coordenadas en el código del Arduino o la forma en que se definen las celdas en `deteccion_tablero.py`.

## Ejecución

1.  Asegúrate de que tu cámara esté conectada y funcionando.
2.  Conecta tu Arduino/brazo robótico a tu computadora a través del puerto USB.
3.  Ejecuta el script principal desde la terminal:
    ```bash
    python main.py
    ```
4.  Coloca el tablero de Tic Tac Toe frente a la cámara de manera que sea claramente visible.
5.  Sigue las instrucciones en la ventana de la cámara para jugar.
6.  Utiliza la interfaz en la ventana de la cámara para seleccionar la dificultad de la IA haciendo clic en los botones "Facil", "Dificil" o "Imposible".
7.  Realiza tus movimientos colocando un objeto circular ('O') en la celda deseada. La cámara detectará el movimiento después de un breve período de estabilidad.
8.  La IA ('X') realizará sus movimientos automáticamente, y si el brazo robótico está conectado, lo hará físicamente en el tablero.
9.  Presiona la tecla `r` en la ventana de la cámara para reiniciar el juego.
10. Presiona la tecla `q` para salir del programa.

Si el brazo robótico está habilitado, también podrás interactuar con él a través del menú en la terminal (ejecutando `python robot_control.py` directamente) para probar los movimientos de las celdas, habilitar el control por joystick y ver las posiciones de los servos.

## Notas

* La detección del tablero y las figuras puede verse afectada por las condiciones de iluminación, el ángulo de la cámara y la claridad del tablero.
* La precisión del movimiento del brazo robótico depende de la calibración y la precisión de tu hardware.
* El código de la IA utiliza el algoritmo Minimax con poda alfa-beta para la dificultad "Imposible", lo que garantiza que la IA jugará de manera óptima. Las otras dificultades ("Facil" y "Dificil") pueden implementar estrategias más simples.
* Asegúrate de que el formato de los comandos enviados al Arduino en `robot_control.py` coincida con lo que tu código de Arduino espera.
* La lectura de las posiciones de los servos en Python depende de que el Arduino envíe esta información en el formato correcto.

¡Disfruta jugando al Tic Tac Toe con tu cámara, la IA y el brazo robótico!
