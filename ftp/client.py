import asyncio

from Crypto.Random import get_random_bytes

from pickle import loads, dumps
from struct import pack, unpack

from base64 import b64encode
b64=lambda x:b64encode(x).decode('utf-8')

from structures import Data, EncryptTransmission
from networknode import NetworkNode

class Client(NetworkNode):
    async def start(self):
        self.reader, self.writer=await asyncio.open_connection(self.host, self.port)
    
    async def send_rsa_key(self):
        await self.send(encrypt=False, pubkey=self.crypto.get_public_key())

    async def read_rsa_key(self):
        key=await self.read(decrypt=False)
        self.crypto.set_encryption_key(key)

async def main():
    s=Client()

    await s.start()
    print('setup complete')

    await s.send_rsa_key()
    print('rsa key sent')
    await s.read_rsa_key()
    print('rsa key read')

    while True:
        data=Data(message=input('>>'))
        await s.send(data)
        if data.message=='bye':
            await s.close()
            break
        await s.read(data)
        print('received:{}')

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())