from os import listdir
from os.path import isfile, isdir

def main(curpath='./'):
	print(*listdir(curpath), sep='\n')