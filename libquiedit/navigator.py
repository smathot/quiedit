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

class navigator(quieditor.quieditor):

	"""Displays the anchors in the text"""

	def __init__(self, parent):

		"""
		Constructor
		
		Keyword arguments:
		parent -- the parent widget (default=None)
		"""		

		super(navigator, self).__init__(parent, readonly=True)

	def refresh(self):

		"""Update the contents to match the anchors in the text"""

		self.clear()
		self.insertHtml("<B>Anchors</B><BR /><BR />")
		html = self.quiedit.editor.toHtml().toLower()
		anchors = re.findall(r"<a name=\"(\w+)\"></a>", html)
		if len(anchors) == 0:
			self.insertHtml("No anchors found<BR />")
		else:
			i = 1
			for anchor in anchors:
				self.insertHtml("[%d] <A HREF='%s' STYLE='color: %s;'>%s</A><BR />" % (i, anchor, self.quiedit.style["border_color"], anchor))
				i += 1
		self.insertHtml("<BR />Press Control+Shift+N to resume editing")

	def mouseDoubleClickEvent(self, event):

		"""
		Jump to an anchor on doubleclick

		Arguments:
		event -- a QMouseEvent
		"""

		anchor = self.anchorAt(event.pos())
		if anchor != "":
			self.quiedit.editor.scrollToAnchor(anchor)
			self.quiedit.show_element("editor")

