import importlib.util
from os.path import join

def import_with_path(module_name, *, filename=None, path='./commands'):
	if filename==None:
		filename=module_name+'.py'
	spec=importlib.util.spec_from_file_location(module_name, join(path, filename))
	mod=importlib.util.module_from_spec(spec)
	spec.loader.exec_module(mod)
	return mod

import_with_path('ls').main()
import_with_path('ls').main()