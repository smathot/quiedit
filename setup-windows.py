#!/usr/bin/env python

from distutils.core import setup
import glob
import py2exe
import os
import os.path
import shutil

# Create empty destination folders
if os.path.exists("dist"):
	shutil.rmtree("dist")
os.mkdir("dist")
os.mkdir(os.path.join("dist", "resources"))

# Setup options
setup(

	# Use 'console' to have the programs run in a terminal and
	# 'windows' to run them normally.
	windows = [{
		"script" : "quiedit",
		'icon_resources': [(0, os.path.join("resources", "quiedit.ico"))],
		}],
	options = {
		'py2exe' : {
		'compressed' : True,
		'optimize': 2,
		'bundle_files': 3,
		'includes': 'sip',
		}
	},
)

# Only copy the relevant resources, to keep the folder clean
for f in os.listdir("resources"):
	if os.path.splitext(f)[1] in [".theme"] or f in ("help.html", "quiedit.png", "keybindings.conf"):
		shutil.copyfile(os.path.join("resources", f), os.path.join("dist", "resources", f))

