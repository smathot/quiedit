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

import time
import os
from PyQt4 import QtGui, QtCore
from libquiedit import quiframe

class export(quiframe.quiframe):

	"""A number of export options"""

	def build_gui(self):

		"""Initialize the GUI elements"""

		self.form = QtGui.QFormLayout()
		self.form.setContentsMargins(32, 32, 32, 32)
		self.form.setSpacing(16)

		self.button_export_txt = QtGui.QPushButton( \
			"Export to plain text/ markdown source\n[.txt, .md, .markdown]")
		self.button_export_txt.clicked.connect(self.export_txt)
		self.form.addRow(self.button_export_txt)

		self.button_export_simple_html = QtGui.QPushButton( \
			"Export to simplified HTML\n[.html, .htm]")
		self.button_export_simple_html.clicked.connect(self.export_simple_html)
		self.form.addRow(self.button_export_simple_html)

		self.button_export_markdown = QtGui.QPushButton( \
			"Parse Markdown and export to HTML\n[.html, .htm]")
		self.button_export_markdown.clicked.connect(self.export_markdown)
		self.form.addRow(self.button_export_markdown)

		self.button_resume = QtGui.QPushButton( \
			"Resume editing")
		self.button_resume.clicked.connect(self.resume)
		self.form.addRow(self.button_resume)

		self.setLayout(self.form)

	def set_theme(self):

		"""Set the theme"""


		super(export, self).set_theme()
		if self.quiedit.theme != 'system-default':
			self.button_resume.setFont(self.quiedit.theme_font())
			self.button_export_markdown.setFont(self.quiedit.theme_font())
			self.button_export_txt.setFont(self.quiedit.theme_font())
			self.button_export_simple_html.setFont(self.quiedit.theme_font())

	def resume(self):

		"""Resume editing"""

		# Resume editing
		self.quiedit.setCursor(QtCore.Qt.BlankCursor)
		self.quiedit.show_element("editor")

	def export(self, contents, title, flt):

		"""
		Export the file

		Arguments:
		contents -- a string with the file contents as they should be saved to
					file
		title -- a title for the Save dialog
		flt -- a filter for the save dialog
		"""

		self.quiedit.minimize_win()
		path = unicode(QtGui.QFileDialog.getSaveFileName(self, title, \
			filter=flt))
		self.quiedit.restore_win()
		if path == "":
			return
		try:
			open(path, "w").write(contents)
			self.quiedit.set_status("Saved as %s" % os.path.basename(path))
		except Exception as e:
			self.quiedit.set_status("Error: %s" % e)

	def export_txt(self):

		"""Export to plain text"""

		title = "Export to plain text / Markdown source"
		flt = "Plain text (*.txt);;Markdown source (*.md *.markdown)"
		contents = self.quiedit.editor.toPlainText()
		self.export(contents, title, flt)

	def export_simple_html(self):

		"""Export to simplified HTML"""

		title = "Export to simplified HTML format"
		flt = "HTML files (*.html *.htm)"
		contents = self.quiedit.cleanse_html(self.quiedit.editor.toHtml())
		self.export(contents, title, flt)

	def export_markdown(self):

		"""Parse to markdown and save to HTML"""

		title = "Parse Markdown and export to HTML"
		flt = "HTML files (*.html *.htm)"
		contents = self.quiedit._markdown.toMarkdown()
		self.export(contents, title, flt)