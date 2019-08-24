from commands.modules.structures import Data
from commands.modules.networking import send, read, close
from commands.modules.variables import TransmissionType

from os import listdir, getcwd
from os.path import isfile, isdir, join

def ls(path):
	file=[]
	dirs=[]
	for f in listdir(path):
		if isfile(join(path, f)):
			file.append(f)
		elif isdir(join(path, f)):
			dirs.append(f)
	return {'file':file, 'dir':dirs}

def main(txt, reader, writer):
	if not txt:
		path=getcwd()
	else:
		path=txt
	if path.startswith('"') and path.endswith('"'):
		path=path[1:-1]
	return ls(path)