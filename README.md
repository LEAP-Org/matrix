# Light Emitting Access Point Tesseract
[![ci](https://github.com/LEAP-Systems/tesseract/actions/workflows/ci.yml/badge.svg)](https://github.com/LEAP-Systems/tesseract/actions/workflows/ci.yml)

Modified: 2021-06

![img](/docs/img/LEAP_INS_WHITE.png)

## Navigation
1. [Brief](#Brief)
2. [Quickstart](#Quickstart)
3. [Documentation](#Documentation)

## Brief
Transmission Control Software (TCS) is responsible for hosting the LEAP public facing API and facilitate TCP and light communications with a receiving device.

## Quickstart
Start the server by specifying a serial port for light-medium communication stream and a public address for accessing the API for registration.
```bash
python3 -m tcs -s /dev/ttyUSB0 -a localhost:5000
# help screen
python3 -m tcs
```

Test a client connection requesting the tcs to echo the `$ECHO_MESSAGE`:
```bash
# cli args
./scripts/client.py $ECHO_MESSAGE $APR_KEY
# sample
./scripts/client.py Hello 06eca1b437c7904cc3ce6546c8110110
```

## Documentation
View the docs [here](/docs/README.md)