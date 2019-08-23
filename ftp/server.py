from os.path import exists, join

import asyncio

from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP

from OpenSSL import crypto, SSL
import ssl
from socket import gethostname

from pickle import loads, dumps
from struct import pack, unpack

from base64 import b64encode
b64=lambda x:b64encode(x).decode('utf-8')

from os.path import exists, join

from structures import Data, RSA_Private, EncryptTransmission
from networking import close, read, send
from variables import *
from server_secret.server_variables import *

sessions={}

rsa_prikey=RSA_Private()
rsa_prikey.generate_RSA_key()

def generate_sessid(min_sessid_len=1):
    sessid=get_random_bytes(min_sessid_len)
    retry=0
    if sessid in sessions:
        retry+=1
        if retry>2**(min_sessid_len):
            min_sessid_len+=1
        sessid=get_random_bytes(min_sessid_len)
    return sessid

async def handle_connection(reader, writer):
    #setup
    sess_id=generate_sessid()
    sessions[sess_id]=EncryptTransmission(rsa_dec=rsa_prikey)
    
    while True:
        data=await read(sessions[sess_id], reader)
        if 'sess_id' not in data.__dict__ and data.type!=TransmissionType.OPEN_TRANSMISSION:
            await error(ErrorCode.INVALID_OPEN_TRANSMISSION, sess_id, reader, writer)
        elif 'sess_id' in data.__dict__ and sess_id!=data.sess_id:
            await error(ErrorCode.INVALID_SESS_ID, sess_id, reader, writer)
        if not (await handle_packet(data, sess_id, reader, writer)):
            print("Connection terminated with {}".format(sess_id))
            return

async def handle_packet(data, sess_id, reader, writer):
    if data.type==TransmissionType.OPEN_TRANSMISSION:
        await key_exchange(data, sess_id, reader, writer)
        return True
    if data.type==TransmissionType.ECHO_TRANSMISSION:
        await echo(data, sess_id, reader, writer)
        return True
    if data.type==TransmissionType.END_TRANSMISSION:
        await bye(data, sess_id, reader, writer)
        return False

async def key_exchange(data, sess_id, reader, writer):
    #send session id
    await send(sessions[sess_id], writer, encrypted=False, type=TransmissionType.OPEN_TRANSMISSION, sess_id=sess_id)

async def echo(data, sess_id, reader, writer):
    await send(sessions[sess_id], writer, type=TransmissionType.ECHO_TRANSMISSION, content=data.content)

async def bye(data, sess_id, reader, writer):
    del sessions[sess_id]
    await close(writer)

async def error(errcode, sess_id, reader, writer):
    await send(sessions[sess_id], writer, type=TransmissionType.ERROR, errcode=errcode)

async def main():
    global rsa_prikey
    #certificate
    ssl_context=ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.check_hostname=False
    ssl_context.load_cert_chain(join(SERV_SECRET, CERT_FILE), join(SERV_SECRET, KEY_FILE))

    print("server started")
    #start server
    server=await asyncio.start_server(handle_connection, HOST_IP, PORT, ssl=ssl_context)

    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())