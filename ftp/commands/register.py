from commands.modules.structures import Data
from commands.modules.networking import send, read, close
from commands.modules.variables import TransmissionType
from commands.modules.account import Account
from commands.modules.filesys import File, Directory

from getpass import getpass

async def parse_client(txt, reader, writer, enc_conn, sessid):
	userid=input("Enter ID:")
	passwd=getpass("Enter PW:").encode()
	await send(enc_conn, writer, type=TransmissionType.COMMAND, command='register', sess_id=sessid, userid=userid, passwd=passwd)
	return await read(enc_conn, reader)

async def parse_server(data, reader, writer, sessions, sessid):
	userid=data.userid
	passwd=data.passwd
	if Account.is_id_usable(userid):
		Account.create_userinfo(userid, passwd)
		await send(sessions[sessid], writer, type=TransmissionType.COMMAND, command='register', success=True, response="Account {} created".format(userid))
	else:
		await send(sessions[sessid], writer, type=TransmissionType.COMMAND, command='register', success=False, response="Account {} already in use".format(userid))