// -*- lsst-c++ -*-
/**
 * LEAP Systems
 * See COPYRIGHT file at the top of the source tree.
 * Copyright © 2020 LEAP. All Rights Reserved.
 * 
 * @file segment.h
 *
 * @brief Modified seven segment driver solution for KEM 5621 BSR
 *
 * @ingroup Segment
 *
 * @author Christian Sargusingh
 * Contact: christian@leapsystems.online
 */

#ifndef LIB_SEGMENT_SRC_SEGMENT_H_
#define LIB_SEGMENT_SRC_SEGMENT_H_
#include <Arduino.h>
class Segment {
 public:
  Segment(int pin1, int pin2, int pin3, int pin4, int pin5, int pin6, \
    int pin7, boolean msb);
  void displayHex(int hex);

 private:
  int pins[7];
};
#endif  // LIB_SEGMENT_SRC_SEGMENT_H_
