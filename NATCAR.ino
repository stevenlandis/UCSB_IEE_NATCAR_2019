#include <SPI.h>
#include <avr/pgmspace.h>

// Registers
#define REG_Product_ID                           0x00
#define REG_Revision_ID                          0x01
#define REG_Motion                               0x02
#define REG_Delta_X_L                            0x03
#define REG_Delta_X_H                            0x04
#define REG_Delta_Y_L                            0x05
#define REG_Delta_Y_H                            0x06
#define REG_SQUAL                                0x07
#define REG_Pixel_Sum                            0x08
#define REG_Maximum_Pixel                        0x09
#define REG_Minimum_Pixel                        0x0a
#define REG_Shutter_Lower                        0x0b
#define REG_Shutter_Upper                        0x0c
#define REG_Frame_Period_Lower                   0x0d
#define REG_Frame_Period_Upper                   0x0e
#define REG_Configuration_I                      0x0f
#define REG_Configuration_II                     0x10
#define REG_Frame_Capture                        0x12
#define REG_SROM_Enable                          0x13
#define REG_Run_Downshift                        0x14
#define REG_Rest1_Rate                           0x15
#define REG_Rest1_Downshift                      0x16
#define REG_Rest2_Rate                           0x17
#define REG_Rest2_Downshift                      0x18
#define REG_Rest3_Rate                           0x19
#define REG_Frame_Period_Max_Bound_Lower         0x1a
#define REG_Frame_Period_Max_Bound_Upper         0x1b
#define REG_Frame_Period_Min_Bound_Lower         0x1c
#define REG_Frame_Period_Min_Bound_Upper         0x1d
#define REG_Shutter_Max_Bound_Lower              0x1e
#define REG_Shutter_Max_Bound_Upper              0x1f
#define REG_LASER_CTRL0                          0x20
#define REG_Observation                          0x24
#define REG_Data_Out_Lower                       0x25
#define REG_Data_Out_Upper                       0x26
#define REG_SROM_ID                              0x2a
#define REG_Lift_Detection_Thr                   0x2e
#define REG_Configuration_V                      0x2f
#define REG_Configuration_IV                     0x39
#define REG_Power_Up_Reset                       0x3a
#define REG_Shutdown                             0x3b
#define REG_Inverse_Product_ID                   0x3f
#define REG_Motion_Burst                         0x50
#define REG_SROM_Load_Burst                      0x62
#define REG_Pixel_Burst                          0x64

byte initComplete=0;
byte testctr=0;
unsigned long currTime;
unsigned long timer;
volatile int xydat[2], xydatprev[2];
volatile byte movementflag=0;

const int ncs = 10; //pin for chip select
const int mosi = 11; //pin for mosi
const int miso = 12; //pin for miso
const int sck = 13; //pin for sck
const int mot = 2; //pin for mot

byte resolution  = 0x09;
double totalDistance = 0;
unsigned long timeInterval = 0;
extern const unsigned short firmware_length;
extern const unsigned char firmware_data[];

void setup() {
  Serial.begin(9600);
  
  pinMode(ncs, OUTPUT);
  pinMode(mosi, OUTPUT);
  pinMode(miso, INPUT);
  pinMode(sck, OUTPUT);

  digitalWrite(sck,HIGH);
  digitalWrite(mosi,LOW);
  digitalWrite(ncs,HIGH);
  
  attachInterrupt(mot, UpdatePointer, FALLING);
  Serial.println("here");
  performStartup();  
  delay(100);
  initComplete=9;
  adns_write_reg(0x02,0);
  adns_write_reg(REG_Configuration_I,resolution); //sets resolution to 1800 counts per inch

}

void loop() {
/*Prints out the distance traveled in the x and y planes  
  if(movementflag){
    Serial.print("x = ");
    Serial.print( convTwosComp(xydat[0]) );
    Serial.print(" | ");
    Serial.print("y = ");
    Serial.println( convTwosComp(xydat[1]) );

    movementflag=0;
    }
  else if(!digitalRead(mot)){
    UpdatePointer();
  }
*/

 if(movementflag){
  timeInterval = micros() - timeInterval;
//  Serial.println("Current data: ");
//  Serial.print("X: ");
//  Serial.println(convTwosComp(xydat[0]));
//  Serial.print("Y: ");
//  Serial.println(convTwosComp(xydat[1]));
  Serial.print("Distance: ");
  totalDistance = totalDistance + distancex(convTwosComp(xydat[0])) + distancey(convTwosComp(xydat[1]));
  Serial.println(totalDistance);
//  Serial.println(digitalRead(mot),BIN);
//  Serial.print("X-velocity: ");
//  Serial.println(velocityx(distancex(convTwosComp(xydat[0])), timeInterval));
//  Serial.print("Y-velocity: ");
//  Serial.println(velocityy(distancey(convTwosComp(xydat[1])), timeInterval));
  movementflag = 0;
 }
 else if(!digitalRead(mot)){
  UpdatePointer();
 }
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
  
