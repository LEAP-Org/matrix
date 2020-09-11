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
 */

#define RCLK 14
#define SRCLK 14
#define SER 14

volatile int srclk = 0;
const char *message = "Hello World!";

// Initial setup of the serial port, pins, and optional startup sequence
void setup() {
    Serial.begin(9600);
    pinMode(RCLK, OUTPUT);
    pinMode(SRCLK, INPUT);
    attachInterrupt(srclk_interrupt)
    pinMode(SER, OUTPUT);

    // represent each byte of message in its binary components
    for (int byte_index = 0; byte_index < strlen(message); byte_index++) {
        char tx_byte = message[byte_index];
        for (int bit_index = 0; bit_index < 8; bit_index++){
            bool tx_bit = tx_byte & (0x80 >> bit_index);
        }
    }
}

void loop() {

}

void srclk_interrupt() {
    if (srclk == 7){
        digitalWrite(RCLK, 1);
        srclk = 0;
    } else {
        srclk ++;
    }
}

void serial_out() {

}
 