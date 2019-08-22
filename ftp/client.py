import asyncio

from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP

from pickle import loads, dumps
from struct import pack, unpack

from base64 import b64encode
b64=lambda x:b64encode(x).decode('utf-8')

from structures import Data, EncryptTransmission
from variables import *
from networking import close, read, send

enc_conn=EncryptTransmission()

async def key_exchange(reader, writer):
    global sessid
    
    #network data exchange
    await send(enc_conn, writer, encrypted=False, type=TransmissionType.OPEN_TRANSMISSION)
    data=await read(enc_conn, reader)
    
    #sessid decryption
    sessid=data.sess_id

    print('server:', enc_conn.get_encryption_key())
    print('client:', enc_conn.get_public_key())
    return sessid

async def echo(txt, reader, writer):
    global sessid

    await send(enc_conn, writer, type=TransmissionType.ECHO_TRANSMISSION, content=txt)
    data=await read(enc_conn, reader)

    return data

async def main():
    reader, writer=await asyncio.open_connection(HOST_IP, PORT)
    print('connection opened')

    sessid=await key_exchange(reader, writer)
    print('key exchange completed')

    while True:
        x=await echo(input(">> "), reader, writer)
        print(x)


async def parse_command(cmd, reader, writer):
    pass

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())