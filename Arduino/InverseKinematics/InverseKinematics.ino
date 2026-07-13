// Arduino/InverseKinematics/InverseKinematics.ino
//
// Milestone 9 - Inverse Kinematics.
// Menggantikan Arduino/SerialTest.ino sebagai sketch produksi:
// terima koordinat robot (cm) via serial, hitung IK, gerakkan
// base/shoulder/elbow, balas "DONE".
//
// z (tinggi pick) FIXED di level meja, gripper rigid menyatu ke
// lengan bawah (L3 gabungan), elbow config = DOWN tetap (lihat
// ELBOW_CONFIG di bawah untuk switch ke UP kalau nanti diuji).

#include <Servo.h>
#include <math.h>

// ==========================================================
// Pin Configuration
// ==========================================================
const int PIN_BASE     = 8;
const int PIN_SHOULDER = 9;
const int PIN_ELBOW    = 10;
const int PIN_GRIPPER  = 11;

// ==========================================================
// Servo Home / Gripper
// ==========================================================
const int BASE_HOME     = 90;
const int SHOULDER_HOME = 90;
const int ELBOW_HOME    = 90;
const int GRIPPER_OPEN  = 90;
const int GRIPPER_CLOSE = 20;

const int SERVO_STEP_DELAY = 15;
const int SERVO_STEP_SIZE  = 2;

// ==========================================================
// Robot Geometry (IK) - hasil kalibrasi manual (chat Milestone 9)
// ==========================================================
const float L2 = 6.3;              // shoulder -> elbow, efektif
const float L3 = 11.46;            // elbow -> titik cengkeram gripper (rigid)
const float SHOULDER_HEIGHT = 8.3; // tinggi meja -> shoulder, cm

// "DOWN" = terverifikasi fisik (default). "UP" = belum diuji,
// jangan dipakai sebelum ditest lengan beneran bisa nekuk ke situ.
#define ELBOW_CONFIG_DOWN

// Arah rotasi base: 0 derajat = kanan, 180 derajat = kiri.
// x+ (arah putih/kanan) -> sudut servo makin KECIL dari home.
// Kalau nanti dites dan arahnya kebalik, tinggal ganti +1 jadi -1.
const int BASE_ANGLE_SIGN = -1;

// ==========================================================
Servo baseServo, shoulderServo, elbowServo, gripperServo;
String inputBuffer = "";

void setup() {
  Serial.begin(115200);

  baseServo.attach(PIN_BASE);
  shoulderServo.attach(PIN_SHOULDER);
  elbowServo.attach(PIN_ELBOW);
  gripperServo.attach(PIN_GRIPPER);

  baseServo.write(BASE_HOME);
  shoulderServo.write(SHOULDER_HOME);
  elbowServo.write(ELBOW_HOME);
  gripperServo.write(GRIPPER_OPEN);

  delay(1000);

  Serial.println("=== Milestone 9: IK Ready ===");
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
  if (line.length() == 0) return;

  int firstComma = line.indexOf(',');
  int secondComma = line.indexOf(',', firstComma + 1);

  if (firstComma == -1 || secondComma == -1) {
    Serial.println("ERR");
    return;
  }

  char color = line.charAt(0);
  float x_cm = line.substring(firstComma + 1, secondComma).toFloat();
  float y_cm = line.substring(secondComma + 1).toFloat();

  if (color != 'B' && color != 'W') {
    Serial.println("ERR");
    return;
  }

  int baseAngle, shoulderAngle, elbowAngle;
  solveIK(x_cm, y_cm, baseAngle, shoulderAngle, elbowAngle);

  Serial.print("IK -> base:");
  Serial.print(baseAngle);
  Serial.print(" shoulder:");
  Serial.print(shoulderAngle);
  Serial.print(" elbow:");
  Serial.println(elbowAngle);

  moveServoSmooth(baseServo, "Base", baseAngle);
  moveServoSmooth(shoulderServo, "Shoulder", shoulderAngle);
  moveServoSmooth(elbowServo, "Elbow", elbowAngle);

  // Pick/Drop/Home fisik (gripper close-open, gerak ke drop zone)
  // menyusul di Milestone 10 - Pick and Place.

  Serial.println("DONE");
}

// ==========================================================
// Inverse Kinematics
// ==========================================================
void solveIK(float x_cm, float y_cm, int &baseAngle, int &shoulderAngle, int &elbowAngle) {

  // --- Base (azimuth) ---
  float azimuth_rad = atan2(x_cm, y_cm);
  float azimuth_deg = azimuth_rad * 180.0 / PI;

  float baseF = BASE_HOME + (BASE_ANGLE_SIGN * azimuth_deg);
  baseAngle = clampServo((int)round(baseF));

  // --- Shoulder + Elbow (2-link planar) ---
  float r = sqrt(x_cm * x_cm + y_cm * y_cm);
  float h = sqrt(r * r + SHOULDER_HEIGHT * SHOULDER_HEIGHT);

  // Shoulder
  float cosA = (L2 * L2 + h * h - L3 * L3) / (2 * L2 * h);
  cosA = constrain(cosA, -1.0, 1.0);  // clamp defensif, r_max check di-skip
  float A = acos(cosA) * 180.0 / PI;
  float theta = 155 - A;
  float shoulderF = 90 + theta;
  shoulderAngle = clampServo((int)round(shoulderF));

  // Elbow
  float cosAlpha = (L2 * L2 + L3 * L3 - h * h) / (2 * L2 * L3);
  cosAlpha = constrain(cosAlpha, -1.0, 1.0);
  float alpha = acos(cosAlpha) * 180.0 / PI;

  float phi;
  #ifdef ELBOW_CONFIG_DOWN
    phi = alpha - 87;
  #else
    // ELBOW_CONFIG_UP - belum diverifikasi hardware, dugaan tanda saja.
    phi = -(alpha - 87);
  #endif

  float elbowF = 90 - phi;
  elbowAngle = clampServo((int)round(elbowF));
}

int clampServo(int angle) {
  if (angle < 0) return 0;
  if (angle > 180) return 180;
  return angle;
}

// ==========================================================
// Positional Servo Helper (base, shoulder, elbow, gripper)
// Base sekarang positional juga (sudah direvisi di hardware),
// jadi dipakai bareng helper yang sama, bukan baseRotate() lagi.
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

  servo.write(targetAngle);
}