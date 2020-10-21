/*
 * pilot_spi.ino
 * 
 * 8-Bit Development Tesseract Software Driver.
 * 
 * Pilot SPI uses the SPI interface to facilitate high speed serial data transfer to the tesseract
 * shift register. https://arduino.stackexchange.com/questions/16348/how-do-you-use-spi-on-an-arduino
 * 
 * @author Christian Sargusingh
 * @version --
 * Copyright © 2020 LEAP. All Rights Reserved.
 */
#include <SPI.h>

// Initial setup of the serial port, pins, and optional startup sequence
void setup() {
    Serial.begin(9600);
    // Note SS is Digital pin 11 on UNO R3
    digitalWrite(SS, HIGH); // enforce SS stays high
    SPI.begin();
    Serial.println("Setup Complete");
}

void loop() {
    byte c;
    SPI.beginTransaction(SPISettings(2000000, MSBFIRST, SPI_MODE0));
    for (const char * p = "LEAP"; c = *p; p++){
        digitalWrite(SS, LOW);
        SPI.transfer(c);
        digitalWrite(SS, HIGH);
        delay(10);
    }
    SPI.endTransaction();
}