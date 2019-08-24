from enum import Enum, unique, auto

#shared variables for network
HOST_IP="127.0.0.1"
PORT=8080

class AutoName(Enum):
	def _generate_next_value_(name, start, count, last_values):
		return name

#message types
@unique
class TransmissionType(AutoName):
	ERROR=auto()
	OPEN_TRANSMISSION=auto()
	COMMAND=auto()
	END_TRANSMISSION=auto()

#error codes
@unique
class ErrorCode(AutoName):
	INVALID_OPEN_TRANSMISSION=auto()
	INVALID_KEY=auto()
	INVALID_SESS_ID=auto()
	INTEGRITY_COMPROMISED=auto()