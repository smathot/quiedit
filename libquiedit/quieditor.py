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

import time
from PyQt4 import QtGui, QtCore
from libquiedit import speller, highlighter

class quieditor(QtGui.QTextEdit):

	"""A fancy text editor"""

	def __init__(self, parent=None, readonly=False):

		"""
		Constructor

		Keyword arguments:
		parent -- the parent widget (default=None)
		readonly -- makes the editor readonly (default=False)
		"""

		super(quieditor, self).__init__(parent)
		self.quiedit = parent
		self.speller_lock = False
		self.setReadOnly(readonly)
		self.textChanged.connect(self.quiedit.set_unsaved)
		self.set_keybindings()
		self.setTabStopWidth(self.quiedit.size_indent)
		if self.quiedit.speller_enabled:
			self.speller = speller.speller(self.quiedit)
		if not readonly and self.quiedit.highlighter_enabled:
			highlighter.MarkdownHighlighter(self)

	def get_cursor(self):

		"""
		Get the cursor position

		Returns:
		The cursor position
		"""

		return self.textCursor().position()

	def set_cursor(self, pos):

		"""
		Set the cursor position:

		Arguments:
		pos -- the cursor position
		"""

		cursor = self.textCursor()
		cursor.setPosition(pos)
		self.setTextCursor(cursor)

	def key_match(self, event, key, modifier=None):

		"""
		Checks if a QKeyEvent matches a keypress and optionally a modifier

		Arguments:
		event -- a QKeyEvent
		key -- a Qt keycode

		Keyword arguments:
		modifier -- a Qt keyboard modifier (default=None)

		Returns:
		True on a match, False otherwise
		"""

		return (modifier == None or event.modifiers() == modifier) and \
			event.key() == key

	def keybinding_match(self, event, function):

		"""
		Checks if a QKeyEvent matches a keybdingin

		Arguments:
		event -- a QKeyEvent
		function -- a function name

		Returns:
		True on a match, False otherwise
		"""

		return event.modifiers() == self.keybindings[function][1] and \
			event.key() == self.keybindings[function][0]

	def speller_style(self):

		"""
		Gives the underline style of the spellchecker

		Returns:
		A QTextCharFormat
		"""

		fmt = QtGui.QTextCharFormat()
		fmt.setUnderlineStyle(QtGui.QTextCharFormat.SpellCheckUnderline)
		fmt.setUnderlineColor(QtGui.QColor( \
			self.quiedit._theme.theme["incorrect_color"]))
		return fmt

	def current_word(self, cursor=None):

		"""
		Return the current word

		Keyword arguments:
		cursor -- A QTextCursor or None to get the current cursor
		"""

		if not self.quiedit.speller_enabled:
			return
		if cursor == None:
			cursor = self.textCursor()
		cursor.select(QtGui.QTextCursor.WordUnderCursor)
		try:
			word = unicode(cursor.selectedText()).strip()
		except:
			word = None
		return word

	def check_entire_document(self):

		"""Perform spellchecking on the entire document"""

		if not self.quiedit.speller_enabled:
			return

		# Remove underline for the document
		fmt = QtGui.QTextCharFormat()
		fmt.setFontUnderline(False)
		cursor = self.textCursor()
		cursor.beginEditBlock()
		cursor.select(QtGui.QTextCursor.Document)
		cursor.mergeCharFormat(fmt)

		# Check all words
		fmt = self.speller_style()
		cursor = self.textCursor()
		cursor.movePosition(QtGui.QTextCursor.Start)
		while not cursor.atEnd():
			word = self.current_word(cursor)
			if word == None or word == "":
				cursor.movePosition(QtGui.QTextCursor.NextWord)
				continue
			if len(word) > 2 and not self.speller.check(word):
				cursor.mergeCharFormat(fmt)
			cursor.movePosition(QtGui.QTextCursor.NextWord)
		cursor.endEditBlock()

	def check_locally(self):

		"""Periodically perform spell checking around the cursor"""

		if not self.quiedit.speller_enabled:
			return

		# Remove underline for the current section
		fmt = QtGui.QTextCharFormat()
		fmt.setFontUnderline(False)
		cursor = self.textCursor()
		cursor.beginEditBlock()
		cursor.movePosition(QtGui.QTextCursor.PreviousWord, \
			QtGui.QTextCursor.MoveAnchor, self.quiedit.speller_local_bound)
		cursor.movePosition(QtGui.QTextCursor.NextWord, \
			QtGui.QTextCursor.KeepAnchor, 2 * self.quiedit.speller_local_bound)
		cursor.mergeCharFormat(fmt)

		# Check all words
		cursor = self.textCursor()
		cursor.movePosition(QtGui.QTextCursor.PreviousWord, \
			n=self.quiedit.speller_local_bound)

		for i in range(2 * self.quiedit.speller_local_bound):
			if cursor.atEnd():
				break
			word = self.current_word(cursor)
			if word == None or word == "":
				cursor.movePosition(QtGui.QTextCursor.NextWord)
				continue
			if len(word) > 2 and not self.speller.check(word):
				cursor.mergeCharFormat(self.speller_style())
			cursor.movePosition(QtGui.QTextCursor.NextWord)
		cursor.endEditBlock()
		QtCore.QTimer.singleShot(self.quiedit.speller_local_interval, \
			self.check_locally)

	def check_current_word(self):

		"""Underline the currently selected word if it is incorrect"""

		if not self.quiedit.speller_enabled:
			return

		cursor = self.textCursor()
		cursor.beginEditBlock()
		pos = cursor.position()
		cursor.movePosition(QtGui.QTextCursor.PreviousCharacter, \
			QtGui.QTextCursor.MoveAnchor, 1)
		word = self.current_word(cursor)
		if word != None and len(word) > 2 and not self.speller.check(word):
			fmt = self.speller_style()
			if self.quiedit.speller_suggest:
				self.suggest_alternatives(word)
			cursor.mergeCharFormat(fmt)
		cursor.endEditBlock()

	def suggest_alternatives(self, word=None):

		"""
		Give spelling suggestions

		Keyword arguments:
		word -- the word to suggest or None for the current word
		"""

		if word == None:
			word = self.current_word()
		if word == None:
			self.quiedit.set_status("No suggestions")
		suggestions = self.speller.suggest(word)
		if len(suggestions) > 0:
			self.quiedit.set_status("Did you mean: " + (", ".join(suggestions)))

	def ignore_current_word(self):

		"""Add the currently selected word to the ignore list"""

		word = self.current_word()
		if word == None:
			return
		word = word.lower()
		if word not in self.quiedit.speller_ignore:
			self.quiedit.speller_ignore.append(word)
			self.quiedit.set_status("Remembering '%s'" % word)
			self.check_entire_document()
		else:
			self.quiedit.set_status("Already know '%s'" % word)

	def perform_search(self):

		"""Perform a text search"""

		term = unicode(self.quiedit.search_edit.text())
		if not self.find(term):
			self.moveCursor(QtGui.QTextCursor.Start)
			if not self.find(term):
				self.quiedit.set_status("Text not found")

	def show_stats(self):

		"""Show document statistics"""

		s = unicode(self.toPlainText().toAscii())
		word_count = len(s.split())
		line_count = len(s.split("\n"))
		char_count = len(s)
		self.quiedit.set_status("%d words, %d lines and %d characters" \
			% (word_count, line_count, char_count))

	def set_keybindings(self):

		"""
		Compiles Python code to handle keybindings

		Arguments:
		A string containing the keybindings
		"""

		self.keybindings = {}
		for l in open(self.quiedit.get_resource("keybindings.conf")):
			a = l.split("=")
			if len(a) == 2:
				function = a[0].strip()
				mods = 0
				for key in a[1].strip().split("+"):
					if hasattr(QtCore.Qt, "%sModifier" % key.capitalize()):
						mods = mods | eval("QtCore.Qt.%sModifier" % \
							key.capitalize())
					else:
						try:
							key = eval("QtCore.Qt.Key_%s" % key.capitalize())
						except:
							print \
								"quieditor.set_keybindings(): unkown key in '%s'" \
								% l
				self.keybindings[function] = key, mods
				
	def set_text(self, text):
		
		self.setPlainText(text)
				
	def wheelEvent(self, event):
		
		"""
		Handle mouse scroll events to implement zoom in and out.

		Arguments:
		event	--	A QWheelEvent.
		"""
		
		if event.orientation() == QtCore.Qt.Horizontal or event.modifiers() != \
			QtCore.Qt.ControlModifier:
			super(quieditor, self).wheelEvent(event)
			return
		if event.delta() > 0:
			self.quiedit._theme.theme[u'font_size'] = \
				int(self.quiedit._theme.theme[u'font_size']) + 1
		else:
			self.quiedit._theme.theme[u'font_size'] = max(1, int( \
				self.quiedit._theme.theme[u'font_size']) - 1)
		self.quiedit.set_theme()
			
	def keyPressEvent(self, event):

		"""
		Handle keypress events

		Arguments:
		event -- a QKeyEvent
		"""

		intercept = False # Set to True to disable the regular keyPressEvent
		had_selection = self.textCursor().hasSelection()

		# Check for keybindings if a modifier was pressed
		if event.modifiers() != QtCore.Qt.NoModifier:

			# Quit the program
			if self.keybinding_match(event, "quit"):
				self.quiedit.close()
				intercept = True

			# Open a file
			elif self.keybinding_match(event, "open"):
				self.quiedit.open_file()
				intercept = True

			# Save a file
			elif self.keybinding_match(event, "save"):
				self.quiedit.save_file()
				intercept = True

			# Save a file as
			elif self.keybinding_match(event, "save_as"):
				self.quiedit.save_file(always_ask=True)
				intercept = True

			# New file
			elif self.keybinding_match(event, "new"):
				self.quiedit.new_file()
				intercept = True

			# Toggle find (only in edit mode)
			elif self.keybinding_match(event, "find") and \
				self.quiedit.editor.isVisible():
				if self.quiedit.search_box.isVisible():
					self.quiedit.search_box.hide()
					self.setFocus()
				else:
					self.quiedit.search_box.show()
					self.quiedit.search_edit.setFocus()
				intercept = True

			# Toggle help
			elif self.keybinding_match(event, "help"):
				intercept = True
				if self.quiedit.help.isVisible():
					self.quiedit.show_element("editor")
					self.quiedit.set_status("Resuming")
				else:
					self.quiedit.show_element("help")
					self.quiedit.set_status("Press Control+H to resume editing")

			# Toggle preferences
			elif self.keybinding_match(event, "prefs"):
				intercept = True
				self.quiedit.show_element("prefs")
				self.quiedit.setCursor(QtCore.Qt.ArrowCursor)
				self.quiedit.set_status("Opening preferences")

			# Toggle markdown
			elif self.keybinding_match(event, "preview_markdown"):
				intercept = True
				if self.quiedit._markdown.isVisible():
					self.quiedit.show_element("editor")
					self.quiedit.set_status("Resuming")
				else:
					self.quiedit._markdown.refresh()
					self.quiedit.show_element("markdown")
					self.quiedit.setCursor(QtCore.Qt.ArrowCursor)
					self.quiedit.set_status("Previewing markdown")

			# Toggle fullscreen
			elif self.keybinding_match(event, "fullscreen"):
				if self.quiedit.isFullScreen():
					self.quiedit.showNormal()
					self.quiedit.resize(QtCore.QSize(self.quiedit.width, \
						self.quiedit.height))
				else:
					self.quiedit.showFullScreen()

			# Ignore current word
			elif self.keybinding_match(event, "ignore"):
				self.ignore_current_word()
				intercept = True

			# Suggest alternatives
			elif self.keybinding_match(event, "suggest"):
				self.suggest_alternatives()
				intercept = True

			# Show document statistics
			elif self.keybinding_match(event, "stats"):
				self.show_stats()
				intercept = True

		# Print debugging output to the editor
		if self.quiedit.debug and self.key_match(event, QtCore.Qt.Key_D, \
			QtCore.Qt.ControlModifier):
			print unicode(self.toHtml().toAscii())
			intercept = True

		# A hack to automatically unindent the tab indent on a backspace
		if self.quiedit.auto_indent and (self.key_match(event, \
			QtCore.Qt.Key_Backspace)\
			or self.key_match(event, QtCore.Qt.Key_Left)):

			cursor = self.textCursor()
			cursor.movePosition(QtGui.QTextCursor.Left, \
				QtGui.QTextCursor.KeepAnchor, 1)
			unindent = True
			for i in cursor.selectedText().toLatin1():
				if ord(i) != self.quiedit.ord_indent:
					unindent = False
					break
			if unindent:
				if self.key_match(event, QtCore.Qt.Key_Backspace):
					cursor.removeSelectedText()
				else:
					self.moveCursor(QtGui.QTextCursor.StartOfLine)

		# Process the keypress in the regular way
		if not intercept:
			super(quieditor, self).keyPressEvent(event)

		# A hack to automatically delete the tab indent on a delete
		if self.quiedit.auto_indent and (self.key_match(event, \
			QtCore.Qt.Key_Delete)\
			or self.key_match(event, QtCore.Qt.Key_Right)\
			or self.key_match(event, QtCore.Qt.Key_Down)\
			or self.key_match(event, QtCore.Qt.Key_Up)):

			cursor = self.textCursor()
			cursor.movePosition(QtGui.QTextCursor.Right, \
				QtGui.QTextCursor.KeepAnchor, 1)
			unindent = True
			for i in cursor.selectedText().toLatin1():
				if ord(i) != self.quiedit.ord_indent:
					unindent = False
					break
			if unindent:
				if self.key_match(event, QtCore.Qt.Key_Delete):
					cursor.removeSelectedText()
				else:
					self.moveCursor(QtGui.QTextCursor.NextWord)

		# Optionally start each newline with a tab indent
		if self.quiedit.auto_indent and self.key_match(event, \
			QtCore.Qt.Key_Return):
			#self.insertHtml(self.quiedit.indent_str)
			self.insertPlainText(self.quiedit.str_indent)

		# Optionally do spellchecking
		if self.quiedit.speller_enabled and (had_selection
			or self.key_match(event, QtCore.Qt.Key_Space) \
			or self.key_match(event, QtCore.Qt.Key_Backspace) \
			or self.key_match(event, QtCore.Qt.Key_Delete)):
			QtCore.QTimer.singleShot(0, self.check_current_word)

	def insertFromMimeData(self, mimeData):

		"""
		Reimplementation of the paste functionality to force plain text pasting

		Arguments:
		mimeData - a QMimeData object
		"""

		if mimeData.hasText():
			self.insertPlainText(mimeData.text())
