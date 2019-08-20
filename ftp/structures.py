from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP

from base64 import b64encode
b64=lambda x:b64encode(x).decode('utf-8')

from pickle import dumps, loads

class IntegrityCompromised(Exception): pass
class KeyNotFound(Exception): pass
class DataNotFound(Exception): pass

class Data:
	def __init__(self, **kwargs):
		self.__dict__=kwargs

	def __repr__(self):
		return str(self.__dict__)

	def __eq__(self, other):
		return self.__dict__==other.__dict__

class EncryptTransmission:
	PRESET=b'\xff'*16
	RSA_BITS=2048
	def __init__(self, *, enc_sesskey=None, enc_data=None,
		         sesskey=PRESET, old_sesskey=PRESET, data=None):
		#encdypted
		self.__enc_sesskey=enc_sesskey
		self.__enc_data=enc_data

		#plaintext
		self.__old_sesskey=old_sesskey
		self.__sesskey=sesskey

		if data==None:
			data=dumps(Data())
		self.__data=data

		#Owned key
		self.__rsa_dec_pri=None
		self.__rsa_dec_pub=None

		#Other's key
		self.__rsa_enc=None

	def generate_RSA_key(self):
		#Generate and save the RSA key.
		#Server will call this function periodically to update the RSA key.
		#Client will call this function
		key=RSA.generate(EncryptTransmission.RSA_BITS)
		self.__rsa_dec_pri=key
		self.__rsa_dec_pub=key.publickey()

	def get_public_key(self):
		return dumps(Data(pubkey=self.__rsa_dec_pub.export_key()))

	def set_encryption_key(self, key):
		#save the public key of the other end after gaining their key.
		self.__rsa_enc=RSA.import_key(loads(key).pubkey)

	def set_data(self, **kwargs):
		#set the data to be transmitted
		data=Data()
		for (key, val) in kwargs.items():
			data.__dict__[key]=val
		self.__data=dumps(data)

	def update_data(self, **kwargs):
		#update the data to be transmitted
		data=loads(self.__data)
		for (key, val) in kwargs.items():
			data.__dict__[key]=val
		self.__data=dumps(data)

	def get_data(self):
		return loads(self.__data)

	def update_sesskey(self):
		self.__old_sesskey=self.__sesskey
		self.__sesskey=get_random_bytes(16)

	def encrypt(self):
		#error handling
		try:
			assert self.__rsa_enc is not None
		except:
			raise KeyNotFound("Encryption RSA key has not been found")

		try:
			assert self.__data is not None
		except:
			raise DataNotFound("Data has not been found")

		self.update_sesskey()

		#session key encryption
		self.__enc_sesskey=PKCS1_OAEP.new(self.__rsa_enc).encrypt(self.__old_sesskey+self.__sesskey)

		#data encryption
		cipher=AES.new(self.__sesskey, AES.MODE_CTR)
		ciphertext=cipher.encrypt(self.__data)
		self.__enc_data=Data(nonce=cipher.nonce, ciphertext=ciphertext)

	def decrypt(self):
		#error handling
		try:
			self.__rsa_dec_pri is not None or self.__rsa_dec_pub is not None
		except:
			raise KeyNotFound("Decryption RSA key has not been found")

		try:
			self.__enc_data is not None or self.__enc_sesskey is not None
		except:
			raise DataNotFound("Data has not been found")

		#session key decryption
		concatkey=PKCS1_OAEP.new(self.__rsa_dec_pri).decrypt(self.__enc_sesskey)
		try:
			assert self.__sesskey==concatkey[:16] or self.__sesskey==EncryptTransmission.PRESET
		except:
			raise IntegrityCompromised("session key does not match")

		self.update_sesskey()
		self.__sesskey=concatkey[16:]

		#data decryption
		cipher=AES.new(self.__sesskey, AES.MODE_CTR, nonce=self.__enc_data.nonce)
		self.__data=cipher.decrypt(self.__enc_data.ciphertext)

	def transmission_data(self):
		#get the pickled data object that will be transmitted.
		return dumps(Data(pubkey=self.__rsa_dec_pub.export_key(), enc_sesskey=self.__enc_sesskey, enc_data=self.__enc_data))

	def assign_transmission(self, pickled_data):
		data=loads(pickled_data)
		self.__enc_sesskey=data.enc_sesskey
		self.__enc_data=data.enc_data

if __name__ == '__main__':
	def main(iteration=10):
		client=EncryptTransmission()
		server=EncryptTransmission()

		server.generate_RSA_key()
		client.generate_RSA_key()
		server.set_encryption_key(client.get_public_key())
		client.set_encryption_key(server.get_public_key())
		
		for i in range(iteration):
			client.set_data(what='the',hell=15,going=b'\x00\n')
			client.encrypt()

			result=client.transmission_data()

			server.assign_transmission(result)
			server.decrypt()

			assert (client.get_data())==(server.get_data())

			server.set_data(some='thing',bad=15,going=b'\x00n')
			server.encrypt()

			result=server.transmission_data()

			client.assign_transmission(result)
			client.decrypt()

			assert (client.get_data())==(server.get_data())

	main()