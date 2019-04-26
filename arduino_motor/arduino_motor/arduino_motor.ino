#include <PID_v1.h>

#include <math.h>

uint16_t counterTick = 0;
uint8_t sensorPin = 3;
uint8_t PWM = 9;
int currTime = 0;
int prevTime = 0;

double inchesPerTick= 2.0; //number of plastic spokes 
double ips = 0;
double wheel = 7.85; //wheel circumference in inches
double timeInt = 0;

double spd = 0;
double Kp=0, Ki=0, Kd = 0;
double targetSpd = 20;

bool dFlag = true;
bool updated = false;

PID myPID(&ips,&spd,&targetSpd,Kp,Ki,Kd, DIRECT);

void setup() {
  Serial.begin(9600);
  attachInterrupt(digitalPinToInterrupt(sensorPin), ticker, RISING);
  pinMode(PWM,OUTPUT);
  analogWrite(PWM,0);
  Kp = 0.3; Ki = 10; Kd = 0.05;
  myPID.SetOutputLimits(0,255);
  myPID.SetTunings(Kp,Ki,Kd);
  myPID.SetSampleTime(20);
  analogWrite(PWM,0);
  myPID.SetMode(AUTOMATIC);
  prevTime = micros();
}

void loop(){
  if(!dFlag){
    delay(1);
    dFlag = true;
  }
  updateSerial();
  updated = false;
  delay(100);
  if(!updated){
    collectTime();
    ips = counterTick/(timeInt);
    writePID();
  }
} 
void updateSerial(){
  if(Serial.available()){
    targetSpd = (Serial.read() - '0')/255.0;
  }
}
void collectips(){
  double k = timeInt/1000.0;
  ips = counterTick/inchesPerTick/k;
}
void collectTime(){
  currTime = micros();
  timeInt = currTime - prevTime;
  prevTime = currTime;
}
void writePID(){
  myPID.Compute();
  analogWrite(PWM,spd);
}
void ticker(void){
  if(dFlag){
      counterTick++;
      dFlag = false;
    }
  if(counterTick == 5){
    collectTime();
    ips = 5/(timeInt);
    writePID();
    counterTick = 0;
    updated = true;
  }
} 
