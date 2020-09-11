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

#define RCLK 8
#define SRCLK 7
#define SER 4

volatile int srclk = 0;
volatile int ser_index = 0;

const char *message = "Hello World!";
bool tx_bits[12*8];

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
            tx_bits[(1+bit_index)+(8*byte_index)] = tx_byte & (0x80 >> bit_index);
        }
    }
}

void loop() {

}

void srclk_interrupt() {
    // Each shift clock pulse, set new bit on the serial bus and count up the pulses until the 8th 
    // pulse is received
    serial_out();
    if (srclk == 7){
        digitalWrite(RCLK, 1);
        srclk = 0;
    } else {
        srclk ++;
    }
}

void serial_out() {
    digitalWrite(SER, tx_bits[ser_index]);
    ser_index++;
}
 