#include "DHT.h"
#include <Wire.h>
#include <TimeLib.h>
#include <DS1307RTC.h>

DHT dht(4, DHT11);

// -=Pendefinisian Pin=-
//LED PIN
const int biru = 9;
const int hijau = 10;
const int merah = 11;

//IC 74HC595 PIN
const int latchPin = 6;
const int clockPin = 7;
const int dataPin = 5;
const int vibsen = A3;

int dt = 0;
int data = 0;
int satuan = 0;
int belas  = 0;

String i;
String itg1;
String alpha;
String command;
String json_dht;
String json_sens;

unsigned long mil;
unsigned long lmil1 = 0;
unsigned long lmil2 = 0;
unsigned long lmil3 = 0;
unsigned long lmil4 = 0;

//SevenSegment Binary 
const byte datArray[10] = {
  0b00000011, //0
  0b01110111, //1
  0b00001101, //2
  0b00010101, //3
  0b01110001, //4
  0b10010001, //5
  0b10000001, //6
  0b00110111, //7
  0b00000001, //8
  0b00010001  //9
};

void setup() {
  Serial.begin(9600);
  dht.begin();
  
  for (int l = 5; l < 12; l++) {
    pinMode(l, OUTPUT);
  }
  
  pinMode(2, OUTPUT);
  pinMode(3, OUTPUT);

  digitalWrite(biru, HIGH);
  digitalWrite(hijau, HIGH);
  digitalWrite(merah, HIGH);

}

void loop() {
// Sengaja saya tidak membuat multiple void karena akan membuat Arduino berkerja sedikit lamban yang akan berpengaruh terhadap tampilan 7Segment 
  
  mil = millis();
  while (Serial.available() > 0) {
    data = Serial.read();

    if (isAlpha(data)) {
      command += (char)data;
    }

    i += (char)data;
    if (isDigit(data)) {
      itg1 += (char)data;
    }
    else if (isAlpha(data)) {
      alpha += (char)data;
    }

    //=======================================================[ RGB LED ]=======================================================


    if ( data == '\n') {
      int itg = map(itg1.toInt(), 0, 255, 255, 0);
      if ( alpha == "merah") {
        analogWrite(merah, itg);
      }
      if ( alpha == "biru") {
        analogWrite(biru, itg);
      }
      if (alpha == "hijau") {
        analogWrite(hijau, itg);
      }
      command = "";
      alpha = "";
      itg1 = "";
    }

    if (command == "ledoff") {
      digitalWrite(merah, HIGH);
      digitalWrite(hijau, HIGH);
      digitalWrite(biru, HIGH);
      command = "";
    }
  }

  //=======================================================[ 7 Segment ]=======================================================

  if (mil - lmil1 >= 200) {
    satuan = satuan + 1;
    if (satuan == 10) {
      satuan = 0;
      belas = belas + 1;
      if (belas == 10) {
        belas = 0;
        lmil1 = mil;
      }
      lmil1 = mil;
    }
    lmil1 = mil;
  }


  if (mil - lmil2 >= 5) {
    digitalWrite(3, LOW);
    digitalWrite(latchPin, LOW);
    shiftOut(dataPin, clockPin, MSBFIRST, datArray[belas]);
    digitalWrite(latchPin, HIGH);
    digitalWrite(2, HIGH);
    if (mil - lmil2 >= 10) {
      digitalWrite(2, LOW);
      digitalWrite(latchPin, LOW);
      shiftOut(dataPin, clockPin, MSBFIRST, datArray[satuan]);
      digitalWrite(latchPin, HIGH);
      digitalWrite(3, HIGH);
      lmil2 = mil;
    }
  }
  //=======================================================[ DHT Sensor ]=======================================================


  if (mil - lmil3 >= 2000) {
    float hum = dht.readHumidity();
    float tem = dht.readTemperature();
    // mengakali agar data yang dikeluarkan adalah data JSON, di arduino ada librarynya, tapi akibatnya proses pengolahan JSON nya sedikit lambat
    json_dht += "{\"hum\":\"";
    json_dht += hum;
    json_dht += "\",\"tem\":\"";
    json_dht += tem;
    json_dht += "\"}";
    Serial.println(json_dht);
    json_dht = "";
    lmil3 = mil;
  }
  
  //=======================================================[ Vib Sensor ]=======================================================
  
  if (mil - lmil4 >= 100) {
    json_sens += "{\"vib_sens\":\"";
    json_sens += analogRead(A3);
    json_sens += "\"}";
    Serial.println(json_sens);
    json_sens = "";
    lmil4 = mil;
  }

  // fungsi mil - lmil = waktu, karena jika menggunakan delay, proses lainya akan ikut terjeda, sehingga digunakanlah manipulasi waktu dari oscillator
  // millis() adalah waktu bawaan arduino, berasal dari hardware detak(oscillator), mulai dari 0 ketika arduino menyala, akan reset selama kurang lebih 49.7 hari
  
}
