# TCS API

## Registration
API should be hosted on a well known port.

1. `curl -X POST 192.168.2.1:3000/v1/register -d {'apr' : 21eaf42}`
2. server opens a tcp socket on a new port ex/. `3549`
3. server response: `{port: 3549}`
4. client starts a new socket connection to the designated port and makes a request for the number of frames
5. 

This triggers a new socket connection on