from commands.modules.structures import Data
from commands.modules.networking import send, read, close
from commands.modules.variables import TransmissionType
from commands.modules.paths import *
from commands.modules.account import Account

from os import sep
from os.path import join

async def parse_client(txt, reader, writer, enc_conn, sessid):
	with open(txt, 'rb') as f:
		content=f.read()
	await send(enc_conn, writer, type=TransmissionType.COMMAND, command='upload', sess_id=sessid, path=get_server_cwd(), file=txt.split(sep)[-1], content=content, **enc_conn.get_login_info())
	return await read(enc_conn, reader)

async def parse_server(data, reader, writer, sessions, sessid):
	try:
		Account(data.username).save_file_to_path(data.passwd, data.path, data.file, data.content)
		await send(sessions[sessid], writer, type=TransmissionType.COMMAND, command='upload', result=True, response="Successfully uploaded")
	except Exception as e:
		await send(sessions[sessid], writer, type=TransmissionType.ERROR, command='upload', result=False, response="Upload failed: {}".format(str(e)))
