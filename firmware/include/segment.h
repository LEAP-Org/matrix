#ifndef Segment_H
#define Segment_H
#include <Arduino.h>
class Segment
{
    public:
      Segment(int pin1, int pin2, int pin3, int pin4, int pin5, int pin6, int pin7, boolean msb);
      void displayHex(int hex);

    private:
      int pins[7];
};
#endif