#include <TeensyThreads.h>


int PWM = 9;  //  pin for PWM
int interruptPin = 10, wantedVelocity;
double err, err_last, Kp, Ki, Kd, voltage, integral;
float maxV = 5.0;
float scale = 255/maxV;

void setup() {
  err = err_last = integral = 0;
  wantedVelocity = 0;
  Kp = Ki = Kd = 1;           // SHOULD BE TESTED
  pinMode(PWM, OUTPUT);
  Serial1.begin(38400);
}

void loop() {
  analogWrite(PIDcontrol(getVelocity(), wantedVelocity), PWM);
  //  if connection is coming read velocity;
  if(Serial1.available() > 0){
    wantedVelocity = Serial.read() * scale;
  }
}


double getVelocity(){
  return 1.1;   // return the current velocity
}

double PIDcontrol(double currV, int actualV){
  err = currV - actualV;
  integral += err;
  double delta_err = err - err_last;
  err_last = err; 
  return actualV * (Kp * err + Ki * integral + Kd * delta_err);
}
