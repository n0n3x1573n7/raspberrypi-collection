from os import getcwd, sep
from os.path import splitdrive, split, join

from pickle import loads, dumps

def get_path_as_list(path=None):
	if path==None:
		path=getcwd()
	return path.split(sep)

def get_local_cwd_as_list():
	with open('./client_secret/client_path','rb') as f:
		return loads(f.read())

def get_local_cwd():
	l=get_local_cwd_as_list()
	return sep.join(l)

def set_local_cwd_from_list(pathlist):
	pathlist=(sep.join(pathlist)).split(sep)
	with open('./client_secret/client_path','wb') as f:
		return f.write(dumps(pathlist))

def set_local_cwd(pathstr):
	set_local_cwd_from_list(pathstr.split(sep))

def get_server_cwd_as_list():
	with open('./client_secret/server_path','rb') as f:
		return loads(f.read())

def get_server_cwd():
	return sep.join(get_server_cwd_as_list())

def set_server_cwd_from_list(pathlist):
	pathlist=(sep.join(pathlist)).split(sep)
	with open('./client_secret/server_path','wb') as f:
		f.write(dumps(pathlist))

def parse_path_to_list(path, local=True):
	if path.startswith(sep):
		path=path[1:].split(sep)
		loc_path=[]
	else:
		path=path.split(sep)
		if local:
			loc_path=get_local_cwd_as_list()
		else:
			loc_path=get_server_cwd_as_list()
	for i in path:
		if i=='.' or '':
			pass
		elif i=='..':
			if len(loc_path):
				loc_path.pop()
		else:
			loc_path.append(i)
	if not loc_path:
		loc_path=['/']
	return loc_path
