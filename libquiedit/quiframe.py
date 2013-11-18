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

from PyQt4 import QtGui, QtCore

class quiframe(QtGui.QFrame):

	"""A preference editor"""

	def __init__(self, parent):

		"""
		Constructor

		Keyword arguments:
		parent -- the parent widget (default=None)
		"""

		super(quiframe, self).__init__(parent)
		self.quiedit = parent
		self.build_gui()

	def build_gui(self):

		"""Builds the GUI"""

		pass