// -*- lsst-c++ -*-
/**
 * LEAP Systems
 * See COPYRIGHT file at the top of the source tree.
 * Copyright © 2020 LEAP. All Rights Reserved.
*/

#include <Arduino.h>
#include "src/segment.h"

Segment::Segment(int pin1, int pin2, int pin3, int pin4, int pin5, int pin6, int pin7, boolean msb) {
    // implementation for the KER 5621 BSR module
    // pulled low to enable LED segment
    if (msb == true) {
        this->pins[0] = pin1;
        this->pins[1] = pin6;
        this->pins[2] = pin2;
        this->pins[3] = pin3;
        this->pins[4] = pin4;
        this->pins[5] = pin5;
        this->pins[6] = pin7;
    } else {
        this->pins[0] = pin1;
        this->pins[1] = pin2;
        this->pins[2] = pin3;
        this->pins[3] = pin4;
        this->pins[4] = pin5;
        this->pins[5] = pin6;
        this->pins[6] = pin7;
    }

    for (int i = 0; i < 7; i++) {
        pinMode(pins[i], OUTPUT);
        digitalWrite(pins[i], HIGH);
    }
}

void Segment::displayHex(int hex) {
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
    for (int segment = 0; segment < 7; segment++) {
        if (hex < 0 || hex > 15) {
            // display error
            bitToWrite = bitRead(bytestream[16], segment);
        } else {
            bitToWrite = bitRead(bytestream[hex], segment);
        }
        digitalWrite(pins[segment], bitToWrite);
    }
}