/*
 * main.ino
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
// #include "Segment.h"

// Maximum amount of hex characters that can be stored to convert to binary

class Segment {
    private:
        int pins[7];

    public:
        Segment(int pin1, int pin2, int pin3, int pin4, int pin5, int pin6, int pin7, boolean msb) {
            // implementation for the 5621 BSR module
            // pulled low to enable LED segment
            if (msb == true){
                this->pins[0] = pin1;
                this->pins[1] = pin6;
                this->pins[2] = pin2;
                this->pins[3] = pin3;
                this->pins[4] = pin4;
                this->pins[5] = pin5;
                this->pins[6] = pin7;
            }else {
                this->pins[0] = pin1;
                this->pins[1] = pin2;
                this->pins[2] = pin3;
                this->pins[3] = pin4;
                this->pins[4] = pin5;
                this->pins[5] = pin6;
                this->pins[6] = pin7;
            }
            
    
            for(int i = 0; i < 7; i++) {
                pinMode(pins[i], OUTPUT);
                digitalWrite(pins[i], HIGH);
            }
        };

        void displayHex(int hex) {
            // mapped based on direct sequential pin mappings
            byte bytestream[] = {
                B0000010,  //  0
                B1101110,  //  1
                B1000001,  //  2
                B1001000,  //  3
                B0101100,  //  4
                B0011000,  //  5
                B0010000,  //  6
                B1001110,  //  7
                B0000000,  //  8
                B0001000,  //  9
                B0000100,  //  A
                B0110000,  //  B
                B0010011,  //  C
                B1100000,  //  D
                B0010001,  //  E
                B0010101,  //  F
                B1111101  //  Error
            };
            boolean bitToWrite;
            
            for(int segment = 0; segment < 7; segment++) {
                if(hex < 0 || hex > 15) {
                    // display error
                    bitToWrite = bitRead(bytestream[16], segment);
                }else {
                    bitToWrite = bitRead(bytestream[hex], segment);
                }
                digitalWrite(pins[segment], bitToWrite);
            }
        }
};

Segment segment_lsb(2, 3, 4, 5, 6, 7, 8, false);
Segment segment_msb(9, 14, 15, 16, 17, 18, 19, true);
byte msb;
byte lsb;
uint8_t c = 0; // for incoming serial data

// Initial setup of the serial port, pins, and optional startup sequence
void setup() {
    Serial.begin(9600);
    // Note SS is Digital pin 11 on UNO R3
    digitalWrite(SS, HIGH); // enforce SS stays high
    SPI.begin();
}

void loop() {
    if (Serial.available() > 0) {
        c = Serial.read();
        if (c==0xD || c==0xA){
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
    delay(500);
}