#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
This file is part of quiedit.

quiedit is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

quiedit is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with quiedit.  If not, see <http://www.gnu.org/licenses/>.
"""

from distutils.core import setup
import libquiedit

setup(name='quiedit',
	version=libquiedit.version,
	description='Fullscreen text editor',
	author='Sebastiaan Mathot',
	author_email='s.mathot@cogsci.nl',
	url='http://www.cogsci.nl',
	scripts=['quiedit'],
	packages=['libquiedit'],
	package_dir={'libquiedit' : 'libquiedit'},
	data_files=[
		('share/applications', ['data/quiedit.desktop']),
		('share/quiedit/resources', ['resources/quiedit.png']),
		('share/quiedit/resources', ['resources/keybindings.conf']),
		('share/quiedit/resources', ['resources/snippets.yaml']),
		('share/quiedit/resources', ['resources/themes.yaml']),
		]
	)



