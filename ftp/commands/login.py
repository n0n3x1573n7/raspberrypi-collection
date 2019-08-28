from commands.modules.structures import Data
from commands.modules.networking import send, read, close
from commands.modules.variables import TransmissionType
from commands.modules.account import Account
from commands.modules.paths import get_path_as_list, set_local_cwd_from_list, set_server_cwd_from_list

from getpass import getpass
from pickle import dumps

async def parse_client(txt, reader, writer, enc_conn, sessid):
	if enc_conn.is_logged_in():
		return Data(type=TransmissionType.COMMAND, response="Already logged in as {}".format(enc_conn.get_login_info()['username']))
	userid=input("Enter ID:").lower()
	passwd=getpass("Enter PW:").encode()
	await send(enc_conn, writer, type=TransmissionType.COMMAND, command='login', sess_id=sessid, userid=userid, passwd=passwd)
	result=await read(enc_conn, reader)

	if result.success:
		enc_conn.set_login_info(userid, passwd)
		set_local_cwd_from_list(get_path_as_list())
		set_server_cwd_from_list([])

	return result

async def parse_server(data, reader, writer, sessions, sessid):
	userid=data.userid
	passwd=data.passwd
	acc=Account(userid)
	try:
		acc.verify_with_hash(passwd)
	except:
		await send(sessions[sessid], writer, type=TransmissionType.COMMAND, command='login', success=False, response="Login failed".format(userid))
	else:
		await send(sessions[sessid], writer, type=TransmissionType.COMMAND, command='login', success=True, response="Account {} logged in".format(userid))