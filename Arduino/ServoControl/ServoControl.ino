// Arduino/ServoControl/ServoControl.ino
//
// Milestone 8 - Kontrol Servo (sweep test).
// Menggerakkan ke-4 servo secara berurutan untuk verifikasi wiring +
// kontrol dasar, sebelum masuk Inverse Kinematics (Milestone 9).
//
// 3 servo positional (shoulder, elbow, gripper): SG90 180 derajat,
// dikontrol pakai target angle (Servo::write) dengan smooth step.
//
// 1 servo base: SG90 360 continuous rotation, TIDAK punya sudut
// absolut (Decision #029, Milestone 7) - dikontrol pakai arah +
// durasi, ditangani via fungsi terpisah, bukan lewat helper yang
// sama dengan 3 servo positional (Decision #035, #037, Milestone 8).

#include <Servo.h>

// ==========================================================
// Pin Configuration - GANTI sesuai wiring kamu
// ==========================================================
const int PIN_BASE     = 8;
const int PIN_SHOULDER = 9;
const int PIN_ELBOW    = 10;
const int PIN_GRIPPER  = 11;

// ==========================================================
// Positional Servo Config (shoulder, elbow, gripper)
// ==========================================================
const int SHOULDER_HOME = 90;
const int ELBOW_HOME    = 90;
const int GRIPPER_OPEN  = 90;
const int GRIPPER_CLOSE = 20;

const int SERVO_STEP_DELAY = 15;   // ms antar step -> gerakan lebih halus
const int SERVO_STEP_SIZE  = 2;    // derajat per step

// ==========================================================
// Base Servo Config (continuous rotation)
// ==========================================================
// Placeholder awal. Kalau base tidak diam sempurna di BASE_STOP_PULSE
// (masih pelan-pelan muter), atau arah CW/CCW ternyata kebalik pas
// sweep test, kalibrasi ulang tiga nilai ini (Decision #035).
const int BASE_STOP_PULSE = 90;
const int BASE_CW_PULSE   = 100;
const int BASE_CCW_PULSE  = 80;

enum BaseDirection { BASE_CW, BASE_CCW };

// ==========================================================
Servo baseServo;
Servo shoulderServo;
Servo elbowServo;
Servo gripperServo;

void setup() {

  Serial.begin(115200);

  baseServo.attach(PIN_BASE);
  shoulderServo.attach(PIN_SHOULDER);
  elbowServo.attach(PIN_ELBOW);
  gripperServo.attach(PIN_GRIPPER);

  // Base harus diam dari awal, sebelum apapun lain terjadi
  baseServo.write(BASE_STOP_PULSE);

  // Servo positional mulai dari home
  shoulderServo.write(SHOULDER_HOME);
  elbowServo.write(ELBOW_HOME);
  gripperServo.write(GRIPPER_OPEN);

  delay(1000);  // beri waktu servo settle di posisi awal

  Serial.println("=== Milestone 8: Servo Sweep Test ===");

  runSweepTest();

  Serial.println("=== Sweep Test Selesai ===");
}

void loop() {
  // Sweep test cuma jalan sekali di setup(); loop() sengaja kosong.
}

// ==========================================================
// Sweep Test
// ==========================================================
void runSweepTest() {

  Serial.println("[Shoulder] sweep 60 -> 120 -> home");
  moveServoSmooth(shoulderServo, "Shoulder", 60);
  moveServoSmooth(shoulderServo, "Shoulder", 120);
  moveServoSmooth(shoulderServo, "Shoulder", SHOULDER_HOME);

  Serial.println("[Elbow] sweep 60 -> 120 -> home");
  moveServoSmooth(elbowServo, "Elbow", 60);
  moveServoSmooth(elbowServo, "Elbow", 120);
  moveServoSmooth(elbowServo, "Elbow", ELBOW_HOME);

  Serial.println("[Gripper] close -> open");
  moveServoSmooth(gripperServo, "Gripper", GRIPPER_CLOSE);
  moveServoSmooth(gripperServo, "Gripper", GRIPPER_OPEN);

  Serial.println("[Base] rotate CW 1s -> stop -> CCW 1s -> stop");
  baseRotate(BASE_CW, 1650);
  delay(500);
  baseRotate(BASE_CCW, 1135);
  delay(500);
}

// ==========================================================
// Positional Servo Helper (shoulder, elbow, gripper)
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

// ==========================================================
// Base Servo Helper (continuous rotation)
// Ditangani terpisah total, tidak pakai moveServoSmooth() (Decision #037)
// karena interface-nya beda: arah + durasi, bukan target angle.
// ==========================================================
void baseRotate(BaseDirection direction, unsigned long durationMs) {

  int pulse = (direction == BASE_CW) ? BASE_CW_PULSE : BASE_CCW_PULSE;

  Serial.print("  Base: rotate ");
  Serial.print(direction == BASE_CW ? "CW" : "CCW");
  Serial.print(" selama ");
  Serial.print(durationMs);
  Serial.println("ms");

  baseServo.write(pulse);
  delay(durationMs);
  baseServo.write(BASE_STOP_PULSE);

  Serial.println("  Base: stop");
}
