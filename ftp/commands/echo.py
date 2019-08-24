from commands.modules.structures import Data
from commands.modules.networking import send, read
from commands.modules.variables import TransmissionType

async def local(txt, reader, writer, enc_conn, sessid):
	return Data(type=TransmissionType.COMMAND, response=txt)

async def sent_conn(txt, reader, writer, enc_conn, sessid):
	await send(enc_conn, writer, type=TransmissionType.COMMAND, command='echo', sess_id=sessid, content=txt)
	data=await read(enc_conn, reader)
	return data

async def read_conn(data, reader, writer, sessions, sessid):
	await send(sessions[sessid], writer, type=TransmissionType.COMMAND, command='echo', response=data.content)

func={
	'l':local,
	's':sent_conn,
	'r':read_conn,
}