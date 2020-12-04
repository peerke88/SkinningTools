# -*- coding: utf-8 -*-
"""
package creator

this file will place everything that is relevant to the current skinningtools in a subdirectory usin the same folderstructure
currently we glob all necessary files together and place them accordingly

@Todo:
 - actually copy and paste objects to the "package" folder
 - maybe add read me file or change readme.md to adhere to the latest install options
 - zip package together, with current date as versioning system
 - update current version in the skinningtoolsui.py file
 - upload to googledrive

@eventually:
 - add unit tests 
 - update documentation (this should be added to www.perryleijten.com)
"""

import sys, os, errno, datetime, runpy, fileinput, subprocess
from shutil import copytree, copy2, rmtree, make_archive


relPath = os.path.normpath(os.path.dirname(os.path.dirname(__file__)))
curFolder = os.path.normpath(os.path.dirname(__file__))
baseFolder =os.path.normpath(os.path.join(curFolder, "package"))

def setVersionDate( ):
	now = datetime.datetime.now( )
	versionDate = "%s%02d%02d" % (now.year, now.month, now.day)
	old = ''
	
	file_path = os.path.join(curFolder, "UI/SkinningToolsUI.py")
	with fileinput.input(file_path, inplace=True) as f:
		for line in f:
			if "__VERSION__ = " in line:

				splitted = line.split( '"' )
				old = splitted[1]
				base = splitted[ 0 ]
				end = splitted[ -1 ]
				new = "5.0.%s"%versionDate
				line = '%s"%s"%s' % (base, new, end)
				line.replace(old, new)
			print(line, end = '')

	print( "Updated Version <%s> to <%s>!" % (old, new), True )
	return new
_vers = setVersionDate()

if os.path.isdir(baseFolder):
	rmtree(baseFolder)
os.mkdir(baseFolder)


toMove = []
_exclude = ["pyc", "ai", "sh", "bat", "user", "cmake", "inl", "pro", "pri", "txt", "h", "cpp", "hpp", "dll", "zip", "mel"]
_noFile = ["reloader.py", "packageCreator.py", "run_cmake.py", "smooth_brush_pri_update.py", "skinBrushes.py"]
for dirName, __, fList in os.walk(curFolder):
	for file in fList:
		if "package" in dirName or "test" in dirName.lower() or "commons" in dirName:
			continue
		if not '.' in file:
			continue
		if file.startswith('.'):
			continue
		suffix = file.split(".")[-1]
		if suffix in _exclude and not "qcachegrind" in dirName:
			continue
		if ".git" in dirName or ".vs" in dirName or "Logs" in dirName or ".idea" in dirName:
			continue
		if "docs" in dirName:
			continue
		if file in _noFile:
			continue
		toMove.append(os.path.join(dirName, file))

for f in toMove:
	dst = os.path.join(baseFolder, "SkinningTools", f.replace("\\", "/").split("%s/"%curFolder.replace("\\", "/"))[-1])
	try:
		os.makedirs(os.path.dirname(dst))
	except OSError as e:
		if e.errno != errno.EEXIST:
			raise
	copy2(f, dst)
print("succesfully copied files")

_baseINI = os.path.join(baseFolder, "__init__.py")
_melInstaller = os.path.join(curFolder, "dragDropInstall.mel")
_pyInstaller = os.path.join(curFolder, "packageInstaller.py")
copy2(_melInstaller, baseFolder )
copy2(_pyInstaller, baseFolder )
open(_baseINI, 'w').close()

subprocess.call(['7z', 'a', os.path.join(baseFolder, "SkinTools_%s.7z"%_vers), os.path.join(baseFolder, "SkinningTools")])
subprocess.call(['7z', 'a', os.path.join(baseFolder, "SkinTools_%s.7z"%_vers), _baseINI])
subprocess.call(['7z', 'a', os.path.join(baseFolder, "SkinTools_%s.7z"%_vers), _melInstaller])
subprocess.call(['7z', 'a', os.path.join(baseFolder, "SkinTools_%s.7z"%_vers), _pyInstaller])
print("succesfully build package")
