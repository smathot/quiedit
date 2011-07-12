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

from PyQt4 import QtGui, QtCore

class search_edit(QtGui.QLineEdit):

	"""A simple hide-on-focus-lost edit input"""

	def __init__(self, parent):

		"""
		Constructor

		Arguments:
		parent -- a qtquiedit instance
		"""

		super(search_edit, self).__init__(parent)
		self.quiedit = parent

	def focusOutEvent(self, event):

		"""
		Hide the searchbox on focus lost

		Arguments:
		event -- a focusOut event
		"""

		self.quiedit.search_box.hide()
		
	def keyPressEvent(self, event):

		"""
		Hide on Control+F and Escape

		Arguments:
		event -- a keyPressEvent
		"""

		if self.quiedit.editor.key_match(event, QtCore.Qt.Key_F, QtCore.Qt.ControlModifier) or\
			self.quiedit.editor.key_match(event, QtCore.Qt.Key_Escape):
			self.quiedit.search_box.hide()
		else:
			super(search_edit, self).keyPressEvent(event)