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

from libquiedit import quieditor
from PyQt4 import QtGui, QtCore
import re

class _markdown(quieditor.quieditor):

	"""Displays a Markdown preview"""

	def __init__(self, parent):

		"""
		Constructor

		Keyword arguments:
		parent -- the parent widget (default=None)
		"""

		super(_markdown, self).__init__(parent)

	def refresh(self):

		"""Update the contents with the markdown generated syntax"""

		self.setHtml(self.toMarkdown())

	def toMarkdown(self):

		"""
		Parse the document using Markdown

		Returns:
		A string with the parsed document
		"""

		try:
			import markdown
		except:
			return 'python-markdown is not available!'
		txt = unicode(self.quiedit.editor.toPlainText())
		html = markdown.markdown(txt, extensions=['extra', 'codehilite'])
		return html
