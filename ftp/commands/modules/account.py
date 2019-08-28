from os import mkdir, remove, rmdir, mkdir, listdir, sep
from os.path import join, isfile, isdir, exists
from shutil import rmtree
from pickle import loads, dumps

from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA3_512

try:
	from server_secret.server_variables import *
except:
	SERV_SECRET="D:/Study/PGM/python/= project_raspberry/ftp/server_secret"
	FILE_FOLDER="files/"
	PASS_FILE="passwd"

pass_file=join(SERV_SECRET, PASS_FILE)
file_path=join(SERV_SECRET, FILE_FOLDER)

class UnverifiedAccountError(Exception): pass
class UnidentifiedUsername(Exception): pass
class ExistingUsername(Exception): pass

def create_salt():
	return get_random_bytes(32)

def ls(path):
	file=[]
	dirs=[]
	for f in listdir(path):
		if isfile(join(path, f)):
			file.append(f)
		elif isdir(join(path, f)):
			dirs.append(f)
	return {'file':file, 'dir':dirs}

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

			mkdir(join(file_path, username))
				
		else:
			raise ExistingUsername("The username already exists")

	def verify_with_hash(self, passwd):
		#hash(hash(pw+pw_salt)+ver_salt)=hash(pw_hash+ver_salt)
		h=SHA3_512.new()
		h.update(passwd+self.__salt)
		if h.digest()!=self.__pwhash:
			raise UnverifiedAccountError("The account needs to be verified to get the file")

	def list_path(self, passwd, path):
		self.verify_with_hash(passwd)
		if not isdir(join(file_path, self.__username, path)):
			raise NameError("Directory does not exist")
		return ls(join(file_path, self.__username, path))

	def save_file_to_path(self, passwd, path, name, content):
		self.verify_with_hash(passwd)
		if not exists(join(file_path, self.__username, path)):
			raise NameError("Path does not exist")
		if isfile(join(file_path, self.__username, path, name)):
			raise NameError("File already exists")
		with open(join(file_path, self.__username, path, name), 'wb') as f:
			f.write(content)

	def get_file_from_path(self, passwd, path, name):
		self.verify_with_hash(passwd)
		if not exists(join(file_path, self.__username, path)):
			raise NameError("Path does not exist")
		if not isfile(join(file_path, self.__username, path, name)):
			raise NameError("File does not exist")
		with open(join(file_path, self.__username, path, name), 'rb') as f:
			return f.read()

	def create_directory(self, passwd, path, dirname):
		self.verify_with_hash(passwd)
		if not exists(join(file_path, self.__username, path)):
			raise NameError("Path does not exist")
		if exists(join(file_path, self.__username, path, dirname)):
			raise NameError("Directory already exists")
		mkdir(join(file_path, self.__username, path, dirname))

	def check_directory(self, passwd, path, dirname=""):
		self.verify_with_hash(passwd)
		return isdir(join(file_path, self.__username, path, dirname))

	def remove(self, passwd, path, name):
		self.verify_with_hash(passwd)
		if not exists(join(file_path, self.__username, path)):
			raise NameError("Path does not exist")
		target=join(file_path, self.__username, path, name)
		if isfile(target):
			remove(target)
			return 'File'
		elif isdir(target):
			rmtree(target)
			return 'Directory'
		else:
			raise NameError("Invalid target")