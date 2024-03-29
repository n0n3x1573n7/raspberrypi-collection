from commands.modules.structures import Data
from commands.modules.networking import send, read, close
from commands.modules.variables import TransmissionType

async def parse_client(txt, reader, writer, enc_conn, sessid):
	'''
	Client-side transmission. Returns response of the server in Data object.
	This includes the local version of said command.

	The return value must be in Data object which has attribute response.
	On local call, if not applicable to local, return Data(type=TransmissionType.ERROR, response="ERROR MESSAGE")

	If the return value has attribute action, it performs the designated actions.
	Currently defined actions are:
	1. return: return and exit client

	txt: string, command options without the first two words of the input(i.e. "send [command]")
	reader: use await read(enc_conn, reader) to read from stream
	sender: use await write(enc_conn, writer, type=TransmissionType.TRANSMISSION_TYPE_HERE,
	                        sess_id=sessid, command=COMMAND_NAME_HERE, **kwargs) to write to stream

	To add the variables the client itself must be fixed, for each subsequent call of import_with_path functions.
	'''
	pass

async def parse_server(data, reader, writer, sessions, sessid):
	'''
	Server-side transmission.
	The initial reception is handled directly in the server and the Data object received is put in data.
	Return value is not handled and discarded.

	data: initial Data object received
	reader, sender: same as above, but use sessions[sessid] in place of enc_conn.

	The intermediary values can be designed freely.
	The final sent value must have attribute response, of which will be shown to the client without further formatting.
	After this function is returned, no further action is performed by the server.
	'''
	pass