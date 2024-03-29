from commands.modules.structures import Data
from commands.modules.networking import send, read, close
from commands.modules.variables import TransmissionType, loc_client, loc_server
from commands.modules.paths import *
from commands.modules.account import Account, ls

from os import listdir, getcwd, sep
from os.path import exists, isfile, isdir, join

async def parse_client(txt, reader, writer, enc_conn, sessid):
	tmp=txt.split(' ')
	loc=tmp[0]
	path=' '.join(tmp[1:])
	if loc not in loc_client+loc_server:
		path=loc+' '+path if path else loc
		loc=''
	if loc in loc_client:
		loc_path=parse_path_to_list(path, local=True)
		loc_path=sep.join(loc_path)
		if not isdir(loc_path):
			return Data(type=TransmissionType.ERROR, response="Path does not exist")
		res=ls(loc_path)
		return Data(type=TransmissionType.COMMAND, response='\n'.join([*map(lambda x:'D:'+x,res['dir'])]+[*map(lambda x:'F:'+x,res['file'])]))
	else:
		if not enc_conn.is_logged_in():
			return Data(type=TransmissionType.COMMAND, response="Not logged in")
		loc_path=parse_path_to_list(path, local=False)
		await send(enc_conn, writer, type=TransmissionType.COMMAND, command='ls', sess_id=sessid, path=loc_path, **enc_conn.get_login_info())
		return await read(enc_conn, reader)

async def parse_server(data, reader, writer, sessions, sessid):
	res=Account(data.username).list_path(data.passwd, join(*data.path))
	await send(sessions[sessid], writer, type=TransmissionType.COMMAND, command='ls', response='\n'.join([*map(lambda x:'D:'+x,res['dir'])]+[*map(lambda x:'F:'+x,res['file'])]))
