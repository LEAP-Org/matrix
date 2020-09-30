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
    digitalWrite(SS, HIGH); // enforce SS stays high
    SPI.begin();
    Serial.println("Setup Complete");
}

void loop() {
    byte c;
    digitalWrite(SS, LOW); // enable chip select
    Serial.println("Writing to ICSP using SPI port");
    for (const char * p = "LEAP"; c = *p; p++){
        SPI.transfer(c);
    }
    Serial.println("Transfer complete");
    digitalWrite(SS, HIGH); // enable chip select
    delay(1000);
}
 