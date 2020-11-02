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
#include "Segment.h"

// Maximum amount of hex characters that can be stored to convert to binary
int c = 0; // for incoming serial data

Segment::Segment(int pin1, int pin2, int, pin3, int pin4, int pin5, int pin6, int pin7, int pin8) {
    pins[0] = pin1;
    pins[1] = pin2;
    pins[2] = pin3;
    pins[3] = pin4;
    pins[4] = pin5;
    pins[5] = pin6;
    pins[6] = pin7;
    pins[7] = pin8;
    
    for(int i = 0; i < 8; i++) {
        pinMode(pins[i], OUTPUT);
        digitalWrite(pins[i], HIGH);
    }
}

void Segment::displayHex(int number) {
    
    byte numbersToDisplay[] = {
        B10001000,  //  0
        B11101011,  //  1
        B01001100,  //  2
        B01001001,  //  3
        B00101011,  //  4
        B00011001,  //  5
        B00011000,  //  6
        B11001011,  //  7
        B00001000,  //  8
        B00001011,  //  9
        B00001010,  //  A
        B00111000,  //  B
        B10011100,  //  C
        B01101000,  //  D
        B00011100,  //  E
        B00011110,  //  F
        B01011101  //  Error
    };
    
    boolean bitToWrite;
    
    for(int segment = 0; segment < 8; segment++) {
        if(number < 0 || number > 15) {
            // display error
            bitToWrite = bitRead(numbersToDisplay[16], segment);
        }else {
            bitToWrite = bitRead(numbersToDisplay[number], segment);
        }
        digitalWrite(pins[segment], bitToWrite);
    }
}

// Initial setup of the serial port, pins, and optional startup sequence
void setup() {
    Serial.begin(9600);
    // Note SS is Digital pin 11 on UNO R3
    digitalWrite(SS, HIGH); // enforce SS stays high
    SPI.begin();
    Segment segment_lsb(2, 3, 4, 5, 6, 7, 8);
    Segment segment_msb(9, 14, 15, 16, 17, 18, 19);
}

void loop() {
    // if (Serial.available() > 0) {
    //     c = Serial.read();
    // }
    // SPI.beginTransaction(SPISettings(2000000, MSBFIRST, SPI_MODE0));
    // digitalWrite(SS, LOW);
    // SPI.transfer(c);
    // digitalWrite(SS, HIGH);
    // SPI.endTransaction();
    c++;
    Serial.println(c)
    segment_lsb.displayHex(c)
    segment_msb.displayHex(c)
}