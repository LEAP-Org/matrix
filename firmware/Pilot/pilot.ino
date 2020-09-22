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
#include <stdio.h> // for function sprintf

#define ROLL 8  // rollover indicator
#define RCLK 7  // RCLK
#define SRCLR 9 // shift register clear
#define SRCLK 3 // arduino UNO uses pin 2 and 3 as valid ISR pins
#define SER 4   // serial out
#define LEN 32  // set length of message

volatile byte srclk = 0;
volatile int ser_index = -1;

const char *message = "LEAP";
bool tx_bits[LEN];
char format[16];

// Initial setup of the serial port, pins, and optional startup sequence
void setup() {
    Serial.begin(9600);
    pinMode(RCLK, OUTPUT);
    pinMode(SRCLK, INPUT);
    pinMode(SER, OUTPUT);
    pinMode(SRCLR, OUTPUT);
    attachInterrupt(digitalPinToInterrupt(SRCLK), update_serin, FALLING);
    attachInterrupt(digitalPinToInterrupt(SRCLK), rclk_count, RISING);
    // represent each byte of message in its binary components
    for (int byte_index = 0; byte_index < strlen(message); byte_index++) {
        char tx_byte = message[byte_index];
        for (int bit_index = 0; bit_index < 8; bit_index++){
            tx_bits[(byte_index*8)+bit_index] = tx_byte & (0x80 >> bit_index);
        }
    }
    //load first bit onto the serial bus
    write_to_bus()

    // clear shift register before write cycle begins
    digitalWrite(SRCLR, HIGH);
    Serial.println("Setup Complete");
}

void loop() {
    
}

void write_to_bus(){
    if (tx_bits[ser_index] == true) {
        digitalWrite(SER, HIGH);
        Serial.println(" | Writing 1");
    } else {
        digitalWrite(SER, LOW);
        Serial.println(" | Writing 0");
    }
    ser_index++;
}

void update_serin() {
    // On falling edge of clk pulse present the next bit on the serial bus
    Serial.println("Interrupt Service Routine executing for update_serin()");
    // if (ser_index == LEN-1){
    //     ser_index = -1;
    // }
    ser_index++;
    sprintf(format, "Bit Index: %i", ser_index);
    Serial.print(format);
    write_to_bus()
}

void rclk_count() {
    // Each shift clock pulse, set new bit on the serial bus and count up the pulses until the 8th 
    // pulse is received
    Serial.println("Interrupt Service Routine executing for rclk_count()");
    
    if (srclk == 8){
        digitalWrite(RCLK, HIGH);
        srclk = 0;
    } else {
        digitalWrite(RCLK, LOW);
    }
    srclk ++;
    
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
 