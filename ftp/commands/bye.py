from commands.modules.structures import Data
from commands.modules.networking import send, read, close
from commands.modules.variables import TransmissionType

async def parse_client(txt, reader, writer, enc_conn, sessid):
	await send(enc_conn, writer, type=TransmissionType.END_TRANSMISSION, command='bye', sess_id=sessid)
	await close(writer)
	return Data(response="", action="return")

async def parse_server(data, reader, writer, sessions, sessid):
	del sessions[sessid]
	await close(writer)
