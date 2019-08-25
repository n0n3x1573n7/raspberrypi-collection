import importlib.util
from os.path import join
from commands.modules.variables import ImportMode

def import_with_path(module_name, mode, *, filename=None, path='./commands'):
	if filename==None:
		filename=module_name+'.py'
	spec=importlib.util.spec_from_file_location(module_name, join(path, filename))
	mod=importlib.util.module_from_spec(spec)
	spec.loader.exec_module(mod)
	if mode==ImportMode.CLIENT:
		return mod.parse_client
	else:
		return mod.parse_server