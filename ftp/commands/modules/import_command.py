import importlib.util
from os.path import join

LOCAL='l'
SENT='s'
READ='r'

def import_with_path(module_name, mode, *, filename=None, path='./commands'):
	if filename==None:
		filename=module_name+'.py'
	spec=importlib.util.spec_from_file_location(module_name, join(path, filename))
	mod=importlib.util.module_from_spec(spec)
	spec.loader.exec_module(mod)
	try:
		return mod.func[mode]
	except:
		func={
			'l':mod.local,
			's':mod.sent,
			'r':mod.read,
		}
		return func[mode]