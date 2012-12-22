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
from libquiedit import speller

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

	def set_theme(self):

		"""Set the theme"""

		self.document().setDefaultFont(self.quiedit.theme_font())
		self.setStyleSheet("""
			background: %(editor_background)s;
			color: %(font_color)s;
			selection-color: %(editor_background)s;
			selection-background-color: %(font_color)s;
			""" % self.quiedit.style)
		# Change the font for the entire document
		fmt = QtGui.QTextCharFormat()
		fmt.setFontFamily(self.quiedit.style["font_family"])
		fmt.setFontUnderline(False)
		cursor = self.textCursor()
		cursor.select(QtGui.QTextCursor.Document)
		cursor.mergeCharFormat(fmt)
		if self.quiedit.style["scrollbar"] == "off":
			self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
		self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

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

		return	event.modifiers() == self.keybindings[function][1] and \
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
			self.quiedit.style["incorrect_color"]))
		return fmt

	def anchor_style(self, anchor_name):

		"""
		Gives the style for an anchor

		Arguments:
		anchor_name -- the name of the anchor

		Returns:
		A QTextCharFormat
		"""

		fmt = QtGui.QTextCharFormat()
		fmt.setAnchor(True)
		fmt.setAnchorNames([anchor_name])
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
			word = str(cursor.selectedText()).strip()
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
			self.set_style(underline=False)
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

		term = str(self.quiedit.search_edit.text())
		if not self.find(term):
			self.moveCursor(QtGui.QTextCursor.Start)
			if not self.find(term):
				self.quiedit.set_status("Text not found")

	def show_stats(self):

		"""Show document statistics"""

		s = str(self.toPlainText().toAscii())
		word_count = len(s.split())
		line_count = len(s.split("\n"))
		char_count = len(s)
		self.quiedit.set_status("%d words, %d lines and %d characters" \
			% (word_count, line_count, char_count))

	def add_anchor(self):

		"""Add a section break to the document"""

		cursor = self.textCursor()
		cursor.select(QtGui.QTextCursor.LineUnderCursor)
		anchor = ""
		for c in str(cursor.selectedText().toAscii()):
			if c.isalnum():
				anchor += c
		cursor.select(QtGui.QTextCursor.WordUnderCursor)
		cursor.mergeCharFormat(self.anchor_style(anchor))
		self.insertHtml("<BR />")
		self.quiedit.set_status("New anchor: %s" % anchor)

	def set_style(self, italic=None, bold=None, underline=None, \
		strikeout=None, font_size=None, align=None):

		"""
		Set the current style

		Keyword arguments:
		italic -- a boolean or None to leave unchanged (default=None)
		bold -- a boolean or None to leave unchanged (default=None)
		underline -- a boolean or None to leave unchanged (default=None)
		strikeout -- a boolean or None to leave unchanged (default=None)
		align -- a QtCore.Qt alignment
		"""

		fmt = QtGui.QTextCharFormat()
		if italic != None:
			fmt.setFontItalic(italic)
		if bold != None:
			if bold:
				fmt.setFontWeight(QtGui.QFont.Bold)
			else:
				fmt.setFontWeight(QtGui.QFont.Normal)
		if underline != None:
			fmt.setFontUnderline(underline)
		if font_size != None:
			fmt.setFontPointSize(int(font_size))
		if align != None:
			self.setAlignment(align)
		self.textCursor().mergeCharFormat(fmt)

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

			# Save a file in simple format
			elif self.keybinding_match(event, "save_as_simple_format"):
				self.quiedit.save_file(fmt='simple', always_ask=True)
				intercept = True

			# Save a file in plaintext format
			elif self.keybinding_match(event, "save_as_plaintext_format"):
				self.quiedit.save_file(fmt='plain', always_ask=True)
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
					help = open(self.quiedit.get_resource("help.html")).read()
					help = help.replace("__keybindings__", open( \
						self.quiedit.get_resource( \
						"keybindings.conf")).read().replace("\n", "<BR />"))
					self.quiedit.help.setHtml(help)
					self.quiedit.help.set_theme()
					self.quiedit.show_element("help")
					self.quiedit.set_status("Press Control+H to resume editing")

			# Toggle preferences
			elif self.keybinding_match(event, "prefs"):
				intercept = True
				self.quiedit.show_element("prefs")
				self.quiedit.setCursor(QtCore.Qt.ArrowCursor)
				self.quiedit.set_status("Opening preferences")

			# Toggle navigator
			elif self.keybinding_match(event, "navigator"):
				intercept = True
				if self.quiedit.navigator.isVisible():
					self.quiedit.show_element("editor")
					self.quiedit.set_status("Resuming")
				else:
					self.quiedit.navigator.refresh()
					self.quiedit.show_element("navigator")
					self.quiedit.set_status("Opening navigator")

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

			# Add anchor
			elif self.keybinding_match(event, "anchor"):
				self.add_anchor()
				intercept = True

			# Toggle italics
			elif self.keybinding_match(event, "italic"):
				self.set_style(italic=not self.fontItalic())
				intercept = True

			# Toggle bold
			elif self.keybinding_match(event, "bold"):
				self.set_style(bold=not self.currentCharFormat().fontWeight() \
					== QtGui.QFont.Bold)
				intercept = True

			# Set center align
			elif self.keybinding_match(event, "align_center"):
				self.set_style(align=QtCore.Qt.AlignCenter)
				intercept = True

			# Set left align
			elif self.keybinding_match(event, "align_left"):
				self.set_style(align=QtCore.Qt.AlignLeft)
				intercept = True

			# Set right align
			elif self.keybinding_match(event, "align_right"):
				self.set_style(align=QtCore.Qt.AlignRight)
				intercept = True

			# Set justify align
			elif self.keybinding_match(event, "align_justify"):
				self.set_style(align=QtCore.Qt.AlignJustify)
				intercept = True

			# Set normal text
			elif self.keybinding_match(event, "size_normal"):
				self.set_style(font_size=self.quiedit.style["font_size"])
				intercept = True

			# Set large text
			elif self.keybinding_match(event, "size_l"):
				self.set_style(font_size=self.quiedit.style["l_font_size"])
				intercept = True

			# Set xl text
			elif self.keybinding_match(event, "size_xl"):
				self.set_style(font_size=self.quiedit.style["xl_font_size"])
				intercept = True

			# Set xxl text
			elif self.keybinding_match(event, "size_xxl"):
				self.set_style(font_size=self.quiedit.style["xxl_font_size"])
				intercept = True

			# Set small text
			elif self.keybinding_match(event, "size_s"):
				self.set_style(font_size=self.quiedit.style["s_font_size"])
				intercept = True

			# Set xs text
			elif self.keybinding_match(event, "size_xs"):
				self.set_style(font_size=self.quiedit.style["xs_font_size"])
				intercept = True

			# Set xxs text
			elif self.keybinding_match(event, "size_xxs"):
				self.set_style(font_size=self.quiedit.style["xxs_font_size"])
				intercept = True

			# Show document statistics
			elif self.keybinding_match(event, "stats"):
				self.show_stats()
				intercept = True

		# Print debugging output to the editor
		if self.quiedit.debug and self.key_match(event, QtCore.Qt.Key_D, \
			QtCore.Qt.ControlModifier):
			print str(self.toHtml().toAscii())
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

