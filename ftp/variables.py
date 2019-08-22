from enum import Enum

#shared variables for network
HOST_IP="127.0.0.1"
PORT=8080

#message types
class TransmissionType(Enum):
	ERROR=-1
	OPEN_TRANSMISSION=0
	ECHO_TRANSMISSION=1
	DATA_TRANSMISSION=2

#error codes
class ErrorCode(Enum):
	INVALID_OPEN_TRANSMISSION=0
	INVALID_KEY=1
	INVALID_SESS_ID=2
	INTEGRITY_COMPROMISED=3