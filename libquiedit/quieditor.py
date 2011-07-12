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

class quieditor(QtGui.QTextEdit):

	"""A fancy text editor"""

	confirm_quit = False

	def __init__(self, parent=None, readonly=False):

		"""
		Constructor
		
		Keyword arguments:
		parent -- the parent widget (default=None)
		readonly -- makes the editor readonly (default=False)
		"""

		super(quieditor, self).__init__(parent)
		self.quiedit = parent
		self.setReadOnly(readonly)
		self.textChanged.connect(self.quiedit.set_unsaved)
		if self.quiedit.speller_enabled:
			self.speller = speller.speller(self.quiedit)
			
	def set_theme(self):

		"""Set the theme"""

		self.document().setDefaultFont(self.quiedit.theme_font())
		self.setStyleSheet("background: %(editor_background)s; color: %(font_color)s; selection-color: %(editor_background)s; selection-background-color: %(font_color)s" % self.quiedit.style)

		# Change the font for the entire document
		fmt = self.currentCharFormat()
		fmt.setFontFamily(self.quiedit.style["font_family"])
		fmt.setFontUnderline(False)
		cursor = self.textCursor()
		cursor.select(QtGui.QTextCursor.Document)
		cursor.mergeCharFormat(fmt)

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

		return	(modifier == None or event.modifiers() == modifier) and event.key() == key

	def speller_style(self):

		"""
		Gives the underline style of the spellchecker

		Returns:
		A QTextCharFormat		
		"""

		fmt = QtGui.QTextCharFormat()
		fmt.setUnderlineStyle(QtGui.QTextCharFormat.SpellCheckUnderline)
		fmt.setUnderlineColor(QtGui.QColor(self.quiedit.style["incorrect_color"]))
		return fmt

	def current_word(self, cursor=None):

		"""
		Return the current word

		Keyword arguments:
		cursor -- A QTextCursor or None to get the current cursor
		"""

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

		# Remove underline for the document
		fmt = self.currentCharFormat()
		fmt.setFontUnderline(False)
		cursor = self.textCursor()
		cursor.select(QtGui.QTextCursor.Document)
		cursor.mergeCharFormat(fmt)

		# Check all words
		fmt = self.speller_style()
		cursor = self.textCursor()
		cursor.movePosition(QtGui.QTextCursor.Start)
		while not cursor.atEnd():
			word = self.current_word(cursor)
			if word == None:
				continue
			if len(word) > 2 and not self.speller.check(word):
				cursor.mergeCharFormat(fmt)
			cursor.movePosition(QtGui.QTextCursor.NextWord)

	def periodic_check(self):

		"""Periodically check the entire document"""

		if self.quiedit.speller_enabled:
				self.check_entire_document()
		QtCore.QTimer.singleShot(self.quiedit.speller_interval, self.periodic_check)

	def check_current_word(self):

		"""Underline the currently selected word if it is incorrect"""

		cursor = self.textCursor()
		pos = cursor.position()
		cursor.movePosition(QtGui.QTextCursor.PreviousCharacter, QtGui.QTextCursor.MoveAnchor, 1)
		word = self.current_word(cursor)
		if word == None or len(word) <= 2 or self.speller.check(word):
			fmt = QtGui.QTextCharFormat()
			fmt.setFontUnderline(False)
			cursor.mergeCharFormat(fmt)
			cursor.movePosition(QtGui.QTextCursor.NextCharacter, QtGui.QTextCursor.KeepAnchor, pos - cursor.position())			
		else:
			fmt = self.speller_style()
			if self.quiedit.speller_suggest:
				self.suggest_alternatives(word)
		cursor.mergeCharFormat(fmt)
		self.set_style(underline=False)

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
		self.quiedit.set_status("%d words, %d lines and %d characters" % (word_count, line_count, char_count))

	def set_style(self, italic=None, bold=None, underline=None, strikeout=None, font_size=None, align=None):

		"""
		Set the current style
		
		Keyword arguments:
		italic -- a boolean or None to leave unchanged (default=None)
		bold -- a boolean or None to leave unchanged (default=None)
		underline -- a boolean or None to leave unchanged (default=None)
		strikeout -- a boolean or None to leave unchanged (default=None)
		align -- a QtCore.Qt alignment
		"""

		fmt = self.currentCharFormat()
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
		self.setCurrentCharFormat(fmt)		

	def keyPressEvent(self, event):

		"""
		Handle keypress events
		
		Arguments:
		event -- a QKeyEvent
		"""

		intercept = False # Set to True to disable the regular keyPressEvent
		had_selection = self.textCursor().hasSelection()

		# Quit the program
		if self.key_match(event, QtCore.Qt.Key_Q, QtCore.Qt.ControlModifier):						
			self.quiedit.close()
			intercept = True

		# Open a file
		if self.key_match(event, QtCore.Qt.Key_O, QtCore.Qt.ControlModifier):						
			self.quiedit.open_file()			
			intercept = True

		# Save a file
		if self.key_match(event, QtCore.Qt.Key_S, QtCore.Qt.ControlModifier):						
			self.quiedit.save_file()			
			intercept = True			

		# Save a file as
		if self.key_match(event, QtCore.Qt.Key_S, QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier):						
			self.quiedit.save_file(always_ask=True)	
			intercept = True

		# Save a file
		if self.key_match(event, QtCore.Qt.Key_N, QtCore.Qt.ControlModifier):
			self.quiedit.new_file()
			intercept = True			

		# Toggle find (only in edit mode)
		if self.key_match(event, QtCore.Qt.Key_F, QtCore.Qt.ControlModifier) and self.quiedit.editor.isVisible():
			if self.quiedit.search_box.isVisible():
				self.quiedit.search_box.hide()
				self.setFocus()
			else:
				self.quiedit.search_box.show()
				self.quiedit.search_edit.setFocus()
			intercept = True			

		# Toggle help
		if self.key_match(event, QtCore.Qt.Key_H, QtCore.Qt.ControlModifier):	
			intercept = True			
			if self.quiedit.help.isVisible():
				self.quiedit.help.hide()
				self.quiedit.prefs.hide()
				self.quiedit.editor.show()
				self.quiedit.set_status("Resuming")
			else:
				self.quiedit.help.setHtml(open(self.quiedit.get_resource("help.html")).read())
				self.quiedit.help.show()
				self.quiedit.prefs.hide()
				self.quiedit.editor.hide()
				self.quiedit.set_status("Press Control+H to resume editing")

		# Toggle preferences
		if self.key_match(event, QtCore.Qt.Key_P, QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier):	
			intercept = True			
			self.quiedit.help.hide()
			self.quiedit.editor.hide()
			self.quiedit.prefs.show()
			self.quiedit.setCursor(QtCore.Qt.ArrowCursor)
			self.quiedit.set_status("Opening preferences")

		# Toggle fullscreen
		if self.key_match(event, QtCore.Qt.Key_F, QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier):
			if self.quiedit.isFullScreen():
				self.quiedit.showNormal()
				self.quiedit.resize(QtCore.QSize(self.quiedit.width, self.quiedit.height))
			else:
				self.quiedit.showFullScreen()

		# Ignore current word
		if self.key_match(event, QtCore.Qt.Key_I, QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier):
			self.ignore_current_word()
			intercept = True				

		# Suggest alternatives
		if self.key_match(event, QtCore.Qt.Key_A, QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier):
			self.suggest_alternatives()
			intercept = True							

		# Toggle italics
		if self.key_match(event, QtCore.Qt.Key_I, QtCore.Qt.ControlModifier):						
			self.set_style(italic=not self.fontItalic())
			intercept = True

		# Toggle bold
		if self.key_match(event, QtCore.Qt.Key_B, QtCore.Qt.ControlModifier):						
			self.set_style(bold=not self.currentCharFormat().fontWeight() == QtGui.QFont.Bold)
			intercept = True		

		# Set center align
		if self.key_match(event, QtCore.Qt.Key_C, QtCore.Qt.AltModifier):						
			self.set_style(align=QtCore.Qt.AlignCenter)
			intercept = True					

		# Set left align
		if self.key_match(event, QtCore.Qt.Key_L, QtCore.Qt.AltModifier):						
			self.set_style(align=QtCore.Qt.AlignLeft)
			intercept = True				

		# Set right align
		if self.key_match(event, QtCore.Qt.Key_R, QtCore.Qt.AltModifier):						
			self.set_style(align=QtCore.Qt.AlignRight)
			intercept = True				

		# Set justify align
		if self.key_match(event, QtCore.Qt.Key_J, QtCore.Qt.AltModifier):						
			self.set_style(align=QtCore.Qt.AlignJustify)
			intercept = True				

		# Set normal text
		if self.key_match(event, QtCore.Qt.Key_0, QtCore.Qt.ControlModifier):						
			self.set_style(font_size=self.quiedit.style["font_size"])
			intercept = True		

		# Set large text
		if self.key_match(event, QtCore.Qt.Key_1, QtCore.Qt.ControlModifier):						
			self.set_style(font_size=self.quiedit.style["l_font_size"])
			intercept = True		

		# Set xl text
		if self.key_match(event, QtCore.Qt.Key_2, QtCore.Qt.ControlModifier):						
			self.set_style(font_size=self.quiedit.style["xl_font_size"])
			intercept = True		

		# Set xxl text
		if self.key_match(event, QtCore.Qt.Key_3, QtCore.Qt.ControlModifier):						
			self.set_style(font_size=self.quiedit.style["xxl_font_size"])
			intercept = True

		# Set small text
		if self.key_match(event, QtCore.Qt.Key_4, QtCore.Qt.ControlModifier):						
			self.set_style(font_size=self.quiedit.style["s_font_size"])
			intercept = True

		# Set xs text
		if self.key_match(event, QtCore.Qt.Key_5, QtCore.Qt.ControlModifier):						
			self.set_style(font_size=self.quiedit.style["xs_font_size"])
			intercept = True

		# Set xxs text
		if self.key_match(event, QtCore.Qt.Key_6, QtCore.Qt.ControlModifier):						
			self.set_style(font_size=self.quiedit.style["xxs_font_size"])
			intercept = True					

		# Show document statistics
		if self.key_match(event, QtCore.Qt.Key_Z, QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier):
			self.show_stats()
			intercept = True								

		# Print debugging output to the editor
		if self.quiedit.debug and self.key_match(event, QtCore.Qt.Key_D, QtCore.Qt.ControlModifier):						
			self.setPlainText(self.toHtml())
			intercept = True					

		# A hack to automatically unindent the 4 spaces indent on a backspace
		if self.quiedit.auto_indent and (self.key_match(event, QtCore.Qt.Key_Backspace)\
			or self.key_match(event, QtCore.Qt.Key_Left)):

			cursor = self.textCursor()
			cursor.movePosition(QtGui.QTextCursor.Left, QtGui.QTextCursor.KeepAnchor, 4)
			unindent = True
			for i in cursor.selectedText().toLatin1():
				if ord(i) != 160:
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

		# A hack to automatically unindent the 4 spaces indent on a backspace
		if self.quiedit.auto_indent and (self.key_match(event, QtCore.Qt.Key_Delete)\
			or self.key_match(event, QtCore.Qt.Key_Right)\
			or self.key_match(event, QtCore.Qt.Key_Down)\
			or self.key_match(event, QtCore.Qt.Key_Up)):
				
			cursor = self.textCursor()
			cursor.movePosition(QtGui.QTextCursor.Right, QtGui.QTextCursor.KeepAnchor, 4)
			unindent = True
			for i in cursor.selectedText().toLatin1():
				if ord(i) != 160:
					unindent = False
					break
			if unindent:
				if self.key_match(event, QtCore.Qt.Key_Delete):
					cursor.removeSelectedText()
				else:
					self.moveCursor(QtGui.QTextCursor.NextWord)					
			

		# Optionally start each newline with a tab indent
		if self.quiedit.auto_indent and self.key_match(event, QtCore.Qt.Key_Return):
			self.insertHtml(self.quiedit.indent_str)

		# Optionally do spellchecking
		if self.quiedit.speller_enabled and (had_selection
			or self.key_match(event, QtCore.Qt.Key_Space) \
			or self.key_match(event, QtCore.Qt.Key_Backspace) \
			or self.key_match(event, QtCore.Qt.Key_Delete)):
			self.check_current_word()
			
