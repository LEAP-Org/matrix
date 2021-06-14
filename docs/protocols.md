# Networking Protocols

Modified: 2021-06

### Acknowledgments
```python
import hashlib
checksum=hashlib(previous msg, md5)
```
crc32digest~ACK->utf-8
        ^ splitting character

server checksum("sent1") -> "sent1" -> client
client -> 342321ed1~ACK -> server checks 

### Termination
\0x00 'Null byte'

### Checksum
crc32digest~UP
           ^ splitting character

```python
import binascii
binascii.crc32(transmitter.payload)
```

### APR Key
Tesseract
'0x87' -> 342e3e2568
'0x47' -> ae3213f313
...

IRIS:
'0x47' -> ae3213f313

### LFTP - TCP
### Case 1: Base Case
1. server cache checksum(543f~UP) -> 43f2 
2. sends payload to client -> 543f~UP
3. client caches payload checksum(543f~UP) -> 43f2
4. client capture and process
5. client verifies checksum 543f
6. checksum validation passes
7. client sends crc32(543f~UP)~ACK -> 43f2~ACK
8. server receives 43f2~ACK and validates checksum
9. if correct proceed to next frame transaction

### Case 2: Bad Socket payload
1. server cache checksum(543f~UP) -> 43f2 
2. sends payload to client -> 543f~UP
3. client caches payload checksum(544f~UP) -> 5322
4. client capture and process
5. client verifies checksum 5322
6. checksum validation fails
7. client sends crc32(544f~UP)~NACK -> 5322~NACK
8. server receives 5322~NACK and validates checksum
9. server checksum validation fails (the client received the wrong checksum)
11. server resends 543f~UP

### Case 3: Checksum Failure
1. server cache checksum(543f~UP) -> 43f2 
2. sends payload to client -> 543f~UP
3. client caches payload checksum(543f~UP) -> 43f2
4. client capture and process
5. client verifies checksum 5322
6. checksum validation fails
7. client sends crc32(543f~UP)~ACK -> 43f2~NACK
8. server receives 43f2~NACK and validates checksum
9. server checksum validation passes (the client capture was faulty) 
10. server updates retry counter
11. if over limit then terminate connection with null byte (0x00) 
12. if within retry limit server resends 543f~UP