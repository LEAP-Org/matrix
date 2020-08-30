# Tesseract Firmware

## Block Diagram
![image](/firmware/block/tcv1.png)

## Modules
1. System Clock: Crystal or 555. To start however we should set up a 555 in astable, bistable and monostable to allow us to have a regular clock period while having the ability to freeze the clock and step through each iteration sequentially.
2. Power Driver: Transformer and full bridge rectifier for converting outlet VAC to VDC. In addition standard PWM fans require 12VDC so we need a 12V and 5V voltage regulators for our motherboard power and RPi Power
3. Serial-To-Parallel converter using an XXHC595 (not sure what model is best yet) coupled with a 4 bit counter (4017) for producing the RCLK for the latches every 8 SCLK cycles 
4. Spatial Encoder: Pretty straight forward encoding logic I want to merge DCL inside it at some point
5. Directional Control Logic: 2 bit control signal specifies the transmission direction and translates the encoded data accordingly. 
6. I want to introduce an error correction module at the end since we are pipelining our parallel lines and if the check is successful we have a chip enable for the matrix controller (some tristate buffers would work). I realize parity may not be the right solution.
7. PWM fan driver for the Pi. RPi's get hot especially if run as a server machine. We should have a proper heatsink and cooling solution for the Pi. Im not sure if I just want it controlled through PWM on the Pi. Ideally I want to Pi to automatically change the fan speed based on its internal temperature reading rather than writing code to do it. This would require some control logic.
