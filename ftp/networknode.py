import asyncio

from Crypto.Random import get_random_bytes

from pickle import loads, dumps
from struct import pack, unpack

from base64 import b64encode
b64=lambda x:b64encode(x).decode('utf-8')

from structures import Data, EncryptTransmission

class InvalidDataError(Exception): pass

class NetworkNode:
    def __init__(self, host='127.0.0.1', port=8080):
        self.host=host
        self.port=port

        self.crypto=EncryptTransmission()
        self.crypto.generate_RSA_key()

        self.reader, self.writer=None, None

    async def start(self):
        raise NotImplementedError("Must be implemented in the subclasses")

    async def close(self):
        self.writer.close()
        await self.writer.wait_closed()

    async def send(self, encrypt=True, **kwargs):
        if encrypt:
            self.crypto.set_data(**kwargs)
            self.crypto.encrypt()
            msg=self.crypto.transmission_data()
        else:
            msg=dumps(Data(**kwargs))

        msg=pack('N', len(msg))+msg

        self.writer.write(msg)

    async def read_length(self, length):
        data=b''
        while len(data)<length:
            partial=await self.reader.read(length-len(data))
            if partial:
                data+=partial
            else:
                break
        return data

    async def read(self, decrypt=True):
        tmp=await self.read_length(8)
        msglen=unpack('N',tmp)[0]

        if not msglen:
            return

        msg=await(self.read_length(msglen))
        if decrypt:
            self.crypto.assign_transmission(self, msg)
            self.decrypt()
            data=self.crypto.get_data()
        else:
            data=loads(msg)

        return data

