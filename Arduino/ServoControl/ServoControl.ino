// Arduino/ServoControl/ServoControl.ino
//
// Milestone 8 - Kontrol Servo (sweep test).
// REVISI: Base diganti dari SG90 360 continuous rotation menjadi
// SG90 180 positional. Base sekarang dikontrol sama persis seperti
// shoulder/elbow/gripper lewat moveServoSmooth() (target angle),
// TIDAK ada lagi baseRotate() / time-based rotation.
//
// Catatan: Decision #029, #035, #037, #039, #040 (Milestone 8)
// di-superseded oleh perubahan hardware ini. Base tidak lagi butuh
// strategi durasi-per-derajat di Milestone 9 - sudut IK bisa
// langsung di-write() seperti servo positional lainnya.

#include <Servo.h>

// ==========================================================
// Pin Configuration
// ==========================================================
const int PIN_BASE     = 8;
const int PIN_SHOULDER = 9;
const int PIN_ELBOW    = 10;
const int PIN_GRIPPER  = 11;

// ==========================================================
// Positional Servo Config (base, shoulder, elbow, gripper)
// Semua 4 servo sekarang jenis yang sama: SG90 180 positional.
// ==========================================================
const int BASE_HOME     = 0;
const int SHOULDER_HOME = 90;
const int ELBOW_HOME    = 90;
const int GRIPPER_OPEN  = 90;
const int GRIPPER_CLOSE = 20;

const int SERVO_STEP_DELAY = 15;   // ms antar step -> gerakan lebih halus
const int SERVO_STEP_SIZE  = 2;    // derajat per step

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

  // Semua servo mulai dari home, termasuk base sekarang
  baseServo.write(BASE_HOME);
  shoulderServo.write(SHOULDER_HOME);
  elbowServo.write(ELBOW_HOME);
  gripperServo.write(GRIPPER_OPEN);

  delay(1000);  // beri waktu servo settle di posisi awal

  Serial.println("=== Milestone 8 (Revisi): Servo Sweep Test ===");
  Serial.println("Base sekarang SG90 180 positional, bukan continuous rotation.");

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

  Serial.println("[Base] sweep 0 -> 180 -> home");
  moveServoSmooth(baseServo, "Base", 0);
  moveServoSmooth(baseServo, "Base", 180);
  moveServoSmooth(baseServo, "Base", BASE_HOME);

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
}

// ==========================================================
// Positional Servo Helper - sekarang dipakai oleh SEMUA 4 servo
// (base, shoulder, elbow, gripper), karena semuanya sudah jenis
// SG90 180 positional yang sama.
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
