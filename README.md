# Light Emitting Access Point Tesseract
[![ci](https://github.com/LEAP-Systems/tesseract/actions/workflows/ci.yml/badge.svg)](https://github.com/LEAP-Systems/tesseract/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/LEAP-Systems/tesseract/branch/master/graph/badge.svg?token=QZ3AXPMDPA)](https://codecov.io/gh/LEAP-Systems/tesseract)

![img](/docs/img/LEAP_INS.png)

## Navigation
1. [About](#Absract)
2. [Run](#Run)
3. [Website](#Website)
4. [Accolades](#accolades)

## About
The Light Emitting Access Point (LEAP) Project is a proof-of-concept for a one-way, encryption independent, wireless communication system. Modern network infrastructure such as fibre optic, fixed/mobile wireless, and satellite relies on encryption to keep data secure due to the nature of their transmission mediums. Encryption algorithms are becoming increasingly complex adding computational overhead to networking systems. Therefore, encryption is not a sustainable solution for long-term network security.

LEAP provides a platform for a new wave of secure transmission technologies that operate securely independent of encryption algorithms. LEAP uses a rigorous design philosophy with a custom data transfer protocol framework emphasizing data security. The LEAP transmitter uses light to transmit data to a single or multiple cameras or photo receiving devices over short-ranges within line-of-sight. It exploits two and three-dimensional matrices enabling simultaneous communication to multiple users by computing the relative position of each receiving device. This is accomplished using a specialized encoding and decoding algorithm by applying concepts in Euclidean space and infinite mathematics. Finally, added cell multiplicity results in a proportional increase in the theoretical bandwidth capabilities, distinguishing it from conventional single-cell light communication technologies.

## Run
Applications are run by the following set of commands at the root-level directory /LEAP

First time setup:
```bash
./setup.sh
```
Server initialization:
```bash
./run-tcs.sh
```
Client initialization:
```bash
./run-rcs.sh
```

## Website

Our website is moving to leapsystems.online and is currently under development. In the meantime you can visit our [Legacy Information Page](https://stevenzhou2.github.io/TheLeapProject/)

## Accolades

### Cowie Innovation Award

The Cowie Innovation Award is given on the recommendation of the Dean of the Faculty of Engineering and Design, to one student or one team of students in the final year of a Bachelor of Engineering degree for demonstrating top quality innovation in Engineering. It was established in 2006 by Alexandra Cowie in memory of her late husband, Wilbur Elliott Cowie, BASc, MASc (Toronto), PEng.

The fourth year capstone project Light Emitting Access Point (LEAP) has won the 2020 W.E. Cowie Innovation Award, valued at $27,000. You can read the news brief covered by Carleton University [here](https://carleton.ca/sce/2020/systems-capstone-project-won-the-w-e-cowie-innovation-award/).

### Promotional Video Competition
Our [promotional video](https://www.youtube.com/watch?v=aiTprGXODSQ) won first place in Systems and Computer Engineering Departments video competition. The team won $1000 and will be featured on the SCE departments' recruitment web-page.

This repository hosts the hardware schematics and PCB designs for LEAP transmission controller.