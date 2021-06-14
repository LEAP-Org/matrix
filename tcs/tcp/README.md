# Wireless Access Point Interface

## Functional Requirements
1. Host a wireless point
2. Shutdown access point
3. Accept new incoming connection requests
   1. Read data from socket (perform any required decoding)
   2. Dispatch data to system using events
4. POST method for sending data through socket
   1. Process an inbound event with data packet
   2. Send data through socket

## Sequencing
1. `ApHandler` hosts access point
2. Iris connects to that access point and makes connection request -> sending APR key
   1. APR Key is a previous frame hashed using `md5`
3. `ApHandler` will accept connection by starting the `SocketHandler` listener loop
4. `SocketHandler` will receive new socket connection with APR key and will forward it to `ApHandler`
5. `ApHandler` will dispatch an event to the system with APR key payload
6. If validated `ApHandler` instructs the `SocketHandler` to send the frame count to the client.
7. `ApHandler` instructs `SocketHandler` to listen for client response
   1. stores `md5` checksum of payload
8. `SocketHandler` receives ack
   1. string parse payload for checksum and validate ack
9. `ApHandler` dispatch event to display a new transmission frame.
10. `ApHandler` instructs socket handler to send crc32
