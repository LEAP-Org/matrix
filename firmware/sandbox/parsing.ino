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
#define INT 12
#define SER 4
#define LEN 32

volatile int ser_index = -1;

const char *message = "LEAP";
bool tx_bits[LEN];

// Initial setup of the serial port, pins, and optional startup sequence
void setup() {
    Serial.begin(9600);
    pinMode(SRCLK, INPUT);
    pinMode(SER, OUTPUT);
    pinMode(INT, OUTPUT);
    // attachInterrupt(digitalPinToInterrupt(SRCLK), increment_ser_index, RISING);

    // represent each byte of message in its binary components
    for (int byte_index = 0; byte_index < strlen(message); byte_index++) {
        char tx_byte = message[byte_index];
        for (int bit_index = 0; bit_index < 8; bit_index++){
            tx_bits[(byte_index*8)+bit_index] = tx_byte & (0x80 >> bit_index);
        }
    }
    Serial.println("Setup Complete");
}

void loop() {
    // Phase 1 CLK +
    digitalWrite(INT, HIGH);
    ser_index++;
    if (tx_bits[ser_index] == true) {
        digitalWrite(SER, HIGH);
    } else {
        digitalWrite(SER, LOW);
    }
    delay(1000);
    // Phase 2 CLK -
    digitalWrite(INT, LOW);
    // reset once max is reached
    if (ser_index == LEN){
        ser_index = -1;
    }
    delay(1000);
    // serial_debug();
}

// void increment_ser_index() {
    
// }

void serial_debug(){
    // Serial Monitor Debug 
    if (ser_index < LEN+1) {
        ser_index++;
        if (tx_bits[ser_index] == true) {
            Serial.print("1");
        } else {
            Serial.print("0");
        }
    }
}
 