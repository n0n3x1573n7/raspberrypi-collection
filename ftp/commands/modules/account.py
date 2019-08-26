from os.path import join, isfile
from pickle import loads, dumps

from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA3_512

try:
	from server_secret.server_variables import *
except:
	SERV_SECRET="D:/Study/PGM/python/= project_raspberry/ftp/server_secret"
	FILE_FOLDER="files/"
	PASS_FILE="passwd"

from commands.modules.filesys import Root, Directory, File

pass_file=join(SERV_SECRET, PASS_FILE)
file_path=join(SERV_SECRET, FILE_FOLDER)

ROOT=Root()

class UnverifiedAccountError(Exception): pass
class UnidentifiedUsername(Exception): pass
class ExistingUsername(Exception): pass

def create_salt():
	return get_random_bytes(32)

class Account:
	def __init__(self, username):
		with open(pass_file, 'rb') as f:
			passdict=loads(f.read())
			if username not in passdict:
				raise UnidentifiedUsername("Username {} unidentified".format(username))
			acc=passdict[username]
		self.__username=username
		self.__pwhash=acc['pwhash']
		self.__salt=acc['salt']

	@classmethod
	def is_id_usable(cls, username):
		try:
			passdict={}
			with open(pass_file,'rb') as f:
				passdict=loads(f.read())
			assert username in passdict
		except:
			return True
		else:
			return False

	@classmethod
	def create_userinfo(cls, username, passwd, update=False):
		try:
			passdict={}
			with open(pass_file,'rb') as f:
				passdict=loads(f.read())
			if not update:
				assert username in passdict
		except:			
			salt=create_salt()
			h=SHA3_512.new()
			h.update(passwd+salt)
			pwhash=h.digest()

			passdict[username]={'pwhash':pwhash, 'salt':salt}

			with open(pass_file, 'wb') as f:
				f.write(dumps(passdict))

			with open(join(file_path, username),'wb') as f:
				f.write(dumps(Directory(username, ROOT)))
		else:
			raise ExistingUsername("The username already exists")

	def verify_with_hash(self, passwd):
		#hash(hash(pw+pw_salt)+ver_salt)=hash(pw_hash+ver_salt)
		h=SHA3_512.new()
		h.update(passwd+self.__salt)
		return h.digest()==self.__pwhash

	def __get_filesys(self):
		with open(join(file_path, self.__username), 'rb') as f:
			return loads(f.read())

	def load_from_path(self, passwd, pathstr='root'):
		if not self.verify_with_hash(passwd):
			raise UnverifiedAccountError("The account needs to be verified to get the file")
		filesys=self.__get_filesys()
		return filesys.load_from_pathstr(pathstr)

	def save_file_to_path(self, passwd, path, name, content):
		if not self.verify_with_hash(passwd):
			raise UnverifiedAccountError("The account needs to be verified to get the file")
		filesys=self.__get_filesys()
		folder=load_from_pathstr(path)
		folder.create_file(name, content)

	def create_directory(self, passwd, path, dirname):
		if not self.verify_with_hash(passwd):
			raise UnverifiedAccountError("The account needs to be verified to get the file")
		filesys=self.__get_filesys()
		folder=load_from_pathstr(path)
		folder.create_subdir(name)