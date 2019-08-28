from commands.modules.structures import Data
from commands.modules.networking import send, read, close
from commands.modules.variables import TransmissionType
from commands.modules.paths import *
from commands.modules.account import Account

from os import sep
from os.path import join

async def parse_client(txt, reader, writer, enc_conn, sessid):
	await send(enc_conn, writer, type=TransmissionType.COMMAND, command='download', sess_id=sessid, path=get_server_cwd(), file=txt, **enc_conn.get_login_info())
	res=await read(enc_conn, reader)
	if res.result:
		with open(join(get_local_cwd(),txt.split(sep)[-1]), 'wb') as f:
			f.write(res.content)
	return res

async def parse_server(data, reader, writer, sessions, sessid):
	try:
		content=Account(data.username).get_file_from_path(data.passwd, data.path, data.file)
		await send(sessions[sessid], writer, type=TransmissionType.COMMAND, command='download', result=True, content=content, response="Successfully downloaded")
	except Exception as e:
		await send(sessions[sessid], writer, type=TransmissionType.ERROR, command='download', result=False, response="Download failed:{}".format(str(type(e))+': '+str(e)))