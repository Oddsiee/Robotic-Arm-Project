#include <Servo.h>

Servo clawServo;
Servo shoulderServo;
Servo elbowServo;
Servo baseServo;

// ========================
// Pin Servo
// ========================
const byte CLAW_PIN = 9;
const byte SHOULDER_PIN = 10;
const byte ELBOW_PIN = 11;
const byte BASE_PIN = 12;

// ========================
// Claw
// ========================
const int CLAW_OPEN = 90;
const int CLAW_CLOSE = 10;

bool clawOpen = false;

// ========================
// Posisi Awal Servo
// ========================
int shoulderPos = 90;
int elbowPos = 110;

const int STEP = 1.7;

// ========================
// Detach Servo
// ========================

unsigned long lastCommandTime = 0;
bool servoAttached = true;

void setup() {

  Serial.begin(9600);

  clawServo.attach(CLAW_PIN);
  shoulderServo.attach(SHOULDER_PIN);
  elbowServo.attach(ELBOW_PIN);
  baseServo.attach(BASE_PIN);

  clawServo.write(CLAW_CLOSE);

  shoulderServo.write(shoulderPos);
  elbowServo.write(elbowPos);

  // Stop continuous servo
  baseServo.write(90);
}

void attachAllServos() {

  if (!servoAttached) {

    clawServo.attach(9);
    shoulderServo.attach(10);
    elbowServo.attach(11);
    baseServo.attach(12);

    // Kembalikan ke posisi terakhir
    clawServo.write(clawOpen ? CLAW_OPEN : CLAW_CLOSE);
    shoulderServo.write(shoulderPos);
    elbowServo.write(elbowPos);
    baseServo.write(90);

    servoAttached = true;
  }
}

void detachAllServos() {

  if (servoAttached) {

    clawServo.detach();
    shoulderServo.detach();
    elbowServo.detach();
    baseServo.detach();

    servoAttached = false;
  }
}

void loop() {

  if (Serial.available()) {

    char cmd = Serial.read();

    attachAllServos();
    lastCommandTime = millis();

    switch(cmd){

      // ======================
      // Shoulder Naik
      // ======================
      case 'W':

        shoulderPos += STEP;
        shoulderPos = constrain(shoulderPos, 0, 180);

        shoulderServo.write(shoulderPos);
        clawServo.detach();
        break;

      // ======================
      // Shoulder Turun
      // ======================
      case 'S':

        shoulderPos -= STEP;
        shoulderPos = constrain(shoulderPos, 0, 180);

        shoulderServo.write(shoulderPos);
        clawServo.detach();
        break;

      // ======================
      // Elbow Naik
      // ======================
      case 'Q':

        elbowPos += STEP;
        elbowPos = constrain(elbowPos, 70, 110);

        elbowServo.write(elbowPos);
        clawServo.detach();
        break;

      // ======================
      // Elbow Turun
      // ======================
      case 'E':

        elbowPos -= STEP;
        elbowPos = constrain(elbowPos, 70, 110);

        elbowServo.write(elbowPos);
        clawServo.detach();
        break;

      // ======================
      // Base Kiri
      // ======================
      case 'A':

        baseServo.write(100);

        break;

      // ======================
      // Base Kanan
      // ======================
      case 'D':

        baseServo.write(80);

        break;

      // ======================
      // Stop Base
      // ======================
      case 'X':

        baseServo.write(90);

        break;

      // ======================
      // Toggle Claw
      // ======================
     case 'Y':

    clawOpen = !clawOpen;

    clawServo.attach(9);

    if(clawOpen)
        clawServo.write(CLAW_OPEN);
    else
        clawServo.write(CLAW_CLOSE);

    break;
    }
  if (servoAttached && millis() - lastCommandTime > 10) {

    detachAllServos();
    }
  }
}