from commands.modules.structures import Data
from commands.modules.networking import send, read, close
from commands.modules.variables import TransmissionType
from commands.modules.account import Account

from getpass import getpass
from os import remove

async def parse_client(txt, reader, writer, enc_conn, sessid):
	enc_conn.delete_login_info()
	return Data(type=TransmissionType.COMMAND, response="logout completed")

async def parse_server(data, reader, writer, sessions, sessid):
	pass