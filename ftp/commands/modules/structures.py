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
		return 'Data('+', '.join(("{}={}".format(key, repr(val)) for (key,val) in self.__dict__.items()))+')'

	def __eq__(self, other):
		return self.__dict__==other.__dict__

class RSA_Private:
	def __init__(self, *, rsa_priv=None):
		self.__rsa_priv=rsa_priv

	def generate_RSA_key(self):
		#Generate and save the RSA key.
		#Server will call this function periodically to update the RSA key.
		#Client will call this function
		self.__rsa_priv=RSA.generate(EncryptTransmission.RSA_BITS)
		
	def get_private_key(self):
		return self.__rsa_priv

	def get_public_key(self):
		return self.__rsa_priv.publickey().export_key()

class EncryptTransmission:
	PRESET=b'\xff'*16
	RSA_BITS=2048
	ENCRYPT=True
	DECRYPT=False
	def __init__(self, *, enc_sesskey=None, enc_data=None,
		         sesskey=PRESET, old_sesskey=None, data=None,
		         rsa_dec=None, rsa_dec_file='rsa.key',rsa_dec_key=None,
		         rsa_enc=None):
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
		if rsa_dec==None:
			self.__rsa_dec=RSA_Private()
		else:
			self.__rsa_dec=rsa_dec
		self.__rsa_pub=None

		#Other's key
		self.__rsa_enc=None

		self.last_action=None

		self.__userid=None
		self.__passwd=None

	def is_logged_in(self):
		return self.__userid!=None

	def get_login_info(self):
		return {'username':self.__userid, 'passwd':self.__passwd}

	def set_login_info(self, userid, passwd):
		self.__userid=userid
		self.__passwd=passwd
		self.update_data(userid=userid, passwd=passwd)

	def delete_login_info(self):
		self.__userid=None
		self.__passwd=None
		d=self.get_data()
		del d.__dict__['userid']
		del d.__dict__['passwd']
		self.set_data(**d.__dict__)

	def copy(self):
		return EncryptTransmission(
			   enc_sesskey=self.__enc_sesskey,
			   enc_data=self.__enc_data,
			   sesskey=self.__sesskey,
			   old_sesskey=self.__old_sesskey,
			   data=self.__data,
			   rsa_enc=self.__rsa_enc,
			   rsa_dec=self.__rsa_dec,
			   )

	def generate_RSA_key(self):
		self.__rsa_dec.generate_RSA_key()
		self.__rsa_pub=self.__rsa_dec.get_public_key()

	def get_public_key(self):
		if self.__rsa_pub==None:
			self.__rsa_pub=self.__rsa_dec.get_public_key()
		return self.__rsa_pub

	def get_private_key(self):
		return self.__rsa_dec.get_private_key()
		
	def set_encryption_key(self, key):
		#save the public key of the other end after gaining their key.
		self.__rsa_enc=RSA.import_key(key)

	def get_encryption_key(self):
		return self.__rsa_enc.export_key()

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
			assert self.__data is not None
		except:
			raise DataNotFound("Data has not been found")

		if self.last_action!=EncryptTransmission.ENCRYPT:
			self.update_sesskey()

		#session key encryption
		key=RSA.import_key(self.get_encryption_key())
		rsa=PKCS1_OAEP.new(key)
		self.__enc_sesskey=rsa.encrypt(self.__old_sesskey+self.__sesskey)

		#data encryption
		cipher=AES.new(self.__sesskey, AES.MODE_EAX)
		ciphertext, tag=cipher.encrypt_and_digest(self.__data)
		self.__enc_data=Data(nonce=cipher.nonce, ciphertext=ciphertext, tag=tag)
		self.last_action=EncryptTransmission.ENCRYPT

	def decrypt(self):
		#error handling
		try:
			self.__enc_data is not None or self.__enc_sesskey is not None
		except:
			raise DataNotFound("Data has not been found")

		#session key decryption
		concatkey=PKCS1_OAEP.new(self.get_private_key()).decrypt(self.__enc_sesskey)
		try:
			if self.last_action==None:
				self.__old_sesskey==None
			elif self.last_action==EncryptTransmission.ENCRYPT:
				assert self.__sesskey==concatkey[:16] or self.__old_sesskey==None
			else:
				assert self.__old_sesskey==concatkey[:16]
		except:
			raise IntegrityCompromised("session key does not match")

		if self.last_action!=EncryptTransmission.DECRYPT:
			self.update_sesskey()
		self.__sesskey=concatkey[16:]

		#data decryption
		cipher=AES.new(self.__sesskey, AES.MODE_EAX, nonce=self.__enc_data.nonce)
		self.__data=cipher.decrypt_and_verify(self.__enc_data.ciphertext, self.__enc_data.tag)
		self.last_action=EncryptTransmission.DECRYPT

	def transmission_data(self):
		#get the pickled data object that will be transmitted.
		return dumps(Data(pubkey=self.get_public_key(), enc_sesskey=self.__enc_sesskey, enc_data=self.__enc_data))

	def assign_transmission(self, pickled_data):
		data=loads(pickled_data)
		self.set_encryption_key(data.pubkey)
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
		print("key exchange complete")
		
		for i in range(iteration):
			client.set_data(what='the',hell=15,going=b'\x00\n')
			client.encrypt()
			client.encrypt()

			result=client.transmission_data()

			server.assign_transmission(result)
			server.decrypt()
			server.decrypt()

			assert (client.get_data())==(server.get_data())

			server.set_data(some='thing',bad=15,going=b'\x00n')
			server.encrypt()
			server.encrypt()

			result=server.transmission_data()

			client.assign_transmission(result)
			client.decrypt()
			client.decrypt()

			assert (client.get_data())==(server.get_data())

	main()