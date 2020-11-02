#ifndef Segment_H
#define Segment_H
#include "Arduino.h"
class Segment
{
    public:
      Segment(int pin1, int pin2, int pin4, int pin5, int pin6, int pin7, int pin9, int pin10);
      void displayHex(int numberToDisplay);

    private:
      int pins[8];
};
#endif