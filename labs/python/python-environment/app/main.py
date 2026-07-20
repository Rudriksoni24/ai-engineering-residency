import sys
from pathlib import Path
import getpass
import platform
import importlib.metadata

print("version: ", sys.version_info)
print("current directory: ", Path.cwd)
print("current User: ", getpass.getuser())
print("current OS: ", platform.system())
print("number of packages: ", len(list(importlib.metadata.distributions())))
