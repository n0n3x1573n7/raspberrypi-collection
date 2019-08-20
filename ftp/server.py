import asyncio

from Crypto.Random import get_random_bytes

from pickle import loads, dumps
from struct import pack, unpack

from base64 import b64encode
b64=lambda x:b64encode(x).decode('utf-8')

from structures import Data, EncryptTransmission
from networknode import NetworkNode

class Server(NetworkNode):#TODO: 
    async def start(self, host='127.0.0.1', port=8080):
        server=await asyncio.start_server(self.handle_conn, host, port)
        addr=server.sockets[0].getsockname()
        print("SERVING ON {}".format(addr))

        async with server:
            await server.serve_forever()

    async def handle_conn(self, reader, writer):
        self.reader=reader
        self.writer=writer

    async def get_public_key(self):
        return self.crypto.get_public_key()

    async def set_encryption_key(self, key):
        self.crypto.set_encryption_key(key)

async def main():
    s=Server()

    await s.start()

    while True:
        data=await s.read()
        print('received: {}'.format(data))
        if data.__dict__.get('pubkey'):
            s.set_encryption_key(data.pubkey)
            data=self.get_public_key()
        if data.message=='bye':
            await s.close()
        await s.send(data)

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())