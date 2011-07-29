#!/usr/bin/env python
#-*- coding:utf-8 -*-

from distutils.core import setup
from libquiedit import qtquiedit
import glob

setup(name='quiedit',
	version=qtquiedit.qtquiedit.version,
	description='Fullscreen text editor',
	author='Sebastiaan Mathot',
	author_email='s.mathot@cogsci.nl',
	url='http://www.cogsci.nl',
	scripts=['quiedit'],
	packages=['libquiedit'],
	package_dir={'libquiedit' : 'libquiedit'},
	data_files=[
		('share/applications', ['data/quiedit.desktop']),
		('share/quiedit/resources', ['resources/help.html']),
		('share/quiedit/resources', ['resources/quiedit.png']),
		('share/quiedit/resources', ['resources/keybindings.conf']),
		('share/quiedit/resources', glob.glob('resources/*.theme'))
		]
	)


