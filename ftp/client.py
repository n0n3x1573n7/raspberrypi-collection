import asyncio

from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP

import ssl

from pickle import loads, dumps
from struct import pack, unpack

from base64 import b64encode
b64=lambda x:b64encode(x).decode('utf-8')

from os.path import exists, join

import atexit

from structures import Data, EncryptTransmission
from networking import close, read, send
from variables import *
from client_secret.client_variables import *

enc_conn=EncryptTransmission()
enc_conn.generate_RSA_key()

sessid=None

async def key_exchange(reader, writer):
    global sessid
    
    #network data exchange
    await send(enc_conn, writer, encrypted=False, type=TransmissionType.OPEN_TRANSMISSION)
    data=await read(enc_conn, reader)
    
    #sessid decryption
    sessid=data.sess_id
    return sessid

async def echo(txt, reader, writer):
    global sessid

    await send(enc_conn, writer, type=TransmissionType.ECHO_TRANSMISSION, sess_id=sessid, content=txt)
    data=await read(enc_conn, reader)

    return data

async def bye(reader, writer):
    await send(enc_conn, writer, type=TransmissionType.END_TRANSMISSION, sess_id=sessid)
    await close(writer)

async def main():
    ssl_context=ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ssl_context.check_hostname=False
    ssl_context.load_verify_locations(join(CLI_SECRET, CERT_FILE))

    conn=False
    while not conn:
        try:
            reader, writer=await asyncio.open_connection(HOST_IP, PORT, ssl=ssl_context)
            print('connection opened')
            conn=True
        except ConnectionRefusedError:
            await asyncio.sleep(0.5)

    atexit.register(lambda: asyncio.get_event_loop().run_until_complete(bye(reader, writer)))

    sessid=await key_exchange(reader, writer)
    print('key exchange completed')

    while True:
        txt=input(">> ")
        if txt=='bye':
            await bye(reader, writer) 
            break
        x=await echo(txt, reader, writer)
        print(x)

async def parse_command(cmd, reader, writer):
    pass

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())