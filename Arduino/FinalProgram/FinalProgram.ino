// Arduino/FinalProgram/FinalProgram.ino
//
// Milestone 10 - Pick and Place.
//
// Menerima satu perintah lewat serial: "color,base,shoulder,elbow\n"
// (base/shoulder/elbow = sudut target PICK, hasil InverseKinematics.compute()
// di Python, level meja - lihat Decision #044, Milestone 9).
//
// Satu perintah = satu siklus penuh:
//   Home (hover) -> Base ke target -> turun -> grip -> naik (hover)
//   -> Base ke drop zone (BLACK/WHITE, konstanta) -> turun -> lepas
//   -> naik -> Base ke home -> balas "DONE"
//
// Prinsip gerak (disepakati bareng Odi):
// - Base SELALU gerak duluan, delay, baru shoulder/elbow turun.
// - Shoulder & elbow di posisi HOME (90/90) berfungsi sebagai posisi
//   "hover" -> tidak perlu rumus IK baru, cukup reuse angka HOME yang
//   sudah ada, supaya rumus IK yang sudah tervalidasi fisik (Decision
//   #044) tidak disentuh sama sekali.
// - Semua gerakan servo pakai moveServoSmooth() (step kecil + delay),
//   sengaja dibuat pelan karena body robot tidak kuat gerakan cepat/
//   hentakan.
// - Parsing serial manual (indexOf/substring/toFloat()), BUKAN
//   sscanf("%f") - tidak reliable di AVR (Decision, Milestone 7).
//
// Titik drop BLACK/WHITE = konstanta hasil pengukuran manual fisik
// oleh Odi (Decision, Milestone 10) - ISI ANGKANYA DI BAWAH setelah
// tes fisik, nilai sekarang masih PLACEHOLDER.

#include <Servo.h>

// ==========================================================
// Pin Configuration (Decision #038, Milestone 8)
// ==========================================================
const int PIN_BASE     = 8;
const int PIN_SHOULDER = 9;
const int PIN_ELBOW    = 10;
const int PIN_GRIPPER  = 11;

// ==========================================================
// Home / Hover Position
// Shoulder & elbow di sudut ini otomatis jadi posisi "hover" -
// aman buat base berputar tanpa capit nyentuh meja/objek lain.
// ==========================================================
const int BASE_HOME     = 35;
const int SHOULDER_HOME = 90;
const int ELBOW_HOME    = 90;

const int GRIPPER_OPEN  = 90;
const int GRIPPER_CLOSE = 5;

// ==========================================================
// Drop Zone Constants (PLACEHOLDER - isi manual setelah tes fisik)
// ==========================================================
const int DROP_BLACK_BASE     = 35;    // TODO: isi hasil tes fisik
const int DROP_BLACK_SHOULDER = 60;   // TODO: isi hasil tes fisik
const int DROP_BLACK_ELBOW    = 90;   // TODO: isi hasil tes fisik

const int DROP_WHITE_BASE     = 170;  // TODO: isi hasil tes fisik
const int DROP_WHITE_SHOULDER = 60;   // TODO: isi hasil tes fisik
const int DROP_WHITE_ELBOW    = 90;   // TODO: isi hasil tes fisik

// ==========================================================
// Gerakan servo - sengaja pelan (step kecil, delay agak besar)
// karena body robot tidak kuat gerakan cepat/hentakan.
// Tuning lanjut kalau perlu setelah tes fisik.
// ==========================================================
const int SERVO_STEP_DELAY = 20;   // ms antar step
const int SERVO_STEP_SIZE  = 1;    // derajat per step

// Jeda "settle" antar fase gerakan (base selesai -> baru turun, dst)
const unsigned long SETTLE_DELAY         = 400;  // ms, base selesai -> sebelum turun
const unsigned long GRIP_SETTLE_DELAY    = 300;  // ms, gripper nutup -> sebelum naik
const unsigned long RELEASE_SETTLE_DELAY = 300;  // ms, gripper buka -> sebelum naik

// ==========================================================
Servo baseServo;
Servo shoulderServo;
Servo elbowServo;
Servo gripperServo;

// Buffer parsing serial
String inputBuffer = "";

void setup() {

  Serial.begin(115200);

  baseServo.attach(PIN_BASE);
  shoulderServo.attach(PIN_SHOULDER);
  elbowServo.attach(PIN_ELBOW);
  gripperServo.attach(PIN_GRIPPER);

  // Semua servo mulai di Home
  baseServo.write(BASE_HOME);
  shoulderServo.write(SHOULDER_HOME);
  elbowServo.write(ELBOW_HOME);
  gripperServo.write(GRIPPER_OPEN);

  delay(1000);  // beri waktu servo settle di posisi awal

  Serial.println("=== Milestone 10: Pick and Place Ready ===");
  Serial.println("Menunggu perintah: color,base,shoulder,elbow");
}

void loop() {

  readSerial();
}

// ==========================================================
// Serial Reading & Parsing
// ==========================================================
void readSerial() {

  while (Serial.available() > 0) {

    char c = Serial.read();

    if (c == '\n') {
      processCommand(inputBuffer);
      inputBuffer = "";
    } else if (c != '\r') {
      inputBuffer += c;
    }
  }
}

void processCommand(String line) {

  line.trim();

  if (line.length() == 0) {
    return;
  }

  // Format: color,base,shoulder,elbow
  // Parsing manual (indexOf/substring/toFloat), bukan sscanf.
  int idx1 = line.indexOf(',');
  int idx2 = line.indexOf(',', idx1 + 1);
  int idx3 = line.indexOf(',', idx2 + 1);

  if (idx1 == -1 || idx2 == -1 || idx3 == -1) {
    Serial.println("ERROR: format perintah tidak valid");
    return;
  }

  String colorCode = line.substring(0, idx1);
  float baseAngle     = line.substring(idx1 + 1, idx2).toFloat();
  float shoulderAngle = line.substring(idx2 + 1, idx3).toFloat();
  float elbowAngle    = line.substring(idx3 + 1).toFloat();

  colorCode.trim();

  if (colorCode != "B" && colorCode != "W") {
    Serial.println("ERROR: kode warna tidak dikenal");
    return;
  }

  runPickAndPlace(colorCode, (int)round(baseAngle), (int)round(shoulderAngle), (int)round(elbowAngle));

  Serial.println("DONE");
}

// ==========================================================
// Siklus Pick and Place Penuh
// ==========================================================
void runPickAndPlace(String colorCode, int pickBase, int pickShoulder, int pickElbow) {

  // --- PICK ---

  // 1. Base menuju target (shoulder/elbow tetap di HOME = hover)
  moveServoSmooth(baseServo, "Base", pickBase);
  delay(SETTLE_DELAY);

  // 2. Turun pelan ke sudut target (hasil IK)
  moveServoSmooth(elbowServo, "Elbow", pickElbow);
  moveServoSmooth(shoulderServo, "Shoulder", pickShoulder);

  // 3. Grip objek
  moveServoSmooth(gripperServo, "Gripper", GRIPPER_CLOSE);
  delay(GRIP_SETTLE_DELAY);

  // 4. Naik (balik ke hover), angkat objek dari meja
  moveServoSmooth(shoulderServo, "Shoulder", SHOULDER_HOME);
  moveServoSmooth(elbowServo, "Elbow", ELBOW_HOME);

  // --- DROP ---

  int dropBase, dropShoulder, dropElbow;

  if (colorCode == "B") {
    dropBase     = DROP_BLACK_BASE;
    dropShoulder = DROP_BLACK_SHOULDER;
    dropElbow    = DROP_BLACK_ELBOW;
  } else {
    dropBase     = DROP_WHITE_BASE;
    dropShoulder = DROP_WHITE_SHOULDER;
    dropElbow    = DROP_WHITE_ELBOW;
  }

  // 5. Base menuju drop zone (masih di hover)
  moveServoSmooth(baseServo, "Base", dropBase);
  delay(SETTLE_DELAY);

  // 6. Turun pelan ke posisi drop
  moveServoSmooth(elbowServo, "Elbow", dropElbow);
  moveServoSmooth(shoulderServo, "Shoulder", dropShoulder);

  // 7. Lepas objek
  moveServoSmooth(gripperServo, "Gripper", GRIPPER_OPEN);
  delay(RELEASE_SETTLE_DELAY);

  // --- HOME ---

  // 8. Naik (hover) lagi
  moveServoSmooth(elbowServo, "Elbow", ELBOW_HOME);
  moveServoSmooth(shoulderServo, "Shoulder", SHOULDER_HOME);

  // 9. Base kembali ke home
  moveServoSmooth(baseServo, "Base", BASE_HOME);
}

// ==========================================================
// Positional Servo Helper (reuse dari ServoControl.ino, Milestone 8)
// Dipakai oleh SEMUA 4 servo - semuanya SG90 180 positional.
// ==========================================================
void moveServoSmooth(Servo &servo, const char* label, int targetAngle) {

  int currentAngle = servo.read();

  Serial.print("  ");
  Serial.print(label);
  Serial.print(": ");
  Serial.print(currentAngle);
  Serial.print(" -> ");
  Serial.println(targetAngle);

  if (currentAngle < targetAngle) {
    for (int a = currentAngle; a <= targetAngle; a += SERVO_STEP_SIZE) {
      servo.write(a);
      delay(SERVO_STEP_DELAY);
    }
  } else {
    for (int a = currentAngle; a >= targetAngle; a -= SERVO_STEP_SIZE) {
      servo.write(a);
      delay(SERVO_STEP_DELAY);
    }
  }

  servo.write(targetAngle);  // pastikan tepat di target
}
