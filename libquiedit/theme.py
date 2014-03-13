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
import yaml

class theme(object):

	"""Handles theming."""

	def __init__(self, editor):

		"""
		Constructor.

		Arguments:
		editor	--	A qtquiedit object.
		"""

		self.editor = editor
		self.themeDict = yaml.load(open(self.editor.get_resource( \
			u'themes.yaml')).read())
		self.theme = self.recTheme(self.editor.theme)

	def apply(self):

		"""Applies the theme."""

		stylesheet = u"""
			background: %(editor_background)s;
			color: %(font_color)s;
			selection-color: %(editor_background)s;
			selection-background-color: %(font_color)s;
			font-family: %(font_family)s;
			font-size: %(font_size)spt;
			""" % self.theme
		self.editor.main_widget.setStyleSheet(u"background: %s;" \
			% self.theme[u"main_background"])
		self.editor.editor_frame.setStyleSheet(u"color: %s;" \
			% self.theme[u"border_color"])
		self.editor.search_box.setStyleSheet(stylesheet)
		self.editor.search_edit.setStyleSheet(u"border: 0;")
		self.editor.search_edit.setFont(self.font())
		self.editor.search_label.setFont(self.font())
		self.editor.command_box.setStyleSheet(stylesheet)
		self.editor.command_edit.setStyleSheet(u"border: 0;")
		self.editor.command_edit.setFont(self.font())
		self.editor.command_label.setFont(self.font())
		self.editor.status.setFont(self.font())
		self.editor.status.setStyleSheet(u"color: %s;" % self.theme[ \
			u"status_color"])
		self.editor.central_widget.setMinimumWidth(int(self.theme[ \
			u"editor_width"]))
		self.editor.central_widget.setMaximumWidth(int(self.theme[ \
			u"editor_width"]))
		# Apply the theme to all quieditors
		for quieditor in self.editor.editor, self.editor.help, \
			self.editor._markdown:
			quieditor.setStyleSheet(stylesheet)
			if not self.theme[u"scrollbar"]:
				quieditor.setVerticalScrollBarPolicy( \
					QtCore.Qt.ScrollBarAlwaysOff)
			quieditor.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
		# Apply the theme to the preferences screen
		self.editor.prefs.setStyleSheet(stylesheet)
		# Redo spellingcheck in the editor
		self.editor.editor.check_entire_document()
		# Hide the cursor for the main screen
		self.editor.setCursor(QtCore.Qt.BlankCursor)

	def font(self):

		"""
		Gives the theme font.

		Returns:
		A QFont.
		"""

		font = QtGui.QFont()
		font.setPointSize(int(self.theme[u'font_size']))
		font.setFamily(self.theme[u'font_family'])
		return font

	def recTheme(self, theme):

		"""
		Gets the current theme, respecting inheritance.

		Arguments:
		theme	--	The theme name.

		Returns:
		A dictionary with with the theme information.
		"""

		if theme not in self.themeDict:
			print(u'theme.__init__(): %s is not a valid theme' % theme)
			theme = u'default'
		d = self.themeDict[theme]
		if u'inherits' in d:
			_d = self.recTheme(d[u'inherits'])
			for key, val in _d.items():
				if key not in d:
					d[key] = val
		return d
