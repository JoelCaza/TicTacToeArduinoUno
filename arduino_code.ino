#include <Servo.h>

Servo cintura;
Servo hombro;
Servo codo;
Servo pinzas;

int grados_cintura = 90;
int grados_hombro = 90;
int grados_codo = 90;
int grados_pinzas = 90;

#define VRY A0
#define VRX A1
#define VRY_2 A2
#define VRX_2 A3

// Definición de las coordenadas de las celdas (debe coincidir con Python)
struct Celda {
  int cintura;
  int hombro;
  int codo;
  int pinzas;
};

Celda coordenadas_celdas[] = {
  {168, 58, 40, 180},  // Celda 0 Fila 1, celda 3
  {154, 70, 100, 180},  // Celda 1
  {150, 62, 135, 180}, // Celda 2
  {130, 58, 40, 180},   // Celda 3
  {134, 86, 90, 180},   // Celda 4
  {134, 62, 135, 180}, // Celda 5
  {86, 58, 40, 180},    // Celda 6
  {114, 86, 90, 180},   // Celda 7 
  {114, 62, 135, 180} // Celda 8 Fila 1, celda 1
  
};

bool recibir_comando_python = true; // Bandera para alternar control

void setup() {
  cintura.attach(6);
  hombro.attach(9);
  codo.attach(10);
  pinzas.attach(11);

  pinMode(VRY, INPUT);
  pinMode(VRX, INPUT);
  pinMode(VRY_2, INPUT);
  pinMode(VRX_2, INPUT);

  Serial.begin(9600);

  // Inicializar los servos a la posición de la celda central
  mover_a_celda(4);
  delay(1000); // Espera breve para que los servos se posicionen
}

void loop() {
  if (recibir_comando_python) {
    if (Serial.available() > 0) {
      String command = Serial.readStringUntil('\n');
      if (command.length() > 0) {
        if (command.startsWith("C") && command.indexOf("H") > 1 && command.indexOf("E") > command.indexOf("H") + 1 && command.indexOf("P") > command.indexOf("E") + 1) {
          int cintura_deg = command.substring(1, command.indexOf("H")).toInt();
          int hombro_deg = command.substring(command.indexOf("H") + 1, command.indexOf("E")).toInt();
          int codo_deg = command.substring(command.indexOf("E") + 1, command.indexOf("P")).toInt();
          int pinzas_deg = command.substring(command.indexOf("P") + 1).toInt();

          grados_cintura = constrain(cintura_deg, 0, 180);
          grados_hombro = constrain(hombro_deg, 10, 110);
          grados_codo = constrain(codo_deg, 0, 180);
          grados_pinzas = constrain(pinzas_deg, 0, 180);

          cintura.write(grados_cintura);
          hombro.write(grados_hombro);
          codo.write(grados_codo);
          pinzas.write(grados_pinzas);

          Serial.print("Recibido de Python: ");
          Serial.print("C"); Serial.print(grados_cintura);
          Serial.print("H"); Serial.print(grados_hombro);
          Serial.print("E"); Serial.print(grados_codo);
          Serial.print("P"); Serial.println(grados_pinzas);
        } else if (command.startsWith("ir_celda")) {
          int celda_index = command.substring(command.indexOf(" ") + 1).toInt();
          if (celda_index >= 0 && celda_index < 9) {
            mover_a_celda(celda_index);
            Serial.print("Moviendo a celda: ");
            Serial.println(celda_index);
          } else {
            Serial.println("Índice de celda inválido.");
          }
        } else if (command == "control_joystick") {
          recibir_comando_python = false;
          Serial.println("Cambiando a control por joystick.");
        }
      }
    }
  } else {
    // Control por joysticks (tu código original)
    int LVRY = analogRead(VRY);
    int LVRX = analogRead(VRX);
    int LVRY_2 = analogRead(VRY_2);
    int LVRX_2 = analogRead(VRX_2);

    if (LVRY < 340) grados_cintura -= 4;
    else if (LVRY > 680) grados_cintura += 4;
    grados_cintura = constrain(grados_cintura, 0, 180);
    cintura.write(grados_cintura);

    if (LVRX < 340) grados_hombro += 4;
    else if (LVRX > 680) grados_hombro -= 4;
    grados_hombro = constrain(grados_hombro, 10, 110);
    hombro.write(grados_hombro);

    if (LVRY_2 < 340) grados_codo += 5;
    else if (LVRY_2 > 680) grados_codo -= 5;
    grados_codo = constrain(grados_codo, 0, 180);
    codo.write(grados_codo);

    if (LVRX_2 < 340) grados_pinzas -= 5;
    else if (LVRX_2 > 680) grados_pinzas += 5;
    grados_pinzas = constrain(grados_pinzas, 0, 180);
    pinzas.write(grados_pinzas);

    Serial.print("Joystick - Cintura: "); Serial.print(grados_cintura);
    Serial.print(", Hombro: "); Serial.print(grados_hombro);
    Serial.print(", Codo: "); Serial.print(grados_codo);
    Serial.print(", Pinzas: "); Serial.println(grados_pinzas);

    delay(40);

    if (Serial.available() > 0) {
      String command = Serial.readStringUntil('\n');
      if (command == "control_python") {
        recibir_comando_python = true;
        Serial.println("Cambiando a control por Python.");
      }
    }
  }
}

void mover_a_celda(int index) {
  if (index >= 0 && index < 9) {
    cintura.write(coordenadas_celdas[index].cintura);
    hombro.write(coordenadas_celdas[index].hombro);
    codo.write(coordenadas_celdas[index].codo);
    pinzas.write(coordenadas_celdas[index].pinzas);

    grados_cintura = coordenadas_celdas[index].cintura;
    grados_hombro = coordenadas_celdas[index].hombro;
    grados_codo = coordenadas_celdas[index].codo;
    grados_pinzas = coordenadas_celdas[index].pinzas;
  } else {
    Serial.println("Índice de celda fuera de rango.");
  }
}