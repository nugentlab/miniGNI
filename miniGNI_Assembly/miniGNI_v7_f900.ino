//
// Firmware for the mini-GNI unit.
// Version 7 
// Frequency: 900 MHz
// v2  --  10/01/2018  Changed the myservo.attach() calls to happen right before we want to move the servo. This prevents
//                     the servo from moving right when the unit is powered on. 
// v5  --  04/01/2019  Added support for the 9-DOF orientation sensor and made it compatible with v5 of the base station
// v5a --  04/10/2019  Added support for the AM-2302 temperature humidity sensor (DHT22 type)
// v6a --  04/11/2019  Removed ability of control station v5a to receive from multiple-GNIs because it doesn't work
// v7  --  07/26/2019  Added comments and fixed organization


//Modes: define the features that are connected:
//#define USE_SERIAL      // use the serial port...only do this if plugged into a computer!
#define USE_WIRELESS    // Talk over the RFM95 LoRa Radio (adafruit id# 3178)
#define USE_BARO        // Use the MPL3115A2 pressure/altitude/temperature sensor (adafruit id# 1893)
#define USE_SD          // Use the SD card and real time clock (adafruit id# 2922)
#define USE_DOF         // Use the 9-DOF orientation sensor (adafruit id# 2472)
#define USE_DHT         // Use the AM-2302 temperature/humidity sensor (adafruit id# 393)

#include <SPI.h>
#include <Wire.h>
#include <Servo.h>


//pinouts:
#define SERVO_PIN 9 
#define SD_CHIP_SELECT 10
#define RFM95_CS 8
#define RFM95_RST 4
#define RFM95_INT 3
#define DHTPIN 6


//radio
#ifdef USE_WIRELESS
  #include <RH_RF95.h>
  #define RF95_FREQ 900.0 //change this depending on what mini-GNI + control station pair
  RH_RF95 rf95(RFM95_CS, RFM95_INT);
  int16_t packetnum = 0;  // packet counter, we increment per xmission
#endif


//temperature humidity sensor
#ifdef USE_DHT
  #include "DHT.h"
  #define DHTTYPE DHT22
  DHT dht(DHTPIN, DHTTYPE);
#endif


//9-DOF sensor
#ifdef USE_DOF
  #include <Adafruit_Sensor.h>
  #include <Adafruit_BNO055.h>
  #include <utility/imumaths.h>
  Adafruit_BNO055 bno = Adafruit_BNO055();
#endif


//barometer
#ifdef USE_BARO
  #include <Adafruit_MPL3115A2.h>
  Adafruit_MPL3115A2 baro = Adafruit_MPL3115A2();
#endif


//sd card and rtc
#ifdef USE_SD
  #include <SD.h>
  #include "RTClib.h"
  RTC_PCF8523 rtc;
  File logfile;
#endif


//servo motor position
Servo myservo;
int pos = 0;            // variable to store the servo position
bool door_status = 0;   // 0:closed, 1:open


void setup() 
{
  String setup_error = "NONE";
  pinMode(SERVO_PIN, OUTPUT);

  #ifdef USE_DHT
    dht.begin();
  #endif
  
  #ifdef USE_SERIAL
    Serial.begin(115200);
    while (!Serial) { delay(1); } // wait!
    Serial.println("MiniGNI");
    Serial.println();
  #endif

  #ifdef USE_WIRELESS
    pinMode(RFM95_RST, OUTPUT);
    digitalWrite(RFM95_RST, HIGH);
    digitalWrite(RFM95_RST, LOW);
    delay(10);
    digitalWrite(RFM95_RST, HIGH);
    delay(10);
    if(!rf95.init()) {
      setup_error = "RF INIT";
    }
    if (!rf95.setFrequency(RF95_FREQ)) {
      setup_error = "RF FREQ";
    }
  #endif  

  #ifdef USE_BARO
    if (! baro.begin()) {
      setup_error = "BARO INIT";
    }
  #endif

  #ifdef USE_DOF
    if(!bno.begin()){
      setup_error = "DOF INIT";
    }
  #endif
  
  #ifdef USE_SD
    if ( !rtc.initialized()) {
      Serial.println("RTC is NOT running! Setting now");
      rtc.adjust(DateTime(F(__DATE__), F(__TIME__))); //sets the RTC to the date & time this sketch was compiled
    }
    if (!SD.begin(SD_CHIP_SELECT)) {
      Serial.println("Card init. failed!");
    }
    char filename[15];
    strcpy(filename, "ANALOG00.TXT");
    for (uint8_t i = 0; i < 100; i++) {
      filename[6] = '0' + i/10;
      filename[7] = '0' + i%10;
      if (! SD.exists(filename)) {
        break;
      }
    }
  #endif
  
  myservo.attach(SERVO_PIN);
  myservo.write(180); //start closed!
  delay(2000); //wait for the movement
  myservo.detach();
  
}


int lenMicroSecondsOfPeriod = 20 * 1000; // 20 milliseconds (ms)
int closedPosition = 1.0 * 1000; // 1.0 ms is 0 degrees
int openPosition = 2.0 * 1000; // 2.0 ms is 180 degrees


void loop() {
  delay(1000);
  char message_save[65];
  char message_send[19];

  char open_command[20];
  char close_command[20];

  sprintf(open_command, "OPEN %02d",1);
  sprintf(close_command, "CLOSE %02d",1);

  int Year   = 0;
  int Month  = 0;
  int Day    = 0;
  int Hour   = 0;
  int Minute = 0;
  int Second = 0;
  int altm_int  = 0;
  int tempC_int = 0;
  int presP_int = 0;
  int rhDH_int = 0;
  int tempDH_int = 0;
  
  float x_deg = 0;
  float y_deg = 0;
  float z_deg = 0;
  
  #ifdef USE_SD
    DateTime now = rtc.now();
    Year   = now.year();
    Month  = now.month();
    Day    = now.day();
    Hour   = now.hour();
    Minute = now.minute();
    Second = now.second();
  #endif

  //read in the DH22 temperature and humidity
  #ifdef USE_DHT
    float rhDH = dht.readHumidity();
    float tempDH = dht.readTemperature();
    rhDH_int = round(100*rhDH);
    tempDH_int = round(100*tempDH);
  #endif

  //read in the altitude and temperature
  #ifdef USE_BARO
    float altm  = baro.getAltitude();
    float tempC = baro.getTemperature();
    float presP = baro.getPressure();
    altm_int  = round(100*altm);
    tempC_int = round(100*tempC);
    presP_int = round(100*presP);
  #endif

  //read orientation from the 9-DOF
  #ifdef USE_DOF
    sensors_event_t event;
    bno.getEvent(&event);
    x_deg = event.orientation.x;
    y_deg = event.orientation.y;
    z_deg = event.orientation.z;
  #endif 

  //create a message to save to SD card and another message to send via radio
  sprintf(message_save, "%04d%02d%02dT%02d%02d%02d,%06d,%04d,%06d,%04d,%04d,%1d,%2.2f,%2.2f,%2.2f",Year,Month,Day,Hour,Minute,Second,altm_int,tempC_int,presP_int,rhDH_int,tempDH_int,door_status,x_deg,y_deg,z_deg);
  sprintf(message_send, "%06d,%04d,%04d,%1d",altm_int,rhDH_int,tempDH_int,door_status);

  #ifdef USE_SERIAL    
    Serial.println(message_save);
  #endif
  
  #ifdef USE_SD
    digitalWrite(8,HIGH);
    delay(100);
    File logfile = SD.open("datalog.csv", FILE_WRITE);
    logfile.println(message_save);
    logfile.close();
    digitalWrite(8,LOW);
    Serial.println("Transmitting..."); // Send a message to rf95_server  
    Serial.print("Sending "); Serial.println(message_send);
    Serial.println("Sending...");
    delay(10);
   #endif

   #ifdef USE_WIRELESS
      message_send[18] = 0;
      rf95.send((uint8_t *)message_send,21);
      delay(10);
      rf95.waitPacketSent();
      // Now wait for a reply
      uint8_t buf[RH_RF95_MAX_MESSAGE_LEN];
      uint8_t len = sizeof(buf);
      if (rf95.waitAvailableTimeout(1000))
      { 
        // Should be a reply message for us now   
       if (rf95.recv(buf,&len))
       {
          Serial.print("Got reply: ");
          Serial.println((char*)buf);
          Serial.print("RSSI: ");
          Serial.println(rf95.lastRssi(), DEC);
          if( strcmp( (char*)buf ,open_command) == 0){
            myservo.attach(9);
            for (pos = 180; pos >= 0; pos -= 1) { // goes from 180 degrees to 0 degrees
              myservo.write(pos);                 // tell servo to go to position in variable 'pos'
              delay(15);                          // waits 15ms for the servo to reach the position
            }
            myservo.detach();
            door_status = 1;
          }
          if( strcmp( (char*)buf ,close_command) == 0){
            myservo.attach(9);
            for (pos = 0; pos <= 180; pos += 1) { 
              myservo.write(pos);              
              delay(15);                       
            }
            door_status = 0;
            delay(1000);
            myservo.detach();
          }
        }
        else
        {
          Serial.println("Receive failed");
        }
      }
      else
      {
      }
  #endif
}


