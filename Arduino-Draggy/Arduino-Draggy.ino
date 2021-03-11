#include <TinyGPS++.h>
#include <SoftwareSerial.h>

#define RX 2
#define TX 3
#define GPSBAUD 38400

TinyGPSPlus gps;
SoftwareSerial gpsSerial(RX, TX);

int hour_ = 0;

void displayInfo();
int valid();

void setup() {
  Serial.begin(38400);
  gpsSerial.begin(GPSBAUD);
  // Serial.println("Time, Latitide, Longitude, Altitude, hdop");
}

void loop() {
  while(gpsSerial.available() > 0) {
    if (gps.encode(gpsSerial.read())) {
       if (valid()) {
         displayInfo(); 
       } else {
         // Serial.println("Invalid Data"); 
       }
    }
  }

  if (millis() > 5000 && gps.charsProcessed() < 10) {
    Serial.println("No GPS detected!");
    while (true);
  }
}

void displayInfo(){
    hour_ = gps.time.hour() + 2;
    if (hour_ < 10) {
      Serial.print(F("0"));
    } 
    Serial.print(hour_);
    Serial.print(":");
    if (gps.time.minute() < 10){
      Serial.print(F("0"));
    } 
    Serial.print(gps.time.minute());
    Serial.print(":");
    if (gps.time.second() < 10) {
      Serial.print(F("0")); 
    }
    Serial.print(gps.time.second());
    Serial.print(".");
    Serial.print(gps.time.centisecond());
    Serial.print(",");
    
    Serial.print(gps.location.lat(), 6);
    Serial.print(",");
    Serial.print(gps.location.lng(), 6);
    Serial.print(",");
    Serial.print(gps.altitude.meters());
    Serial.print(",");
    Serial.print(gps.hdop.value());
    Serial.print(",");
    Serial.println(gps.speed.mps());
}

int valid() {
  return (gps.location.isValid() && gps.location.isUpdated() && gps.altitude.isValid());  
}
