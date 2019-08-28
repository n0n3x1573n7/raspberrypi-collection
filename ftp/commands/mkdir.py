from commands.modules.structures import Data
from commands.modules.networking import send, read, close
from commands.modules.variables import TransmissionType
from commands.modules.paths import *
from commands.modules.account import Account

from os.path import join

async def parse_client(txt, reader, writer, enc_conn, sessid):
	if not enc_conn.is_logged_in():
		return Data(type=TransmissionType.COMMAND, response="Not logged in")
	await send(enc_conn, writer, type=TransmissionType.COMMAND, command='mkdir', sess_id=sessid, path=get_server_cwd_as_list(), name=txt, **enc_conn.get_login_info())
	return await read(enc_conn, reader)

async def parse_server(data, reader, writer, sessions, sessid):
	path=data.path
	dirname=data.name
	Account(data.username).create_directory(data.passwd, join(*path), dirname)
	await send(sessions[sessid], writer, type=TransmissionType.COMMAND, command='mkdir', response='Directory {} successfully created'.format(dirname))