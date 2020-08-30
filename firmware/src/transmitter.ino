/*
 * transmitter.ino
 * Purpose: Translate a given serial input into its respective LED
 * pattern for the receiver to identiy and translate into data.
 * 
 * @author Aaron Huang
 * @version 03.19.2020
 * 
 */
 
// Outputs the serial data for input to the shift register (Blue)
int dataPin = 10;
// Shifts in one data bit in the register (Red)
int latchPin = 11;
// Releases the entire data set once all loaded (Green)
int clockPin = 12;
// Control the lighting of each layer respectively from bottom to top
int controlSwitch1 = 4;
int controlSwitch2 = 5;
int controlSwitch3 = 6;
int controlSwitch4 = 7;
// Number of LEDs available for display
int totalLED = 64;
// Number of layers in the cube
int totalFloor = 4;
// Counter variable to switch between frames
int frameCount = 0;
// Counter variable to switch between each layer
int floorCount = 0;
// Maximum time spent on each frame in ms
int singleFrameDelay = 100;
// Maximum time spent on each floor in ms
int singleFloorDelay = 1;
// Maximum amount of hex characters that can be stored to convert to binary
char hexArray[16];
// Maximum available binary bits to display
int frame[64];
 
// A array of array of patterns referenced for a startup sequence
// Pattern 1 represents a side- side pattern. Pattern 2 has a rotation pattern.
// Pattern 3 has an expansion pattern. Pattern 4 has a rotating expansion pattern.
char patterns[4][24][16] = {{{'0', '0', '0', 'F', '0', '0', '0', 'F', '0', '0', '0', 'F', '0', '0', '0', 'F'},
                               {'0', '0', 'F', '0', '0', '0', 'F', '0', '0', '0', 'F', '0', '0', '0', 'F', '0'},
                               {'0', 'F', '0', '0', '0', 'F', '0', '0', '0', 'F', '0', '0', '0', 'F', '0', '0'},
                               {'F', '0', '0', '0', 'F', '0', '0', '0', 'F', '0', '0', '0', 'F', '0', '0', '0'},
                               {'F', '0', '0', '0', 'F', '0', '0', '0', 'F', '0', '0', '0', 'F', '0', '0', '0'},
                               {'0', 'F', '0', '0', '0', 'F', '0', '0', '0', 'F', '0', '0', '0', 'F', '0', '0'},
                               {'0', '0', 'F', '0', '0', '0', 'F', '0', '0', '0', 'F', '0', '0', '0', 'F', '0'},
                               {'0', '0', '0', 'F', '0', '0', '0', 'F', '0', '0', '0', 'F', '0', '0', '0', 'F'},
                               {'F', 'F', 'F', 'F', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'},
                               {'0', '0', '0', '0', 'F', 'F', 'F', 'F', '0', '0', '0', '0', '0', '0', '0', '0'},
                               {'0', '0', '0', '0', '0', '0', '0', '0', 'F', 'F', 'F', 'F', '0', '0', '0', '0'},
                               {'0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', 'F', 'F', 'F', 'F'},
                               {'0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', 'F', 'F', 'F', 'F'},
                               {'0', '0', '0', '0', '0', '0', '0', '0', 'F', 'F', 'F', 'F', '0', '0', '0', '0'},
                               {'0', '0', '0', '0', 'F', 'F', 'F', 'F', '0', '0', '0', '0', '0', '0', '0', '0'},
                               {'F', 'F', 'F', 'F', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'},
                               {'8', '8', '8', '8', '8', '8', '8', '8', '8', '8', '8', '8', '8', '8', '8', '8'},
                               {'4', '4', '4', '4', '4', '4', '4', '4', '4', '4', '4', '4', '4', '4', '4', '4'},
                               {'2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2'},
                               {'1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1'},
                               {'1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1'},
                               {'2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2'},
                               {'4', '4', '4', '4', '4', '4', '4', '4', '4', '4', '4', '4', '4', '4', '4', '4'},
                               {'8', '8', '8', '8', '8', '8', '8', '8', '8', '8', '8', '8', '8', '8', '8', '8'}},
  
                               {{'8', '4', '2', '1', '8', '4', '2', '1', '8', '4', '2', '1', '8', '4', '2', '1'},
                               {'4', '4', '2', '2', '4', '4', '2', '2', '4', '4', '2', '2', '4', '4', '2', '2'},
                               {'2', '2', '4', '4', '2', '2', '4', '4', '2', '2', '4', '4', '2', '2', '4', '4'},
                               {'1', '2', '4', '8', '1', '2', '4', '8', '1', '2', '4', '8', '1', '2', '4', '8'},
                               {'0', '3', 'C', '0', '0', '3', 'C', '0', '0', '3', 'C', '0', '0', '3', 'C', '0'},
                               {'0', 'C', '3', '0', '0', 'C', '3', '0', '0', 'C', '3', '0', '0', 'C', '3', '0'},
                               {'8', '4', '2', '1', '8', '4', '2', '1', '8', '4', '2', '1', '8', '4', '2', '1'},
                               {'4', '4', '2', '2', '4', '4', '2', '2', '4', '4', '2', '2', '4', '4', '2', '2'},
                               {'2', '2', '4', '4', '2', '2', '4', '4', '2', '2', '4', '4', '2', '2', '4', '4'},
                               {'1', '2', '4', '8', '1', '2', '4', '8', '1', '2', '4', '8', '1', '2', '4', '8'},
                               {'0', '3', 'C', '0', '0', '3', 'C', '0', '0', '3', 'C', '0', '0', '3', 'C', '0'},
                               {'0', 'C', '3', '0', '0', 'C', '3', '0', '0', 'C', '3', '0', '0', 'C', '3', '0'},
                               {'8', '4', '2', '1', '8', '4', '2', '1', '8', '4', '2', '1', '8', '4', '2', '1'},
                               {'0', 'C', '3', '0', '0', 'C', '3', '0', '0', 'C', '3', '0', '0', 'C', '3', '0'},
                               {'0', '3', 'C', '0', '0', '3', 'C', '0', '0', '3', 'C', '0', '0', '3', 'C', '0'},
                               {'1', '2', '4', '8', '1', '2', '4', '8', '1', '2', '4', '8', '1', '2', '4', '8'},
                               {'2', '2', '4', '4', '2', '2', '4', '4', '2', '2', '4', '4', '2', '2', '4', '4'},
                               {'4', '4', '2', '2', '4', '4', '2', '2', '4', '4', '2', '2', '4', '4', '2', '2'},
                               {'8', '4', '2', '1', '8', '4', '2', '1', '8', '4', '2', '1', '8', '4', '2', '1'},
                               {'0', 'C', '3', '0', '0', 'C', '3', '0', '0', 'C', '3', '0', '0', 'C', '3', '0'},
                               {'0', '3', 'C', '0', '0', '3', 'C', '0', '0', '3', 'C', '0', '0', '3', 'C', '0'},
                               {'1', '2', '4', '8', '1', '2', '4', '8', '1', '2', '4', '8', '1', '2', '4', '8'},
                               {'2', '2', '4', '4', '2', '2', '4', '4', '2', '2', '4', '4', '2', '2', '4', '4'},
                               {'4', '4', '2', '2', '4', '4', '2', '2', '4', '4', '2', '2', '4', '4', '2', '2'}},
  
                               {{'0', '0', '0', '0', '0', '6', '6', '0', '0', '6', '6', '0', '0', '0', '0', '0'},
                               {'9', '0', '0', '9', '0', '0', '0', '0', '0', '0', '0', '0', '9', '0', '0', '9'},  
                               {'F', '9', '9', 'F', '9', '0', '0', '9', '9', '0', '0', '9', 'F', '9', '9', 'F'},
                               {'6', '9', '9', '6', '9', '0', '0', '9', '9', '0', '0', '9', '6', '9', '9', '6'},
                               {'0', '6', '6', '0', '6', '9', '9', '6', '6', '9', '9', '6', '0', '6', '6', '0'},
                               {'0', '0', '0', '0', '0', '6', '6', '0', '0', '6', '6', '0', '0', '0', '0', '0'},
                               {'F', 'F', 'F', 'F', 'F', '9', '9', 'F', 'F', '9', '9', 'F', 'F', 'F', 'F', 'F'},
                               {'F', 'F', 'F', 'F', 'F', 'F', 'F', 'F', 'F', 'F', 'F', 'F', 'F', 'F', 'F', 'F'},
                               {'0', '0', '0', '0', '0', '6', '6', '0', '0', '6', '6', '0', '0', '0', '0', '0'},
                               {'9', '0', '0', '9', '0', '0', '0', '0', '0', '0', '0', '0', '9', '0', '0', '9'},
                               {'F', '9', '9', 'F', '9', '0', '0', '9', '9', '0', '0', '9', 'F', '9', '9', 'F'},
                               {'6', '9', '9', '6', '9', '0', '0', '9', '9', '0', '0', '9', '6', '9', '9', '6'},
                               {'0', '6', '6', '0', '6', '9', '9', '6', '6', '9', '9', '6', '0', '6', '6', '0'},
                               {'0', '0', '0', '0', '0', '6', '6', '0', '0', '6', '6', '0', '0', '0', '0', '0'},
                               {'F', 'F', 'F', 'F', 'F', '9', '9', 'F', 'F', '9', '9', 'F', 'F', 'F', 'F', 'F'},
                               {'F', 'F', 'F', 'F', 'F', 'F', 'F', 'F', 'F', 'F', 'F', 'F', 'F', 'F', 'F', 'F'},
                               {'0', '0', '0', '0', '0', '6', '6', '0', '0', '6', '6', '0', '0', '0', '0', '0'},
                               {'9', '0', '0', '9', '0', '0', '0', '0', '0', '0', '0', '0', '9', '0', '0', '9'},
                               {'F', '9', '9', 'F', '9', '0', '0', '9', '9', '0', '0', '9', 'F', '9', '9', 'F'},
                               {'6', '9', '9', '6', '9', '0', '0', '9', '9', '0', '0', '9', '6', '9', '9', '6'},
                               {'0', '6', '6', '0', '6', '9', '9', '6', '6', '9', '9', '6', '0', '6', '6', '0'},
                               {'0', '0', '0', '0', '0', '6', '6', '0', '0', '6', '6', '0', '0', '0', '0', '0'},
                               {'F', 'F', 'F', 'F', 'F', '9', '9', 'F', 'F', '9', '9', 'F', 'F', 'F', 'F', 'F'},
                               {'F', 'F', 'F', 'F', 'F', 'F', 'F', 'F', 'F', 'F', 'F', 'F', 'F', 'F', 'F', 'F'}},
 
                              {{'0', '0', '0', '0', '0', '6', '6', '0', '0', '6', '6', '0', '0', '0', '0', '0'},
                                {'9', 'F', '2', '1', '9', '9', '9', '3', 'F', '9', '9', '6', '9', 'C', '0', '6'},
                                {'9', 'F', '2', '1', '9', '9', '9', '3', 'F', '9', '9', '6', '9', 'C', '0', '6'},
                                {'9', 'F', '2', '1', '9', '9', '9', '3', 'F', '9', '9', '6', '9', 'C', '0', '6'},
                                {'9', 'F', '2', '1', '9', '9', '9', '3', 'F', '9', '9', '6', '9', 'C', '0', '6'},
                                {'9', 'F', '2', '1', '9', '9', '9', '3', 'F', '9', '9', '6', '9', 'C', '0', '6'},
                                {'9', 'F', '2', '1', '9', '9', '9', '3', 'F', '9', '9', '6', '9', 'C', '0', '6'},
                                {'9', 'F', '2', '1', '9', '9', '9', '3', 'F', '9', '9', '6', '9', 'C', '0', '6'},
                                {'9', 'F', '2', '1', '9', '9', '9', '3', 'F', '9', '9', '6', '9', 'C', '0', '6'},
                                {'9', 'F', '2', '1', '9', '9', '9', '3', 'F', '9', '9', '6', '9', 'C', '0', '6'},
                                {'9', 'F', '2', '1', '9', '9', '9', '3', 'F', '9', '9', '6', '9', 'C', '0', '6'},
                                {'C', '7', '3', '2', 'C', '9', '1', '7', 'F', '9', '1', 'D', 'C', '1', '0', 'C'},
                                {'6', '6', '5', '5', 'E', '0', '1', 'F', 'F', '1', '9', 'B', '3', '2', '9', '8'},
                                {'3', '6', '4', 'B', '7', '0', '8', 'F', '7', '9', '9', '7', '1', 'B', '8', '1'},
                                {'1', '7', 'C', '6', '3', '9', '8', 'E', 'B', '9', '1', 'F', '8', 'B', '1', '2'},
                                {'0', 'F', '3', 'C', '9', '9', '9', 'C', '1', '1', '9', 'F', 'C', '0', '3', '5'},
                                {'8', '6', 'B', '9', 'C', '9', '9', '9', '0', '9', '9', 'F', '6', '0', '2', 'B'},
                                {'4', 'E', 'A', '3', 'E', '8', '9', '3', '8', '8', '9', 'F', '3', '0', 'A', '6'},
                                {'A', 'A', '6', '6', 'F', '8', '0', '7', 'C', '8', '8', 'F', '1', '9', '4', 'C'},
                                {'D', '2', '6', 'C', 'F', '1', '0', 'E', 'E', '8', '8', 'E', '8', '1', 'D', '8'},
                                {'6', '3', 'E', '8', '7', '1', '9', 'C', 'F', '8', '8', 'C', '3', '8', 'D', '1'},
                                {'9', 'F', '2', '1', '9', '9', '9', '3', 'F', '9', '9', '6', '9', 'C', '0', '6'},
                                {'0', '0', '0', '0', '0', '6', '6', '0', '0', '6', '6', '0', '0', '0', '0', '0'},
                                {'0', '0', '0', '0', '0', '6', '6', '0', '0', '6', '6', '0', '0', '0', '0', '0'}}};
 
// An array of arrays of patterns referenced to demonstrate the mapping.
// Array 1 demonstrates the mapping of the cube to the Hilbert's Curve algorithm.
// Array 2 demonstrates the mapping of the physical cube
char mapping[2][64] = {{63, 59, 43, 47, 46, 42, 58, 62, 61, 45, 44, 60, 56, 40, 41, 57, 53, 37, 36, 52, 48, 32, 33, 49, 50, 51, 55, 54, 38, 39, 35, 34, 18, 19, 23, 22, 6, 7, 3, 2, 1, 17, 16, 0, 4, 20, 21, 5, 9, 25, 24, 8, 12, 28, 29, 13, 14, 10, 26, 30, 31, 27, 11, 15},
                       {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63}};
 
 
// Initial setup of the serial port, pins, and optional startup sequence
void setup() {
  Serial.begin(9600);
  Serial.println("Setup Complete");
  pinMode(latchPin, OUTPUT);
  pinMode(clockPin, OUTPUT);
  pinMode(dataPin, OUTPUT);
  pinMode(controlSwitch1, OUTPUT);
  pinMode(controlSwitch2, OUTPUT);
  pinMode(controlSwitch3, OUTPUT);
  pinMode(controlSwitch4, OUTPUT);  
  resetHexArray();
  startUp(0);
  // startUp(1);
  // startUp(2);
  // startUp(3);
  // testMapping(0);
  // testMapping(1);
}
 
// Display the mapping of the cube. 
//
// Given a 0 (Hilbert's Curve) or 1 (Hardware), the function will iterate
// through a list of values and light up the respective LEDs according 
// to the mapping
void testMapping(int mapValue) {
  resetHexArray();
  hexToBin(hexArray, frame);
  for (int i = 0; i < 64; i++) {
    while (frameCount < singleFrameDelay) {
      frame[mapping[mapValue][i]] = 1;
      frameIt(frame);
      frameCount += singleFloorDelay;
    }
    frameCount = 0;
  }
}
 
 
// Display a specified startup sequence 
//
// Given a pattern value ranging from 0 to 3, the function will iterate
// through a list an array of frames to display 
void startUp(int setVal) {
  int totalFrameinSet = sizeof(patterns[setVal]) / sizeof(patterns[setVal][0]);
  for(int i = 0; i < totalFrameinSet;i++){
    for (int j = 0; j < 16; j++) {
      hexArray[j] = patterns[setVal][i][j];
    }
    hexToBin(hexArray, frame);
 
    while (frameCount < singleFrameDelay) {
      for (int i = floorCount * (totalLED / totalFloor); i < ((floorCount + 1)*totalLED / totalFloor); i++) {
        digitalWrite(dataPin, frame[i]);
        pulseLatch();
      }
      pulseCLK();
      switch (floorCount) {
        case 0:
          digitalWrite(controlSwitch1, HIGH);
          break;
        case 1:
          digitalWrite(controlSwitch2, HIGH);
          break;
        case 2:
          digitalWrite(controlSwitch3, HIGH);
          break;
        case 3:
          digitalWrite(controlSwitch4, HIGH);
          break;
        default:
          turnOffLayers();
          break;
      }
  
      floorCount = (floorCount == totalFloor - 1) ? 0 : floorCount + 1;
      delay(singleFloorDelay);
      frameCount += singleFloorDelay;
    }
    frameCount = 0;
  }
}
 
// Output to the LEDs given a frame input
//
// Take the first 16 bits, output to the shift registers, release to the LEDs 
// Then repeat for the second, third, and fourth 16 bit parts. 
void frameIt(int frame[]){
  //Loads 16 bits for the first layer, second, third, or fourth layer
  for (int i = floorCount * (totalLED / totalFloor); i < ((floorCount + 1)*totalLED / totalFloor); i++) {
    digitalWrite(dataPin, frame[i]);
    pulseLatch();
  }
  // Release into LEDs
  pulseCLK();
  switch (floorCount) {
    case 0:
      digitalWrite(controlSwitch1, HIGH);
      break;
    case 1:
      digitalWrite(controlSwitch2, HIGH);
      break;
    case 2:
      digitalWrite(controlSwitch3, HIGH);
      break;
    case 3:
      digitalWrite(controlSwitch4, HIGH);
      break;
    default:
      turnOffLayers();
      break;
  }
      
  //Increment to upper floor, if reached reset to bottom
  floorCount = (floorCount == totalFloor - 1) ? 0 : floorCount + 1;
 
  //Single Floor Delay - Delay for the minimum amount of time an led can stay on
  delay(singleFloorDelay);
  turnOffLayers();
}
 
// Convert a given array of hexadecimal char to array of binary inputs
//
// Iterate through the hex array and convert the respective input
// into its binary counterpart 
int hexToBin(char hexArray[], int *binArray) {
  int i = 0;
  while (hexArray[i]) {
    switch (hexArray[i]) {
      case '0':
        binArray[(i * 4) + 0] = 0;
        binArray[(i * 4) + 1] = 0;
        binArray[(i * 4) + 2] = 0;
        binArray[(i * 4) + 3] = 0;
        break;
      case '1':
        binArray[(i * 4) + 0] = 0;
        binArray[(i * 4) + 1] = 0;
        binArray[(i * 4) + 2] = 0;
        binArray[(i * 4) + 3] = 1;
        break;
      case '2':
        binArray[(i * 4) + 0] = 0;
        binArray[(i * 4) + 1] = 0;
        binArray[(i * 4) + 2] = 1;
        binArray[(i * 4) + 3] = 0;
        break;
      case '3':
        binArray[(i * 4) + 0] = 0;
        binArray[(i * 4) + 1] = 0;
        binArray[(i * 4) + 2] = 1;
        binArray[(i * 4) + 3] = 1;
        break;
      case '4':
        binArray[(i * 4) + 0] = 0;
        binArray[(i * 4) + 1] = 1;
        binArray[(i * 4) + 2] = 0;
        binArray[(i * 4) + 3] = 0;
        break;
      case '5':
        binArray[(i * 4) + 0] = 0;
        binArray[(i * 4) + 1] = 1;
        binArray[(i * 4) + 2] = 0;
        binArray[(i * 4) + 3] = 1;
        break;
      case '6':
        binArray[(i * 4) + 0] = 0;
        binArray[(i * 4) + 1] = 1;
        binArray[(i * 4) + 2] = 1;
        binArray[(i * 4) + 3] = 0;
        break;
      case '7':
        binArray[(i * 4) + 0] = 0;
        binArray[(i * 4) + 1] = 1;
        binArray[(i * 4) + 2] = 1;
        binArray[(i * 4) + 3] = 1;
        break;
      case '8':
        binArray[(i * 4) + 0] = 1;
        binArray[(i * 4) + 1] = 0;
        binArray[(i * 4) + 2] = 0;
        binArray[(i * 4) + 3] = 0;
        break;
      case '9':
        binArray[(i * 4) + 0] = 1;
        binArray[(i * 4) + 1] = 0;
        binArray[(i * 4) + 2] = 0;
        binArray[(i * 4) + 3] = 1;
        break;
      case 'A':
      case 'a':
        binArray[(i * 4) + 0] = 1;
        binArray[(i * 4) + 1] = 0;
        binArray[(i * 4) + 2] = 1;
        binArray[(i * 4) + 3] = 0;
        break;
      case 'B':
      case 'b':
        binArray[(i * 4) + 0] = 1;
        binArray[(i * 4) + 1] = 0;
        binArray[(i * 4) + 2] = 1;
        binArray[(i * 4) + 3] = 1;
        break;
      case 'C':
      case 'c':
        binArray[(i * 4) + 0] = 1;
        binArray[(i * 4) + 1] = 1;
        binArray[(i * 4) + 2] = 0;
        binArray[(i * 4) + 3] = 0;
        break;
      case 'D':
      case 'd':
        binArray[(i * 4) + 0] = 1;
        binArray[(i * 4) + 1] = 1;
        binArray[(i * 4) + 2] = 0;
        binArray[(i * 4) + 3] = 1;
        break;
      case 'E':
      case 'e':
        binArray[(i * 4) + 0] = 1;
        binArray[(i * 4) + 1] = 1;
        binArray[(i * 4) + 2] = 1;
        binArray[(i * 4) + 3] = 0;
        break;
      case 'F':
      case 'f':
        binArray[(i * 4) + 0] = 1;
        binArray[(i * 4) + 1] = 1;
        binArray[(i * 4) + 2] = 1;
        binArray[(i * 4) + 3] = 1;
        break;
      default:
        break;
    }
    i++;
  }
}
 
// Reset a the hexadecimal array
//
// Iterate through the array and set back to the default off 
// value, '0'
void resetHexArray() {
  for (int i = 0; i < 16; i++) {
    hexArray[i] = '0';
  }
}
 
// Load in a single serial data bit
//
// Output a high signal to have the latch take in the serial data bit.
// Then turn off before receiving the next data bit
void pulseLatch() {
  digitalWrite(latchPin, HIGH);
  digitalWrite(latchPin, LOW);
}
 
// Release all the loaded serial data
//
// Output a high signal to have the entire shift register release all
// the data bits into a parallel out output. Then turn off before receiving
// the next batch of the serial stream
void pulseCLK() {
  digitalWrite(clockPin, HIGH);
  digitalWrite(clockPin, LOW);
}
 
// Turn off all the floors respective LEDs
//
// Output a low signal to the BJT to turn off the switch mechanism of the 
// transistor, cutting off the grounding of all LEDs in each floor
void turnOffLayers() {
  digitalWrite(controlSwitch1, LOW);
  digitalWrite(controlSwitch2, LOW);
  digitalWrite(controlSwitch3, LOW);
  digitalWrite(controlSwitch4, LOW);
}
 
// Take in 16 hexadecimal characters through the serial port and 
// output to the respective LEDs
//
// Checks the serial port for any available data. Once reached, the
// the hexadecimals are saved into a char array. The hexadecimal array
// would then be converted to a binary array and send to the LEDs
void loop() {
  if (Serial.available() >= totalLED / 4) {
    for (int i = 0; i < 16; i++) {
      hexArray[i] = Serial.read();
    }
  }
 
  //Convert entire array to a 64 bit frame
  hexToBin(hexArray, frame); 
  frameIt(frame);
}
