//
//  for the mini-GNI control station
//  Version 7
//  Frequency: 900 MHz
//  v5  --              Added ability to receive from multiple mini-GNI v5 units
//                      and minor edits
//  v6a --  04/11/2019  Removed the v5 function to receive from multiple mini-GNI
//                      v5 units but kept minor edits.
//  v7  --  07/26/2019  Minor edits adding comments and fixing structure


//#define USE_SERIAL //comment this out if not using the serial stream

#include <SPI.h>
#include <RH_RF95.h>
#include <Wire.h>
#include <Adafruit_GFX.h>    // Core graphics library
#include <Adafruit_ILI9341.h> // Hardware-specific library
#include <Adafruit_STMPE610.h> //touchscreen
 
#define RFM95_CS 8
#define RFM95_RST 4
#define RFM95_INT 3
#define RF95_FREQ 900.0 //change according to mini-GNI + control station pair
 
RH_RF95 rf95(RFM95_CS, RFM95_INT);

#define LED 13

#define STMPE_CS 6
#define TFT_CS   9
#define TFT_DC   10
#define SD_CS    5

// This is calibration data for the raw touch data to the screen coordinates
#define TS_MINX 3800
#define TS_MAXX 100
#define TS_MINY 100
#define TS_MAXY 3750

Adafruit_ILI9341 tft = Adafruit_ILI9341(TFT_CS, TFT_DC);
Adafruit_STMPE610 ts = Adafruit_STMPE610(STMPE_CS);
 
void setup()
{
  pinMode(LED, OUTPUT);
  pinMode(RFM95_RST, OUTPUT);
  digitalWrite(RFM95_RST, HIGH);

  #ifdef USE_SERIAL
    Serial.begin(115200);
    while (!Serial) { delay(1); }
    delay(100);
    Serial.println("Mini GNI base station v05!");
  #endif
 
  // manual reset
  digitalWrite(RFM95_RST, LOW);
  delay(10);
  digitalWrite(RFM95_RST, HIGH);
  delay(10);
 
  while (!rf95.init()) {
    #ifdef USE_SERIAL
      Serial.println("LoRa radio init failed");
    #endif
    while (1);
  }
  #ifdef USE_SERIAL
    Serial.println("LoRa radio init OK!");
  #endif
   
  if (!rf95.setFrequency(RF95_FREQ)) {
    #ifdef USE_SERIAL
      Serial.println("setFrequency failed");
    #endif
    while (1);
  }
  #ifdef USE_SERIAL
    Serial.print("Set Freq to: "); Serial.println(RF95_FREQ);
  #endif
   
  rf95.setTxPower(23, false);  //5 to 23

  if (!ts.begin()) {
    #ifdef USE_SERIAL
      Serial.println("Couldn't start touchscreen controller");
    #endif
    while (1);
  }
  
  #ifdef USE_SERIAL
    Serial.println("Touchscreen started");
  #endif
  
  tft.begin();
  yield();
  tft.fillScreen(ILI9341_BLACK);
  yield();
  tft.drawRect(0, 0, 240, 40, ILI9341_BLUE);
  tft.setCursor(18,8);
  tft.setTextColor(ILI9341_WHITE);
  
  tft.setTextSize(3);
  tft.println("Mini GNI v7");
  
  tft.drawRect(15,220,95,60,ILI9341_BLUE);
  tft.fillRect(15,220,95,60,ILI9341_BLUE);
  tft.setCursor(25,240);
  tft.println("OPEN");

  tft.drawRect(130,220,95,60,ILI9341_BLUE);
  tft.fillRect(130,220,95,60,ILI9341_BLUE);
  tft.setCursor(135,240);
  tft.println("CLOSE");

  tft.setTextColor(ILI9341_WHITE,ILI9341_BLACK);

}

char user_input = 'n';
char outgoing_message[20] = "ACK";

void loop(){
  
  #ifdef USE_SERIAL
    if(Serial.available()){
      user_input = Serial.read();
      Serial.println(user_input);
    }
  #endif

  digitalWrite(LED, LOW);
  digitalWrite(RFM95_CS, HIGH);
  
  TS_Point p;
  while (ts.touched()) {
    while (! ts.bufferEmpty()) {
      p = ts.getPoint();
      p.x = map(p.x, TS_MINX, TS_MAXX, 0, tft.width());
      p.y = map(p.y, TS_MINY, TS_MAXY, 0, tft.height());
      //true_y = tft.height() -  map(p.x, TS_MINX, TS_MAXX, 0, tft.height());
      //true_x = map(p.y, TS_MINY, TS_MAXY, 0, tft.width());
      
    }
    ts.writeRegister8(STMPE_INT_STA, 0xFF); // reset all ints
  }

  if( (p.y > 210) && (p.y < 270) && (p.x > 15) && (p.x < 110) ){
    user_input = 'o';
    tft.fillRect(15,220,95,60,ILI9341_WHITE);
    tft.setTextColor(ILI9341_BLACK,ILI9341_WHITE);
    tft.setCursor(25,240);
    tft.println("OPEN");
  }
  if( (p.y > 210) && (p.y < 270) && (p.x > 130) && (p.x < 225) ){
    user_input = 'c';
    tft.fillRect(130,220,95,60,ILI9341_WHITE);
    tft.setTextColor(ILI9341_BLACK,ILI9341_WHITE);
    tft.setCursor(135,240);
    tft.println("CLOSE");
  }
  
  digitalWrite(RFM95_CS, LOW);
  delay(20);
  
  if (rf95.available()){
    uint8_t buf[RH_RF95_MAX_MESSAGE_LEN];
    uint8_t len = sizeof(buf);
    if (rf95.recv(buf, &len)){
      digitalWrite(LED, HIGH);
      #ifdef USE_SERIAL
        Serial.print((char*)buf);
        Serial.print(", RSSI: ");
        Serial.println(rf95.lastRssi(), DEC);
      #endif

        tft.setTextColor(ILI9341_WHITE,ILI9341_BLACK);
        tft.setCursor(20,60);
        tft.print("ALT: ");
        printPart(buf,0,4);
        tft.setCursor(20,100);
        tft.print("TEMP: ");
        printPart(buf,12,2);
        tft.print(".");
        printPart(buf,14,1);
        tft.setCursor(20,140);
        tft.print("RH:   ");
        printPart(buf,7,2);
        tft.print(".");
        printPart(buf,9,1);
        tft.setCursor(20,180);
        tft.print("DOOR: ");
        if( buf[17] == '1'){
          tft.print("OPEN  ");
        }
        if( buf[17] == '0'){
          tft.print("SHUT");
        }
    }
  }

  if( user_input != 'n'){
    if( user_input == 'o'){
      #ifdef USE_SERIAL
        Serial.println("opening door!");
      #endif
      //strncpy((char*)outgoing_message, "OPEN DOOR", 20);
      sprintf(outgoing_message,"OPEN %02d",1);
    }
    if( user_input == 'c'){
      #ifdef USE_SERIAL
        Serial.println("closing door!");
      #endif
      sprintf(outgoing_message,"CLOSE %02d",1);
      //strncpy((char*)outgoing_message, "CLOSE DOOR", 20);
    }
    #ifdef USE_SERIAL
      Serial.println( (char*)outgoing_message);
    #endif
      
    //rf95.send(outgoing_message, sizeof(outgoing_message));
    rf95.send((uint8_t *)outgoing_message, 20);
    rf95.waitPacketSent();
    user_input = 'n';

    tft.fillRect(15,220,95,60,ILI9341_BLUE);
    tft.setTextColor(ILI9341_WHITE,ILI9341_BLUE);
    tft.setCursor(25,240);
    tft.println("OPEN");
    tft.fillRect(130,220,95,60,ILI9341_BLUE);
    tft.setTextColor(ILI9341_WHITE,ILI9341_BLUE);
    tft.setCursor(135,240);
    tft.println("CLOSE");
  }
  
}

void printPart(uint8_t* txt, byte start, byte len){
  for(byte i = 0; i < len; i++){
    tft.write(txt[start + i]);
  } 
}
