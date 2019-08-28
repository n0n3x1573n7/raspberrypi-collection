import asyncio

from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP

import ssl

from pickle import loads, dumps
from struct import pack, unpack

from base64 import b64encode
b64=lambda x:b64encode(x).decode('utf-8')

from os import remove
from os.path import exists, join

import atexit

from commands.modules.structures import Data, EncryptTransmission
from commands.modules.networking import close, read, send
from commands.modules.import_command import import_with_path
from commands.modules.variables import *
from client_secret.client_variables import *

enc_conn=EncryptTransmission()
enc_conn.generate_RSA_key()
print('keygen completed')

sessid=None

def gencert():
    cert=b'-----BEGIN CERTIFICATE-----\nMIIB9DCCAV0CAgPoMA0GCSqGSIb3DQEBBQUAMEExJTAjBgNVBAsMHEZUUCBzZXJ2\nZXIgZm9yIHJhc3BiZXJyeXBpIDQxGDAWBgNVBAMMD0RFU0tUT1AtUDI5TTNWNDAg\nFw0xOTA4MjMxNjAzMjJaGA8yMDg3MDkxMDE5MTcyOVowQTElMCMGA1UECwwcRlRQ\nIHNlcnZlciBmb3IgcmFzcGJlcnJ5cGkgNDEYMBYGA1UEAwwPREVTS1RPUC1QMjlN\nM1Y0MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDioiLon6/9lklDYW8CSjmS\nmx4bWVs98Bk52mK9mozZMwj5v/cjYVGvWmH1RyErK9JAE+7DFNCa7VVaFV9xOiKF\npIbR+JiymiC6ScNi6Y3o/cXBbMtgEU0vnuWViEtl9IXIAu3mLW+hvdaRy4tXDaj+\nlssVqjRmqdK80sCd51FuSQIDAQABMA0GCSqGSIb3DQEBBQUAA4GBAALyo2oYEquU\ngbW716m4QaSs7dpvLcPmexsmeotAFLgOV8N+/8f64lFxg8QQUI27cByPyHd8/wGA\nHK++LFIp1W8XvEF/cJjshlzsPbI7QIUgySaKZHdaFkzWUGv9oCXWWGWCGusDuSYT\nUem25pwbc4QO2IaAe/5E8BImYf2n5MCx\n-----END CERTIFICATE-----\n'
    with open(join(CLI_SECRET, CERT_FILE), 'wb') as f:
        f.write(cert)

def delcert():
    remove(join(CLI_SECRET, CERT_FILE))

async def key_exchange(reader, writer):
    global sessid
    
    #network data exchange
    await send(enc_conn, writer, encrypted=False, type=TransmissionType.OPEN_TRANSMISSION)
    data=await read(enc_conn, reader)
    
    #sessid decryption
    sessid=data.sess_id
    return sessid

async def parse_command(cmd, reader, writer):
    tmp=cmd.split(' ')
    cmd=tmp[0]
    txt=' '.join(tmp[1:])
    try:
        return (await import_with_path(cmd, ImportMode.CLIENT)(txt, reader, writer, enc_conn, sessid))
    except Exception as e:
        print(e)
        return Data(type=TransmissionType.ERROR,response="Command {} unrecognized".format(cmd))

async def main():
    gencert()
    atexit.register(delcert)

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

    sessid=await key_exchange(reader, writer)
    print('key exchange completed')

    atexit.register(lambda: asyncio.get_event_loop().run_until_complete(import_with_path('bye', ImportMode.CLIENT)("", reader, writer, enc_conn, sessid)))

    while True:
        cmd=input(">> ")
        res=await parse_command(cmd, reader, writer)

        if 'action' in res.__dict__ and res.action=="return":
            return
        
        if res.type==TransmissionType.ERROR:
            print("ERROR:", end='')
        
        print(res.response)

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())