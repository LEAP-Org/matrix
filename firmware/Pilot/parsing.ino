/*
 * parsing.ino
 * 
 * Test Software for 8-Bit Development Tesseract
 * 
 * @author Christian Sargusingh
 * @version --
 * Copyright © 2020 LEAP. All Rights Reserved.
 */

#define SRCLK 7
#define SER 4

volatile int ser_index = -1;

const char *message = "Hello World!";
bool tx_bits[12*8];

// Initial setup of the serial port, pins, and optional startup sequence
void setup() {
    Serial.begin(9600);
    pinMode(SRCLK, INPUT);
    pinMode(SER, OUTPUT);
    attachInterrupt(digitalPinToInterrupt(SRCLK), increment_ser_index, RISING);

    // represent each byte of message in its binary components
    for (int byte_index = 0; byte_index < strlen(message); byte_index++) {
        char tx_byte = message[byte_index];
        for (int bit_index = 0; bit_index < 8; bit_index++){
            tx_bits[(1+bit_index)+(8*byte_index)] = tx_byte & (0x80 >> bit_index);
        }
    }
}

void loop() {
    
}

void increment_ser_index() {
    // Each shift clock pulse, set new bit on the serial bus and count up the pulses until the 8th 
    // pulse is received
    ser_index++;
    digitalWrite(SER, tx_bits[ser_index]);
}

void serial_out() {
    
}
 