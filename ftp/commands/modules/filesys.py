class FileNotFound(Exception): pass
class FileAlreadyExists(Exception): pass

def verify_name(name):
	if '/' in name:
		raise NameError('"/" cannot be in file or directory name.')

class File:
	def __init__(self, name, content, supdir):
		verify_name(name)
		self.__name=name
		self.__content=content
		self.__supdir=sup

	def rename(self, name):
		verify_name(name)
		self.__name=name

	def get_path(self):
		return self.__supdir.get_path_str()+'/'+self.__name

	def get_path_list(self):
		return self.__supdir.get_path_list()+[self.__name]

	def get_content(self):
		return self.__content

	def delete_file(self):
		self.__supdir.delete(self.__name)

class Directory:
	def __init__(self, name, sup):
		verify_name(name)
		self.__name=name
		self.__supdir=sup
		self.__subdir={}
		self.__files={}

	def rename(self, name):
		verify_name(name)
		self.__name=name

	def get_path_str(self):
		return self.__supdir.get_path_str()+'/'+self.__name

	def get_path_list(self):
		return self.__supdir.get_path_list()+[self.__name]

	def get_subdir_names(self):
		return [*self.__subdir.keys()]

	def get_file_names(self):
		return [*self.__files.keys()]

	def get_subdir(self, name):
		if name in self.__subdir:
			return self.__subdir[name]
		raise FileNotFound("Directory {} is not found".format(name))

	def get_file(self, name):
		if name in sef.__files:
			return self.__files[name]
		raise FileNotFound("File {} is not found".format(name))

	def delete_dir(self):
		self.__supdir.delete_subdir(self.__name)

	def delete_subdir(self, name):
		if name not in self.__subdir:
			raise FileNotFound("Directory {} is not found".format(name))
		tmp=self.__subdir[name]
		del self.__subdir[name]
		del tmp

	def delete_file(self, name):
		if name not in self.__files:
			raise FileNotFound("File {} is not found".format(name))
		tmp=self.__files[name]
		del self.__files[name]
		del tmp

	def create_subdir(self, name):
		if name in self.__subdir[name]:
			raise FileAlreadyExists("Subdirectory {} already exists".format(name))
		self.__subdir[name]=Directory(name, self)

	def create_file(self, name, content):
		if name in self.__file[name]:
			raise FileAlreadyExists("File {} already exists".format(name))
		self.__files[name]=File(name, content, self)

	def load_from_pathstr(self, pathstr):
		pathlist=pathstr.split('/')
		self.load_from_pathlist(pathlist)

	def load_from_pathlist(self, pathlist):
		if pathlist==[]:
			return self
		if len(pathlist)==1 and pathlist[0] in self.__files:
			return self.get_file(pathlist[0])
		return self.get_subdir(pathlist[0]).load_from_pathlist(pathlist[1:])

class Root(Directory):
	def __init__(self):
		Directory.__init__(self,'root',None)

	def rename(self, name):
		raise NameError("Name of Root cannot be changed")

	def get_path_str(self):
		return 'root'

	def get_path_list(self):
		return ['root']

