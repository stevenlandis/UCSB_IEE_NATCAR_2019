#include <PID_v1.h>
#include <math.h>

#define LIGHT_DEBOUNCE_TIME 3 // in ms
#define N_LIGHT_TICKS 5 // number of ticks to read an ideal speed

uint16_t counterTick = 0;
uint8_t sensorPin = 3;
uint8_t PWM = 9;
// int currTime = 0;
// int prevTime = 0;

const double inchesPerTick= 2.0; //number of plastic spokes 
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
    updated = false;
    delay(100);
    updateSerial();
    if(!updated) {
        updateSpeed();
    }
} 
void updateSerial(){
    if(Serial.available()){
        targetSpd = ((double)Serial.read())/255.0;
    }
}
// use counterTick to calculate current speed and update PID
void updateSpeed() {
    static unsigned long prevTime = 0;
    unsigned long currTime = micros();
    unsigned long deltaTime = currTime - prevTime;
    prevTime = currTime;
    ips = ((double)counterTick)/((double)deltaTime) * inchesPerTick * 1000;
    counterTick = 0;
    writePID();
}
void writePID(){
    myPID.Compute();
    analogWrite(PWM,spd);
}
void ticker(void){
    // remember last triggered time for debouncing
    static unsigned long prevTime = 0;
    unsigned long currTime = micros();

    // test for debouncing
    if (currTime - prevTime > LIGHT_DEBOUNCE_TIME) {
        prevTime = currTime;
        updated = true;
        counterTick++;
        if (counterTick == N_LIGHT_TICKS) {
            updateSpeed();
        }
    }
}
// void collectips(){
//     double k = timeInt/1000.0;
//     ips = counterTick/inchesPerTick/k;
// }
// void collectTime(){
//     currTime = micros();
//     timeInt = currTime - prevTime;
//     prevTime = currTime;
// }
