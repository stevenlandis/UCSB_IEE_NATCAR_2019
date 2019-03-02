#include <SPI.h>
#include <avr/pgmspace.h>
#include <math.h>
#include "adns9800_registers.h"
#include "RingBuffer.h"

byte initComplete=0;
byte testctr=0;

unsigned long currTime;
unsigned long prevTime = 0;
unsigned long timer;

volatile int xydat[2], xydatprev[2];
volatile byte movementflag=0;

const int ncs = 10; //pin for chip select
const int mosi = 11; //pin for mosi
const int miso = 12; //pin for miso
const int sck = 13; //pin for sck
const int mot = 2; //pin for mot
const int PWM = 9;  //  pin for PWM

byte resolution  = 0x09;
double totalDistance = 0;
unsigned long timeInterval = 0;

extern const unsigned short firmware_length;
extern const unsigned char firmware_data[];

double wantedVelocity;
double err,err_last, Kp, Ki, Kd, voltage, integral;

float maxV = 5.0;
float scale = 255/maxV;
double maxcarspeed = 25.0; //km/hour (found online)
double factor = 255/(maxcarspeed*(1/3600.0)*pow(10, 5));

void setup() {
  Serial.begin(9600);
  
  pinMode(ncs, OUTPUT);
  pinMode(mosi, OUTPUT);
  pinMode(miso, INPUT);
  pinMode(sck, OUTPUT);
  pinMode(23,OUTPUT);
  pinMode(20,INPUT);
  digitalWrite(sck,HIGH);
  digitalWrite(mosi,LOW);
  digitalWrite(ncs,HIGH);

  pinMode(PWM, OUTPUT);
  analogWrite(PWM,100);
  attachInterrupt(mot, UpdatePointer, FALLING);
  
  performStartup(); 
   
  delay(100);
  initComplete=9;
  adns_write_reg(0x02,0);
  adns_write_reg(REG_Configuration_I,resolution); //sets resolution to 7200 counts per inch

  err = err_last = integral = 0;
  wantedVelocity = 0;
  Kp = 0.5;
  Kd = 0.5;
  Ki = 0;// SHOULD BE TESTED
 //Serial1.begin(38400);
 
}

  double pid = 0;
void loop(){
  analogWrite(23, (int)pid);
  pid = PIDcontrol(analogRead(20)*255/1023, 200);
  Serial.println(pid);
}

//
//void loop() {
// if(movementflag){
//  currTime= micros();
//  timeInterval = currTime - prevTime;
//  prevTime = currTime;
//  
//  //totalDistance = totalDistance + distancex(convTwosComp(xydat[0]));
//  double xdelt = distancex(convTwosComp(xydat[0]));
//  double ydelt = distancey(convTwosComp(xydat[1]));
//  
// 
//  double xvelocity = velocityx(xdelt, timeInterval);
//  double yvelocity = velocityy(ydelt, timeInterval);
//  double velocity = sqrt(pow(xvelocity,2) + pow(yvelocity,2));
//  Serial.println(velocity,4);
//  //Serial.print("PWM: ");
//  //Serial.println(velocity,4);
//  /*if(Serial1.available() > 0){
//    wantedVelocity = Serial.read() * scale;
//    wantedVelocity = 1.2;
//    analogWrite(PIDcontrol(velocity, wantedVelocity), PWM);
//  }*/
//  
//  wantedVelocity = 10;
//  //analogWrite(PWM,PIDcontrol(velocity,wantedVelocity));
//  //Serial.println(PIDcontrol(velocity,wantedVelocity),5);
//  
//  movementflag = 0;
//  /*Serial.print("Mot: ");
//  Serial.println(digitalRead(mot));*/
// }
// else if(!digitalRead(mot)){
//  UpdatePointer();  
// }
//}

double PIDcontrol(double currV, double actualV){
  err = currV - actualV;
  integral += err;
  double delta_err = err - err_last;
  err_last = err; 
  return actualV *(Kp * err + Ki * integral + Kd * delta_err);
}

void adns_com_begin(){ //communication start
  digitalWrite(ncs, LOW);
}

void adns_com_end(){ //communication end
  digitalWrite(ncs, HIGH);
}

void clockgen(){
  digitalWrite(sck,LOW);
  delayMicroseconds(0.15);
  digitalWrite(sck,HIGH);
}

byte adns_read_reg(byte reg_addr){
  adns_com_begin();
  byte temp = reg_addr;//&0x7f;
  byte data = 0;
  // send adress of the register, with MSBit = 0 to indicate it's a read
  digitalWrite(mosi,LOW);
  clockgen();
  for(int i = 0; i<7; i++){
    digitalWrite(mosi,bitRead(temp,6-i));
    clockgen();
  }
  delayMicroseconds(100); // tSRAD
  for(int i = 0; i<8; i++){
    clockgen();
    temp = digitalRead(miso);
    if(temp){
      bitSet(data,7-i);
    }
  }

  delayMicroseconds(1); // tSCLK-NCS for read operation is 120ns
  adns_com_end();
  delayMicroseconds(19); //  tSRW/tSRR (=20us) minus tSCLK-NCS
  return data;
}

void adns_write_reg(byte reg_addr, byte data){
  adns_com_begin();
  byte temp = reg_addr|0x80;
  //send adress of the register, with MSBit = 1 to indicate it's a write
  for(int i = 0; i<8; i++){
    digitalWrite(mosi,bitRead(temp,7-i));
    clockgen();
  }
  for(int i = 0; i<8; i++){
    digitalWrite(mosi,bitRead(data,7-i));
    clockgen();
  }
  delayMicroseconds(20); // tSCLK-NCS for write operation
  adns_com_end();
  delayMicroseconds(100); // tSWW/tSWR (=120us) minus tSCLK-NCS. Could be shortened, but is looks like a safe lower bound 
}

void adns_upload_firmware(){
  // send the firmware to the chip, cf p.18 of the datasheet
  Serial.println("Uploading firmware...");
  // set the configuration_IV register in 3k firmware mode
  adns_write_reg(REG_Configuration_IV, 0x02); // bit 1 = 1 for 3k mode, other bits are reserved 
  
  // write 0x1d in SROM_enable reg for initializing
  adns_write_reg(REG_SROM_Enable, 0x1d); 
  
  // wait for more than one frame period
  delay(10); // assume that the frame rate is as low as 100fps... even if it should never be that low
  
  // write 0x18 to SROM_enable to start SROM download
  adns_write_reg(REG_SROM_Enable, 0x18); 
  
  // write the SROM file (=firmware data) 
  
  adns_com_begin();
  byte temp = REG_SROM_Load_Burst | 0x80; // write burst destination adress
  //Serial.println();
  for(int i = 0; i<8; i++){
    digitalWrite(mosi,bitRead(temp,7-i));
    clockgen();
  }
  delayMicroseconds(15);
  
  unsigned char c;
 
  for(int i = 0; i < firmware_length; i++){ 
    c = (unsigned char)pgm_read_byte(firmware_data + i);
    for(int i = 0; i<8; i++){
      digitalWrite(mosi,bitRead(c,7-i));
      clockgen();
    }
    delayMicroseconds(15);
  }
  adns_com_end();
  }


void performStartup(void){
  adns_com_end(); // ensure that the serial port is reset
  adns_com_begin(); // ensure that the serial port is reset
  adns_com_end(); // ensure that the serial port is reset
  adns_write_reg(REG_Power_Up_Reset, 0x5a); // force reset
  delay(50); // wait for it to reboot
  // read registers 0x02 to 0x06 (and discard the data)
  adns_read_reg(REG_Motion);
  adns_read_reg(REG_Delta_X_L);
  adns_read_reg(REG_Delta_X_H);
  adns_read_reg(REG_Delta_Y_L);
  adns_read_reg(REG_Delta_Y_H);
  // upload the firmware
  adns_upload_firmware();
  delay(10);
  //enable laser(bit 0 = 0b), in normal mode (bits 3,2,1 = 000b)
  // reading the actual value of the register is important because the real
  // default value is different from what is said in the datasheet, and if you
  // change the reserved bytes (like by writing 0x00...) it would not work.
  byte laser_ctrl0 = adns_read_reg(REG_LASER_CTRL0);
  adns_write_reg(REG_LASER_CTRL0, laser_ctrl0 & 0xf0 );
  
  delay(1);

  Serial.println("Optical Chip Initialized");
  }

void UpdatePointer(void){
  if(initComplete==9){

    digitalWrite(ncs,LOW);
    xydatprev[0] = xydat[0];
    xydatprev[1] = xydat[1];
    xydat[0] = (int)adns_read_reg(REG_Delta_X_L);
    xydat[1] = (int)adns_read_reg(REG_Delta_Y_L);
    digitalWrite(ncs,HIGH);     

    movementflag=1;
    }
  }

int convTwosComp(int b){
  //Convert from 2's complement
  if(b & 0x80){
    b = -1 * ((b ^ 0xff) + 1);
    }
  return b;
}
  
