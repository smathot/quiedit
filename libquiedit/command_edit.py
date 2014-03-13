# -*- coding: utf-8 -*-

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

import yaml
from PyQt4 import QtGui, QtCore

class command_edit(QtGui.QLineEdit):

	"""A simple hide-on-focus-lost edit input"""

	def __init__(self, parent):

		"""
		Constructor

		Arguments:
		parent -- a qtquiedit instance
		"""

		super(command_edit, self).__init__(parent)
		self.quiedit = parent
		self.snippets = yaml.load(open(self.quiedit.get_resource( \
			u'snippets.yaml')).read())
		self.returnPressed.connect(self.execute)

	def execute(self):

		"""Executes the current command."""

		cmd = unicode(self.text()).split()
		if len(cmd) == 2 and cmd[0] == u'snp':
			snippet = cmd[1]
			if snippet in self.snippets:
				self.quiedit.editor.insertText(self.snippets[snippet])
		self.clear()
		self.quiedit.command_box.hide()

	def focusOutEvent(self, event):

		"""
		Hide the searchbox on focus lost

		Arguments:
		event -- a focusOut event
		"""

		self.quiedit.command_box.hide()

	def keyPressEvent(self, event):

		"""
		Hide on Escape

		Arguments:
		event 	--	A keyPressEvent.
		"""

		if self.quiedit.editor.key_match(event, QtCore.Qt.Key_Escape):
			self.quiedit.command_box.hide()
		else:
			super(command_edit, self).keyPressEvent(event)
