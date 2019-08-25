from commands.modules.structures import Data
from commands.modules.networking import send, read
from commands.modules.variables import TransmissionType

async def local(txt, reader, writer, enc_conn, sessid):
	return Data(type=TransmissionType.COMMAND, response=txt)

async def sent_conn(txt, reader, writer, enc_conn, sessid):
	await send(enc_conn, writer, type=TransmissionType.COMMAND, command='echo', sess_id=sessid, content=txt)
	data=await read(enc_conn, reader)
	return data

async def parse_client(txt, reader, writer, enc_conn, sessid):
	location=txt.split(' ')[0]
	text=' '.join(txt.split(' ')[1:])
	if location in ['local', 'l']:
		return await local(text, reader, writer, enc_conn, sessid)
	else:
		return await sent_conn(txt, reader, writer, enc_conn, sessid)


async def parse_server(data, reader, writer, sessions, sessid):
	await send(sessions[sessid], writer, type=TransmissionType.COMMAND, command='echo', response=data.content)