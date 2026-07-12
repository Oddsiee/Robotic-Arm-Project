// Arduino/SerialTest.ino
//
// Milestone 7 - Test handshake serial Python <-> Arduino.
// BUKAN kode produksi. Servo & IK belum ada (menyusul Milestone 8 & 9).
// Sketch ini cuma menguji jalur komunikasi: terima koordinat,
// simulasikan waktu proses, balas "DONE".

const long BAUDRATE = 115200;
const unsigned long SIMULATED_PROCESS_TIME = 1500; // ms, simulasi durasi Pick->Drop->Home

String inputBuffer = "";

void setup() {
  Serial.begin(BAUDRATE);
}

void loop() {

  while (Serial.available()) {

    char c = Serial.read();

    if (c == '\n') {
      handleCommand(inputBuffer);
      inputBuffer = "";
    } else if (c != '\r') {
      inputBuffer += c;
    }
  }
}

void handleCommand(String line) {

  line.trim();

  if (line.length() == 0) {
    return;
  }

  int firstComma = line.indexOf(',');
  int secondComma = line.indexOf(',', firstComma + 1);

  if (firstComma == -1 || secondComma == -1) {
    Serial.println("ERR");
    return;
  }

  char color = line.charAt(0);
  float x = line.substring(firstComma + 1, secondComma).toFloat();
  float y = line.substring(secondComma + 1).toFloat();

  if (color != 'B' && color != 'W') {
    Serial.println("ERR");
    return;
  }

  Serial.print("Received: ");
  Serial.print(color);
  Serial.print(", ");
  Serial.print(x);
  Serial.print(", ");
  Serial.println(y);

  // Simulasi waktu siklus Pick -> Drop -> Home
  delay(SIMULATED_PROCESS_TIME);

  Serial.println("DONE");
}