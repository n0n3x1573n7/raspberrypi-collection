import asyncio

from Crypto.Random import get_random_bytes

from pickle import loads, dumps
from struct import pack, unpack

from base64 import b64encode
b64=lambda x:b64encode(x).decode('utf-8')

from structures import Data, EncryptTransmission
from variables import *

class NoTypeDeclared(Exception): pass

async def close(writer):
	writer.close()
	await writer.wait_closed()

async def send(enckey, writer, *, encrypted=True, type=None, **kwargs):
	if type==None:
		raise NoTypeDeclared("Messages must have its type declared")
	
	if encrypted:
		enckey.set_data(type=type, **kwargs)
		enckey.encrypt()
		enc_data=enckey.transmission_data()
		data=Data(pubkey=enckey.get_public_key(), encrypted=True, enc_data=enc_data)
	else:
		data=Data(pubkey=enckey.get_public_key(), encrypted=False, type=type, **kwargs)

	msg=dumps(data)
	msg=pack('!Q', len(msg))+msg

	writer.write(msg)

async def read_length(reader, length):
	data=b''
	while len(data)<length:
		partial=await reader.read(length-len(data))
		data+=partial
	return data

async def read(deckey, reader):
	tmp=await read_length(reader, 8)
	msglen=unpack('!Q',tmp)[0]

	if not msglen:
		return

	msg=await read_length(reader, msglen)
	data=loads(msg)

	if data.encrypted:
		deckey.assign_transmission(data.enc_data)
		deckey.decrypt()
		dec_data=deckey.get_data()
	else:
		dec_data=data

	deckey.set_encryption_key(data.pubkey)

	return dec_data