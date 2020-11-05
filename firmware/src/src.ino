// -*- lsst-c++ -*-
/**
 * LEAP Systems
 * See COPYRIGHT file at the top of the source tree.
 * Copyright © 2020 LEAP. All Rights Reserved.
 * 
 * @file main.ino
 *
 * @brief Pilot system uses SPI interface to facilitate high speed serial data 
 * transfer to the tesseract shift register. See: 
 * https://arduino.stackexchange.com/questions/16348/how-do-you-use-spi-on-an-arduino
 *
 * @author Christian Sargusingh
 * Contact: christian@leapsystems.online
 */
#include <SPI.h>
#include <SoftwareSerial.h>
#include <Segment.h>

// Maximum amount of hex characters that can be stored to convert to binary

Segment segment_lsb(2, 3, 4, 5, 6, 7, 8, false);
Segment segment_msb(9, 14, 15, 16, 17, 18, 19, true);
byte msb;
byte lsb;
uint8_t c = 0;  // for incoming serial data

// Initial setup of the serial port, pins, and optional startup sequence
void setup() {
    Serial.begin(9600);
    // Note SS is Digital pin 11 on UNO R3
    digitalWrite(SS, HIGH);  // enforce SS stays high
    SPI.begin();
}

void loop() {
    if (Serial.available() > 0) {
        c = Serial.read();
        if (c == 0xD || c == 0xA) {
            Serial.println("Received D or A EOS byte");
        } else {
            msb = c >> 4;
            lsb = c & 0x0F;
            Serial.print("Received: ");
            Serial.println(c, HEX);
            Serial.println(msb, HEX);
            Serial.println(lsb, HEX);
            segment_lsb.displayHex(lsb);
            segment_msb.displayHex(msb);
            SPI.beginTransaction(SPISettings(2000000, MSBFIRST, SPI_MODE0));
            digitalWrite(SS, LOW);
            SPI.transfer(c);
            digitalWrite(SS, HIGH);
            SPI.endTransaction();
        }
    }
}
