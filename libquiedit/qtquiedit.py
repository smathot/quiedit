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
from libquiedit import quieditor, speller, prefs, search_edit, navigator, \
	_markdown, export
import sys
import os
import os.path
import csv
import re

class qtquiedit(QtGui.QMainWindow):

	"""The main application"""

	version = "0.23-pre1"
	auto_indent = True
	status_timeout = 3000
	current_path = None
	unsaved_changes = False
	width = 800
	height = 500

	str_indent = "\t"
	ord_indent = 9
	size_indent = 16

	speller_local_interval = 1000
	speller_local_bound = 20

	def __init__(self, parent=None):

		"""
		Constructor

		Keyword arguments:
		parent -- parent widget (default=None)
		"""

		self.debug = "--debug" in sys.argv
		QtGui.QMainWindow.__init__(self, parent, flags= \
			QtCore.Qt.FramelessWindowHint)
		self.restore_state()
		self.set_theme()
		self.editor.check_locally()
		self.editor.setFocus()

	def restore_state(self):

		"""Restore the current window to the saved state"""

		settings = QtCore.QSettings("cogscinl", "quiedit")
		settings.beginGroup("MainWindow");
		self.resize(settings.value("size", QtCore.QSize(self.width, \
			self.height)).toSize())
		self.move(settings.value("pos", QtCore.QPoint(200, 200)).toPoint())
		self.restoreState(settings.value("state").toByteArray())
		if settings.value("fullscreen", True).toBool():
			self.showFullScreen()
		else:
			self.showNormal()
		self.set_unsaved(False)
		self.auto_indent = settings.value("auto_indent", True).toBool()
		self.speller_enabled = settings.value("speller_enabled", True).toBool()
		self.speller_suggest = settings.value("speller_suggest", True).toBool()
		self.speller_max_suggest = settings.value( \
			"speller_max_suggest", 4).toInt()[0]
		self.speller_ignore = settings.value("speller_ignore", ["quiedit", \
			"sebastiaan", "mathot"]).toList()
		self.hunspell_dict = str(settings.value("hunspell_dict", \
			"en_US").toString())
		self.hunspell_path = str(settings.value("hunspell_path", \
			speller.locate_hunspell_path()).toString())
		self.theme = str(settings.value("theme", "solarized-light").toString())
		self.build_gui()
		self.current_path = str(settings.value("current_path", "").toString())
		if self.current_path == "":
			self.current_path = None
		else:
			self.set_status("Resuming %s" % os.path.basename(self.current_path))
		self.restore_content()
		self.editor.set_cursor(settings.value("cursor_pos", 0).toInt()[0])
		settings.endGroup();

	def save_state(self):

		"""Restores the state of the current window"""

		settings = QtCore.QSettings("cogscinl", "quiedit")
		settings.beginGroup("MainWindow")
		settings.setValue("size", self.size())
		settings.setValue("pos", self.pos())
		settings.setValue("state", self.saveState())
		settings.setValue("fullscreen", self.isFullScreen())
		settings.setValue("auto_indent", self.auto_indent)
		settings.setValue("speller_enabled", self.speller_enabled)
		settings.setValue("speller_suggest", self.speller_suggest)
		settings.setValue("speller_ignore", self.speller_ignore)
		settings.setValue("hunspell_dict", self.hunspell_dict)
		settings.setValue("hunspell_path", self.hunspell_path)
		settings.setValue("cursor_pos", self.editor.get_cursor())
		settings.setValue("theme", self.theme)
		settings.setValue("current_path", self.current_path)
		settings.endGroup()
		self.save_content()

	def restore_content(self):

		"""Restore the contents"""

		if os.path.exists(self.saved_content_file()):
			self.editor.setHtml(open(self.saved_content_file()).read())
		else:
			self.editor.clear()

	def save_content(self):

		"""Save the contents"""

		fd = open(self.saved_content_file(), "w")
		fd.write(self.editor.toHtml())
		fd.close()

	def saved_content_file(self):

		"""
		Get the path to the content file

		Returns:
		Path to the content file
		"""

		if os.name == "posix":
			return os.path.join(os.environ["HOME"], ".quiedit-saved-content")
		else:
			return os.path.join(os.environ["USERPROFILE"], \
				".quiedit-saved-content")

	def minimize_win(self):

		"""Minimize the window if it is fullscreen"""

		self.was_fullscreen = self.isFullScreen()
		if self.was_fullscreen:
			self.showNormal()

	def restore_win(self):

		"""Restore fullscreen (if necessary)"""

		if self.was_fullscreen:
			self.showFullScreen()

	def open_file(self):

		"""Opens a file"""

		self.minimize_win()
		flt = "HTML (*.html *.htm);;Plain text (*.txt);;Markdown source (*.md *.markdown)"
		path = unicode(QtGui.QFileDialog.getOpenFileName(self, "Open file", \
			filter=flt))
		self.restore_win()
		if path == "":
			return
		if os.path.exists(path):
			ext = os.path.splitext(path)[1].lower()
			try:
				s = open(path).read()
				self.editor.clear()
				self.editor.set_theme()
				self.editor.setAcceptRichText(True)
				if ext == '.html':
					self.editor.setHtml(s)
				else:
					self.editor.setPlainText(s)
				self.editor.set_theme()
				self.current_path = path
				self.set_status("Opened %s" % os.path.basename(path))
				self.set_unsaved(False)
				self.editor.check_entire_document()
			except Exception as e:
				self.set_status("Error: %s" % e)
		else:
			self.set_status("File does not exist")
		self.show_element("editor")

	def set_unsaved(self, unsaved_changes=True):

		"""
		Sets the unsaved changes status

		Keyword arguments:
		unsaved_changes -- indicates if there are unsaved changes

		Returns:
		"""

		self.unsaved_changes = unsaved_changes

	def save_file(self, always_ask=False):

		"""
		Save a file

		Keyword arguments:
		always_ask -- ask for a filename even if the file already has a name
					  (default=False)

		fmt -- indicates the file format. Can be 'html' or 'text'
		"""

		if self.current_path == None or always_ask:
			title = "Save file as"
			flt = "HTML (*.html *.htm);;Plain text (*.txt);;Markdown source (*.md *.markdown)"
			exts = '.html', '.htm', '.txt', '.md', '.markdown'
			defaultExt = '.html'
			self.minimize_win()
			path = unicode(QtGui.QFileDialog.getSaveFileName(self, title, \
				filter=flt))
			self.restore_win()
			# Save has been cancelled
			if path == "":
				return
			# Make sure that the file has a sensible extension
			if os.path.splitext(path)[1].lower() not in exts:
				path += defaultExt
			self.current_path = path

		path = self.current_path
		ext = os.path.splitext(path)[1].lower()
		if ext in ('.html', '.htm'):
			contents = self.editor.toHtml()
		else:
			contents = self.editor.toPlainText()

		# Write the file contents to disk
		try:
			open(path, "w").write(contents)
			self.set_status("Saved as %s" % os.path.basename(path))
			self.set_unsaved(False)
		except Exception as e:
			self.set_status("Error: %s" % e)

		self.show_element("editor")

	def new_file(self):

		"""Clear the buffer and start a new file"""

		if self.unsaved_changes:

			self.minimize_win()
			if QtGui.QMessageBox.question(self, "New file", \
				"Discard current file?", QtGui.QMessageBox.No, \
				QtGui.QMessageBox.Yes) == QtGui.QMessageBox.No:
				self.restore_win()
				return
			self.restore_win()

		self.editor.clear()
		self.editor.setAcceptRichText(True)
		self.current_path = None
		self.set_status("Starting new file")
		self.set_unsaved(False)
		self.show_element("editor")

	def cleanse_html(self, html):

		"""
		Strips the ugly QTextEdit formatting from the HTML

		Arguments:
		An ugly HTML string

		Returns:
		A pretty HTML string
		"""

		s = str(unicode(html).encode('ascii', 'xmlcharrefreplace'))

		# Remove headers
		s = re.sub( r'<head>(.*?)</head>', "", s, flags=re.DOTALL)
		s = re.sub( r'<body(.*?)>', "<body>", s)

		# Replace paragraphs
		s = re.sub( r'<p(.*?)>', "<p>", s)

		# Remove tabs
		s = s.replace("\t", "")

		# Replace bold
		s = re.sub( r'<span(.*?)font-weight:(.*?)>(.*?)</span>', r"<b>\3</b>", \
			s)

		# Replace italics
		s = re.sub( r'<span(.*?)font-style:italic;(.*?)>(.*?)</span>', \
			r"<i>\3</i>", s)

		# Replace spurious spans
		s = re.sub( r'<span(.*?)>(.*?)</span>', r"\2", s)

		return "<!-- Created with QuiEdit --!>\n" + s

	def get_resource(self, res):

		"""
		Gives the full path to a resource file

		Arguments:
		res -- name of the resource file

		Returns:
		The full path to the resource
		"""

		for f in self.resource_folders():
			path = os.path.join(f, res)
			if os.path.exists(path):
				return path
		raise Exception("Failed to find resource '%s'" % res)

	def resource_folders(self):

		"""
		Returns a list of folders containing the resources

		Returns:
		A list of folder names
		"""

		l = []
		if os.path.exists("resources"):
			l.append(os.path.join("resources"))
		if os.name == "posix":
			if os.path.exists(os.path.join(os.environ["HOME"], ".quiedit", \
				"resources")):
				l.append(os.path.join(os.environ["HOME"], ".quiedit", \
					"resources"))
			if os.path.exists("/usr/share/quiedit/resources/"):
				l.append("/usr/share/quiedit/resources/")
		elif os.name == "nt":
			if os.path.exists(os.path.join(os.environ["USERPROFILE"], \
				".quiedit", "resources")):
				l.append(os.path.join(os.environ["USERPROFILE"], ".quiedit", \
					"resources"))
		return l

	def build_gui(self):

		"""Initialize the GUI elements"""

		self.setWindowTitle("Quiedit %s" % self.version)
		self.setWindowIcon(QtGui.QIcon(self.get_resource("quiedit.png")))

		# Status widget, visible in all components
		self.status = QtGui.QLabel("Press Control+H for help")
		self.status.setAlignment(QtCore.Qt.AlignHCenter)

		# Editor component
		self.editor = quieditor.quieditor(self)
		self.editor.setFrameStyle(QtGui.QFrame.NoFrame)

		# Search widget, visible in editor component
		self.search_edit = search_edit.search_edit(self)
		self.search_edit.returnPressed.connect(self.editor.perform_search)
		self.search_label = QtGui.QLabel("Search:")
		self.search_layout = QtGui.QHBoxLayout()
		self.search_layout.addWidget(self.search_label)
		self.search_layout.addWidget(self.search_edit)
		self.search_layout.setContentsMargins(8, 8, 8, 8)
		self.search_box = QtGui.QFrame()
		self.search_box.setLayout(self.search_layout)
		self.search_box.hide()

		# Help component
		self.help = quieditor.quieditor(self, readonly=True)
		self.help.setFrameStyle(QtGui.QFrame.NoFrame)
		self.help.hide()

		# Preferences component
		self.prefs = prefs.prefs(self)
		self.prefs.hide()

		# Navigator component
		self.navigator = navigator.navigator(self)
		self.navigator.setFrameStyle(QtGui.QFrame.NoFrame)
		self.navigator.hide()

		# Markdown component
		self._markdown = _markdown._markdown(self)
		self._markdown.setFrameStyle(QtGui.QFrame.NoFrame)
		self._markdown.hide()

		# Export component
		self.export = export.export(self)
		self.export.setFrameStyle(QtGui.QFrame.NoFrame)
		self.export.hide()

		# Layout for all components, only one of which is visible at a time
		self.editor_layout = QtGui.QVBoxLayout()
		self.editor_layout.setContentsMargins(0, 0, 0, 0)
		self.editor_layout.addWidget(self.editor)
		self.editor_layout.addWidget(self.help)
		self.editor_layout.addWidget(self.prefs)
		self.editor_layout.addWidget(self.navigator)
		self.editor_layout.addWidget(self.search_box)
		self.editor_layout.addWidget(self._markdown)
		self.editor_layout.addWidget(self.export)
		self.editor_layout.setSpacing(0)
		self.editor_frame = QtGui.QFrame()
		self.editor_frame.setFrameStyle(QtGui.QFrame.Box)
		self.editor_frame.setLayout(self.editor_layout)

		# Central widget to contain all central widgets, i.e. everything except
		# the padding around the window
		self.central_vbox = QtGui.QVBoxLayout()
		self.central_vbox.addWidget(QtGui.QLabel())
		self.central_vbox.addWidget(self.editor_frame)
		self.central_vbox.addWidget(self.status)
		self.central_widget = QtGui.QWidget()
		self.central_widget.setLayout(self.central_vbox)

		# Main widget that contains everything, i.e. the central widget plus
		# padding
		self.main_hbox = QtGui.QHBoxLayout()
		self.main_hbox.addStretch()
		self.main_hbox.addWidget(self.central_widget)
		self.main_hbox.addStretch()
		self.main_widget = QtGui.QWidget()
		self.main_widget.setLayout(self.main_hbox)
		self.setCentralWidget(self.main_widget)

	def set_theme(self):

		"""Sets the current theme"""

		self.style = {}
		try:
			self.get_resource("%s.theme" % self.theme)
		except:
			self.theme = 'system-default'
		for l in open(self.get_resource("%s.theme" % self.theme)):
			w = l.split(" = ")
			if len(w) == 2:
				self.style[w[0].strip()] = w[1].strip()
		if self.theme != 'system-default':
			self.main_widget.setStyleSheet("background: %s;" \
				% self.style["main_background"])
			self.editor_frame.setStyleSheet("color: %s;" \
				% self.style["border_color"])
			self.search_box.setStyleSheet( \
				"background: %(font_color)s; color: %(editor_background)s; selection-color: %(font_color)s; selection-background-color: %(editor_background)s" \
				% self.style)
			self.search_edit.setStyleSheet("border: 0;")
			self.search_edit.setFont(self.theme_font())
			self.search_label.setFont(self.theme_font())
			self.status.setFont(self.theme_font("xs_font_size"))
			self.status.setStyleSheet("color: %s;" % self.style["status_color"])
		self.central_widget.setMinimumWidth(int(self.style["editor_width"]))
		self.central_widget.setMaximumWidth(int(self.style["editor_width"]))
		self.editor.set_theme()
		self.navigator.set_theme()
		self.help.set_theme()
		self.prefs.set_theme()
		self._markdown.set_theme()
		self.export.set_theme()
		self.editor.check_entire_document()
		self.setCursor(QtCore.Qt.BlankCursor)

	def theme_font(self, size="font_size"):

		"""
		Gives the theme font

		Returns:
		A QFont
		"""

		font = QtGui.QFont()
		font.setPointSize(int(self.style[size]))
		font.setFamily(self.style["font_family"])
		return font

	def available_themes(self):

		"""
		Lists available themes

		Returns:
		A list of theme names
		"""

		themes = []
		for dirname in self.resource_folders():
			for basename in os.listdir(dirname):
				path = os.path.join(dirname, basename)
				base, ext = os.path.splitext(basename)
				if ext == ".theme" and base not in themes:
					themes.append(base)
		return themes

	def set_status(self, msg=""):

		"""
		Present a status message

		Keyword arguments:
		msg -- the message (default="")
		"""

		self.status.setText(msg)
		if msg != "":
			QtCore.QTimer.singleShot(self.status_timeout, self.set_status)

	def show_element(self, element):

		"""
		Show only one part of the GUI

		Keyword arguments:
		element -- one of the elements
		"""

		self.help.setVisible(element == "help")
		self.prefs.setVisible(element == "prefs")
		self.navigator.setVisible(element == "navigator")
		self.editor.setVisible(element == "editor")
		self._markdown.setVisible(element == "markdown")
		self.export.setVisible(element == "export")

	def closeEvent(self, event):

		"""
		Neatly close the application

		Arguments:
		event -- a closeEvent
		"""

		self.save_state()
		event.accept()

