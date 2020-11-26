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

import sys, os, errno
from shutil import copytree, copy2, rmtree



relPath = os.path.dirname(os.path.dirname(__file__))
curFolder = os.path.dirname(__file__)
baseFolder =os.path.join(curFolder, "package")

if os.path.isdir(baseFolder):
	rmtree(baseFolder)
os.mkdir(baseFolder)


toMove = []
_exclude = ["pyc", "ai", "sh", "bat", "user", "cmake", "inl", "pro", "pri", "txt", "h", "cpp", "hpp", "dll"]
_noFolder = [".git"]
_noFile = ["reloader.py", "packageCreator.py", "run_cmake.py", "smooth_brush_pri_update.py"]
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
		if ".git" in dirName:
			continue
		if "docs" in dirName:
			continue
		if file in _noFile:
			continue
		toMove.append(os.path.join(dirName, file))

for f in toMove:
	if "test" in f.lower():
		print f
	#print f + " > " + f.split("%s/"%curFolder)[-1]
	dst = os.path.join(baseFolder, f.split("%s/"%curFolder)[-1])
	try:
		os.makedirs(os.path.dirname(dst))
	except OSError as e:
		if e.errno != errno.EEXIST:
			raise
	copy2(f, dst)
print("succesfully copied files")
