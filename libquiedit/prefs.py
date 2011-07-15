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
from libquiedit import speller

class prefs(QtGui.QFrame):

	"""A preference editor"""

	def __init__(self, parent):

		"""
		Constructor
		
		Keyword arguments:
		parent -- the parent widget (default=None)
		"""

		super(prefs, self).__init__(parent)
		self.quiedit = parent
		self.build_gui()

	def set_theme(self):

		"""Set the theme"""

		font = QtGui.QFont()
		font.setPointSize(int(self.quiedit.style["font_size"]))
		font.setFamily(self.quiedit.style["font_family"])
		self.setCursor(QtCore.Qt.ArrowCursor)
		self.setStyleSheet("background: %(editor_background)s; color: %(font_color)s; selection-color: %(editor_background)s; selection-background-color: %(font_color)s" % self.quiedit.style)
		self.combobox_theme.setFont(self.quiedit.theme_font())		
		self.checkbox_auto_indent.setFont(self.quiedit.theme_font())
		self.checkbox_speller_enabled.setFont(self.quiedit.theme_font())
		self.edit_hunspell_path.setFont(self.quiedit.theme_font())
		self.edit_hunspell_dict.setFont(self.quiedit.theme_font())
		self.label_theme.setFont(self.quiedit.theme_font())		
		self.label_auto_indent.setFont(self.quiedit.theme_font())
		self.label_speller_enabled.setFont(self.quiedit.theme_font())
		self.label_hunspell_path.setFont(self.quiedit.theme_font())
		self.label_hunspell_dict.setFont(self.quiedit.theme_font())		
		self.label_hunspell_available.setFont(self.quiedit.theme_font())		
		self.button_apply.setFont(self.quiedit.theme_font())

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
		self.label_theme = QtGui.QLabel("Theme")
		self.form.addRow(self.label_theme, self.combobox_theme)

		self.checkbox_auto_indent = QtGui.QCheckBox()
		self.checkbox_auto_indent.setChecked(self.quiedit.auto_indent)
		self.label_auto_indent = QtGui.QLabel("Indent new lines")
		self.form.addRow(self.label_auto_indent, self.checkbox_auto_indent)		
			
		self.checkbox_speller_enabled = QtGui.QCheckBox()
		self.checkbox_speller_enabled.setChecked(self.quiedit.speller_enabled)
		self.label_speller_enabled = QtGui.QLabel("Spellchecking")
		self.form.addRow(self.label_speller_enabled, self.checkbox_speller_enabled)

		self.edit_hunspell_path = QtGui.QLineEdit(self.quiedit.hunspell_path)
		self.label_hunspell_path = QtGui.QLabel("Path to hunspell")
		self.form.addRow(self.label_hunspell_path, self.edit_hunspell_path)

		self.edit_hunspell_dict = QtGui.QLineEdit(self.quiedit.hunspell_dict)
		self.label_hunspell_dict = QtGui.QLabel("Hunspell dictionary\n(e.g., 'en_US')")
		self.form.addRow(self.label_hunspell_dict, self.edit_hunspell_dict)

		try:
			import hunspell
			self.label_hunspell_available = QtGui.QLabel("dummy")		
		except:			
			self.label_hunspell_available = QtGui.QLabel("Spellchecking is not available, please install pyhunspell")
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
