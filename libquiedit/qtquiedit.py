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
from libquiedit import quieditor, speller, prefs, search_edit,_markdown, \
	command_edit, theme
import libquiedit
import sys
import os
import os.path
import csv
import re

class qtquiedit(QtGui.QMainWindow):

	"""The main application"""

	encoding = u'utf-8'
	auto_indent = True
	status_timeout = 3000
	current_path = None
	unsaved_changes = False
	width = 800
	height = 500
	str_indent = u'\t'
	ord_indent = 9
	size_indent = 16
	speller_local_interval = 1000
	speller_local_bound = 20
	recent_files = []

	def __init__(self, parent=None):

		"""
		Constructor

		Keyword arguments:
		parent -- parent widget (default=None)
		"""

		self.debug = "--debug" in sys.argv
		QtGui.QMainWindow.__init__(self, parent)
		self.restore_state()
		self.set_theme()
		self.editor.check_locally()
		self.editor.setFocus()

	def add_recent_file(self, path):

		"""
		Adds a path to the list of recent files.

		Arguments:
		path		--	The path to add.
		"""

		if path not in self.recent_files:
			self.recent_files.append(path)
		self.recent_files = self.recent_files[:9]

	def restore_state(self):

		"""Restore the current window to the saved state"""

		settings = QtCore.QSettings(u"cogscinl", u"quiedit")
		settings.beginGroup(u"MainWindow");
		self.resize(settings.value(u"size", QtCore.QSize(self.width, \
			self.height)).toSize())
		self.move(settings.value(u"pos", QtCore.QPoint(200, 200)).toPoint())
		self.restoreState(settings.value(u"state").toByteArray())
		if settings.value(u"fullscreen", True).toBool():
			self.showFullScreen()
		else:
			self.showNormal()
		self.set_unsaved(False)
		self.auto_indent = settings.value(u"auto_indent", True).toBool()
		self.speller_enabled = settings.value(u"speller_enabled", True).toBool()
		self.speller_suggest = settings.value(u"speller_suggest", True).toBool()
		self.speller_max_suggest = settings.value( \
			u"speller_max_suggest", 4).toInt()[0]
		self.speller_ignore = settings.value(u"speller_ignore", [u"quiedit", \
			u"sebastiaan", "mathot"]).toList()
		self.highlighter_enabled = settings.value(u"highlighter_enabled", \
			True).toBool()
		self.hunspell_dict = unicode(settings.value(u"hunspell_dict", \
			u"en_US").toString())
		self.hunspell_path = unicode(settings.value(u"hunspell_path", \
			speller.locate_hunspell_path()).toString())
		self.theme = unicode(settings.value(u"theme", u"default").toString())
		self._theme = theme.theme(self)
		self.build_gui()
		self.current_path = unicode(settings.value(u"current_path", u"") \
			.toString())
		if self.current_path == u"":
			self.current_path = None
		else:
			self.set_status(u"Resuming %s" % os.path.basename( \
				self.current_path))
		self.restore_content()
		self.editor.set_cursor(settings.value(u"cursor_pos", 0).toInt()[0])
		self.recent_files = settings.value(u"recent_files", []).toList()
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
		settings.setValue("highlighter_enabled", self.highlighter_enabled)
		settings.setValue("speller_ignore", self.speller_ignore)
		settings.setValue("hunspell_dict", self.hunspell_dict)
		settings.setValue("hunspell_path", self.hunspell_path)
		settings.setValue("cursor_pos", self.editor.get_cursor())
		settings.setValue("theme", self.theme)
		settings.setValue("current_path", self.current_path)
		settings.setValue("recent_files", self.recent_files)
		settings.endGroup()
		self.save_content()

	def restore_content(self):

		"""Restore the contents"""

		# If we were working on a file, open it and resume.
		if self.current_path not in (u'', None):
			# If the current file does not exist, notify the user and start with
			# a clear file.
			if not os.path.exists(self.current_path):
				self.set_status( \
					u'The file that you were working on (%s) seems to have dissappeared.' \
					% os.path.basename(self.current_path))
				self.current_path = u''
				self.editor.clear()
				return
			print(u'qtquiedit.restore_content(): opening %s' \
				% self.current_path)
			content = open(self.current_path).read().decode(self.encoding, \
				u'ignore')
		# If we were not working on a file, see if there is a saved file and
		# start from there. If not, start with a clear file.
		else:
			saved_content_path = self.saved_content_file()
			if not os.path.exists(saved_content_path):
				self.editor.clear()
				return
			content = open(saved_content_path).read().decode(self.encoding, \
				u'ignore')
			print(u'qtquiedit.restore_content(): opening %s' \
				% saved_content_path)
		self.editor.set_text(content)

	def save_content(self):

		"""Save the contents"""

		if self.current_path in (u'', None):
			path = self.saved_content_file()
		else:
			path = self.current_path
		print(u'qtquiedit.save_content(): saving to %s' % path)
		fd = open(path, u'w')
		fd.write(unicode(self.editor.toPlainText()).encode(u'utf-8'))
		fd.close()

	def saved_content_file(self):

		"""
		Gets the path to the content file.

		Returns:
		The path to the content file.
		"""

		if os.name == u'posix':
			home_folder = os.environ[u"HOME"]
		else:
			home_folder = os.environ[u"USERPROFILE"]
		path = os.path.join(home_folder.decode(sys.getfilesystemencoding()), \
			u".quiedit-saved-content")
		return path

	def minimize_win(self):

		"""Minimize the window if it is fullscreen"""

		self.was_fullscreen = self.isFullScreen()
		if self.was_fullscreen:
			self.showNormal()

	def restore_win(self):

		"""Restore fullscreen (if necessary)"""

		if self.was_fullscreen:
			self.showFullScreen()

	def open_file(self, path=None):

		"""
		Automatically saves pending changes and opens a file.

		Keyword arguments:
		path	--	The file to open or None to present a file dialog.
		"""

		if path == None:
			self.minimize_win()
			flt = u"Markdown source (*.md *.markdown);;Plain text (*.txt)"
			path = unicode(QtGui.QFileDialog.getOpenFileName(self, \
				u"Open file", filter=flt))
			self.restore_win()
		if path == u"":
			return
		if self.editor.toPlainText().trimmed() != u'':
			self.save_file()
		if os.path.exists(path):
			ext = os.path.splitext(path)[1].lower()
			try:
				s = open(path).read().decode(self.encoding, u'ignore')
				self.editor.clear()
				self.editor.setAcceptRichText(True)
				self.editor.set_text(s)
				self.current_path = path
				self.set_status(u"Opened %s" % os.path.basename(path))
				self.set_unsaved(False)
				self.editor.check_entire_document()
				self.add_recent_file(path)
			except Exception as e:
				self.set_status(u"Error: %s" % e)
		else:
			self.set_status(u"File does not exist")
		self.show_element(u"editor")

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
			title = u"Save file as"
			flt = u"Markdown source (*.md *.markdown);;Plain text (*.txt)"
			exts = u'.md', u'.markdown', u'.txt'
			defaultExt = u'.md'
			self.minimize_win()
			path = unicode(QtGui.QFileDialog.getSaveFileName(self, title, \
				filter=flt))
			self.restore_win()
			# Save has been cancelled
			if path == u"":
				return
			# Make sure that the file has a sensible extension
			if os.path.splitext(path)[1].lower() not in exts:
				path += defaultExt
			self.current_path = path

		path = self.current_path
		ext = os.path.splitext(path)[1].lower()
		contents = unicode(self.editor.toPlainText())
		contents = contents.replace(unicode(os.linesep), u'\n')
		if not contents.endswith(u'\n'):
			contents += u'\n'

		# Write the file contents to disk
		try:
			open(path, u"w").write(contents.encode(self.encoding))
			self.set_status(u"Saved as %s" % os.path.basename(path))
			self.set_unsaved(False)
			self.add_recent_file(path)
		except Exception as e:
			self.set_status(u"Error: %s" % e)

		self.show_element(u"editor")

	def new_file(self):

		"""Clear the buffer and start a new file"""

		if self.unsaved_changes and self.editor.toPlainText().trimmed() != u'':

			#self.minimize_win()
			#if QtGui.QMessageBox.question(self, u"New file", \
				#u"Discard current file?", QtGui.QMessageBox.No, \
				#QtGui.QMessageBox.Yes) == QtGui.QMessageBox.No:
				#self.restore_win()
				#return
			#self.restore_win()
			self.save_file()

		self.editor.clear()
		self.editor.setAcceptRichText(False)
		self.current_path = None
		self.set_status(u"Starting new file")
		self.set_unsaved(False)
		self.show_element(u"editor")

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
		raise Exception(u"Failed to find resource '%s'" % res)

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

		self.setWindowTitle(u"Quiedit %s" % libquiedit.version)
		self.setWindowIcon(QtGui.QIcon(self.get_resource(u"quiedit.png")))

		# Status widget, visible in all components
		self.status = QtGui.QLabel(u"Press Control+H for help")
		self.status.setAlignment(QtCore.Qt.AlignHCenter)

		# Editor component
		self.editor = quieditor.quieditor(self)
		self.editor.setFrameStyle(QtGui.QFrame.NoFrame)

		# Search widget, visible in editor component
		self.search_edit = search_edit.search_edit(self)
		self.search_edit.returnPressed.connect(self.editor.perform_search)
		self.search_label = QtGui.QLabel(u"Search:")
		self.search_layout = QtGui.QHBoxLayout()
		self.search_layout.addWidget(self.search_label)
		self.search_layout.addWidget(self.search_edit)
		self.search_layout.setContentsMargins(8, 8, 8, 8)
		self.search_box = QtGui.QFrame()
		self.search_box.setLayout(self.search_layout)
		self.search_box.hide()

		# Command widget, visible in editor component
		self.command_edit = command_edit.command_edit(self)
		self.command_label = QtGui.QLabel(u"$")
		self.command_layout = QtGui.QHBoxLayout()
		self.command_layout.addWidget(self.command_label)
		self.command_layout.addWidget(self.command_edit)
		self.command_layout.setContentsMargins(8, 8, 8, 8)
		self.command_box = QtGui.QFrame()
		self.command_box.setLayout(self.command_layout)
		self.command_box.hide()

		# Help component
		self.help = quieditor.quieditor(self, readonly=True)
		self.help.setFrameStyle(QtGui.QFrame.NoFrame)
		self.help.set_text(open(self.get_resource(u'keybindings.conf')) \
			.read())
		self.help.hide()

		# Preferences component
		self.prefs = prefs.prefs(self)
		self.prefs.hide()

		# Markdown component
		self._markdown = _markdown._markdown(self)
		self._markdown.setFrameStyle(QtGui.QFrame.NoFrame)
		self._markdown.hide()

		# Layout for all components, only one of which is visible at a time
		self.editor_layout = QtGui.QVBoxLayout()
		self.editor_layout.setContentsMargins(0, 0, 0, 0)
		self.editor_layout.addWidget(self.editor)
		self.editor_layout.addWidget(self.help)
		self.editor_layout.addWidget(self.prefs)
		self.editor_layout.addWidget(self.search_box)
		self.editor_layout.addWidget(self.command_box)
		self.editor_layout.addWidget(self._markdown)
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

		self._theme.apply()

	def available_themes(self):

		"""
		Lists available themes

		Returns:
		A list of theme names
		"""

		return self._theme.themeDict.keys()

	def set_status(self, msg=u""):

		"""
		Present a status message

		Keyword arguments:
		msg -- the message (default="")
		"""

		self.status.setText(msg)
		if msg != u"":
			QtCore.QTimer.singleShot(self.status_timeout, self.set_status)

	def show_element(self, element):

		"""
		Show only one part of the GUI

		Keyword arguments:
		element -- one of the elements
		"""

		self.help.setVisible(element == "help")
		self.prefs.setVisible(element == "prefs")
		self.editor.setVisible(element == "editor")
		self._markdown.setVisible(element == "markdown")

	def closeEvent(self, event):

		"""
		Neatly close the application

		Arguments:
		event -- a closeEvent
		"""

		self.save_state()
		event.accept()

