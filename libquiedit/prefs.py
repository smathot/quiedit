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
from libquiedit import speller, quiframe

class prefs(quiframe.quiframe):

	"""A preference editor"""

	def build_gui(self):

		"""Initialize the GUI elements"""

		self.form = QtGui.QFormLayout()
		self.form.setContentsMargins(32, 32, 32, 32)
		self.form.setSpacing(16)

		self.combobox_theme = QtGui.QComboBox(self)
		i = 0
		for theme in self.quiedit.available_themes():
			self.combobox_theme.addItem(theme)
			if theme == self.quiedit.theme:
				self.combobox_theme.setCurrentIndex(i)
			i += 1
		self.label_theme = QtGui.QLabel( \
			"Theme\n(system-default requires restart)")
		self.label_theme.setAlignment(QtCore.Qt.AlignRight)
		self.form.addRow(self.label_theme, self.combobox_theme)

		self.checkbox_auto_indent = QtGui.QCheckBox()
		self.checkbox_auto_indent.setChecked(self.quiedit.auto_indent)
		self.label_auto_indent = QtGui.QLabel("Indent new lines")
		self.form.addRow(self.label_auto_indent, self.checkbox_auto_indent)

		self.checkbox_speller_enabled = QtGui.QCheckBox()
		self.checkbox_speller_enabled.setChecked(self.quiedit.speller_enabled)
		self.label_speller_enabled = QtGui.QLabel("Spellchecking")
		self.form.addRow(self.label_speller_enabled, \
			self.checkbox_speller_enabled)

		self.edit_hunspell_path = QtGui.QLineEdit(self.quiedit.hunspell_path)
		self.label_hunspell_path = QtGui.QLabel("Path to hunspell")
		self.form.addRow(self.label_hunspell_path, self.edit_hunspell_path)

		self.edit_hunspell_dict = QtGui.QLineEdit(self.quiedit.hunspell_dict)
		self.label_hunspell_dict = QtGui.QLabel( \
			"Hunspell dictionary\n(e.g., 'en_US')")
		self.label_hunspell_dict.setAlignment(QtCore.Qt.AlignRight)
		self.form.addRow(self.label_hunspell_dict, self.edit_hunspell_dict)

		try:
			import hunspell
			self.label_hunspell_available = QtGui.QLabel("dummy")
		except:
			self.label_hunspell_available = QtGui.QLabel( \
				"Spellchecking is not available, please install pyhunspell")
			self.label_hunspell_available.setWordWrap(True)
			self.form.addRow(self.label_hunspell_available)
			self.checkbox_speller_enabled.setEnabled(False)
			self.edit_hunspell_path.setEnabled(False)
			self.edit_hunspell_dict.setEnabled(False)
			self.label_speller_enabled.setEnabled(False)
			self.label_hunspell_path.setEnabled(False)
			self.label_hunspell_dict.setEnabled(False)

		self.button_apply = QtGui.QPushButton("Apply")
		self.button_apply.clicked.connect(self._apply)
		self.form.addRow(self.button_apply)
		self.setLayout(self.form)

	def _apply(self):

		"""Apply changes and resume editing"""

		# Set the speller
		self.quiedit.speller_enabled = self.checkbox_speller_enabled.isChecked()
		self.quiedit.hunspell_path = str(self.edit_hunspell_path.text())
		self.quiedit.hunspell_dict = str(self.edit_hunspell_dict.text())
		self.quiedit.editor.speller = speller.speller(self.quiedit)

		# Set the theme
		self.quiedit.theme = str(self.combobox_theme.currentText())
		self.quiedit.set_theme()
		self.quiedit.auto_indent = self.checkbox_auto_indent.isChecked()

		# Continue editing
		self.quiedit.setCursor(QtCore.Qt.BlankCursor)
		self.quiedit.show_element("editor")
