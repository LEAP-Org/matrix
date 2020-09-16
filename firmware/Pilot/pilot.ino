/*
 * pilot.ino
 * 
 * 8-Bit Development Tesseract Software Driver.
 * 
 * The shift clock (SRCLK) is defined by a 555 in mono and bistable mode for debugging. Each clk
 * pulse is counted by an interrupt service and when 8 pulses are counted the RCLK is pulsed.
 * The firmware in essence will act in place of a synchronous 4 bit ripple counter while controlling
 * the serial output on each clk pulse.
 * 
 * @author Christian Sargusingh
 * @version --
 * Copyright © 2020 LEAP. All Rights Reserved.
 */

#define RCLK 8
#define SRCLK 3
#define SER 4
#define LEN 32

volatile int srclk = 0;
volatile int ser_index = -1;

const char *message = "LEAP";
bool tx_bits[LEN];

// Initial setup of the serial port, pins, and optional startup sequence
void setup() {
    Serial.begin(9600);
    pinMode(RCLK, OUTPUT);
    pinMode(SRCLK, INPUT);
    pinMode(SER, OUTPUT);
    attachInterrupt(digitalPinToInterrupt(SRCLK), srclk_interrupt, RISING);
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
    
}

void srclk_interrupt() {
    // Each shift clock pulse, set new bit on the serial bus and count up the pulses until the 8th 
    // pulse is received
    Serial.println("Interrupt Service Routine executing");
    ser_index++;
    if (tx_bits[ser_index] == true) {
        digitalWrite(SER, HIGH);
    } else {
        digitalWrite(SER, LOW);
    }
    if (srclk == 7){
        digitalWrite(RCLK, HIGH);
        srclk = 0;
    } else {
        srclk ++;
    }
}

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
 