from commands.modules.structures import Data
from commands.modules.networking import send, read, close
from commands.modules.variables import TransmissionType

async def local(txt, reader, writer, enc_conn, sessid):
	return Data(type=TransmissionType.ERROR, response="Local cannot be closed")

async def send_conn(txt, reader, writer, enc_conn, sessid):
	await send(enc_conn, writer, type=TransmissionType.END_TRANSMISSION, command='bye', sess_id=sessid)
	await close(writer)
	return Data(response="", action="return")

async def read_conn(data, reader, writer, sessions, sessid):
	del sessions[sessid]
	await close(writer)

func={
	'l':local,
	's':send_conn,
	'r':read_conn,
}