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

from PyQt4.QtCore import QRegExp
from PyQt4.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter

class MarkdownHighlighter(QSyntaxHighlighter):

	"""Markdown syntax highligher"""

	def __init__(self, qtextedit):

		"""
		Constructor.

		Arguments:
		qtextedit	--	A QTextEdit object.
		"""

		self.qtextedit = qtextedit
		super(MarkdownHighlighter, self).__init__(qtextedit)

		keywords = [u'TODO', u'NOTE', u'HIGHLIGHT', u'REF']

		rules = [
			# Header 1 strings: # Title
			(ur'^#[^#\n]*', 0, self.format(color= \
				self.qtextedit.quiedit._theme.theme[u'h1_color'], \
				bold=True)),
			# Header 2 strings: ## Title
			(ur'^##[^\n]*', 0, self.format(color= \
				self.qtextedit.quiedit._theme.theme[u'h2_color'], italic=True)),
			# Emphasize: *emphasize*
			(ur'\*(\S[^\*]+\S|[^\*\s]{1,2})\*(?!\w)', 0, self.format(italic=True)),
			# Strong: **strong**
			(ur'\*\*(\S[^\*]+\S|[^\*\s]{1,2})\*\*(?!\w)', 0, self.format(bold=True)),
			# Emphasize: _emphasize_
			(ur'_(\S[^\*\_]+\S|[^\*\_\s]{1,2})_(?!\w)', 0, self.format(italic=True)),
			# Strong: __strong__
			(ur'__(\S[^\*\_]+\S|[^\*\_\s]{1,2})__(?!\w)', 0, self.format(bold=True)),
			# Citation: '@Mathôt2013'
			(ur'@[\w\+]+', 0, self.format(color= \
				self.qtextedit.quiedit._theme.theme[u'citation_color'])),
			# Academic markdown refs: '%Figure', '%Figure::a', 'Figure:a,b'
			(ur'%[\w]+(::[\w,]+)*', 0, self.format(color= \
				self.qtextedit.quiedit._theme.theme[u'ref_color'])),
			# Normal link style: [link](url)
			(ur'\[[^@%\]]+\]\(\S+\)', 0, self.format(color= \
				self.qtextedit.quiedit._theme.theme[u'link_color'])),
			# Shorthand link style: [link]
			(ur'\[[^@%\]]+\]', 0, self.format(color= \
				self.qtextedit.quiedit._theme.theme[u'link_color'])),
			# Direct links: <url>
			(ur'<[^>]+>', 0, self.format(color= \
				self.qtextedit.quiedit._theme.theme[u'link_color'])),
			# Code: indented by a single tab at the start of a sentence
			(ur'^\t.+', 0, self.format(family= \
				self.qtextedit.quiedit._theme.theme[u'code_font'])),
			# Code: `inline style`
			(ur'`[^`]+`', 0, self.format(family= \
				self.qtextedit.quiedit._theme.theme[u'code_font'])),
			# Lists, starting with '- ' or '1. '
			(ur'^(-|\d+\.)\s', 0, self.format(color= \
				self.qtextedit.quiedit._theme.theme[u'list_color'])),
			# Quotations, starting with '> '
			(ur'^>\s.+$', 0, self.format(color= \
				self.qtextedit.quiedit._theme.theme[u'quote_color'])),
			# Academic Markdown YAML blocks
			(ur'^%--', 0, self.format(color= \
				self.qtextedit.quiedit._theme.theme[u'ref_color'])),
			(ur'^--%', 0, self.format(color= \
				self.qtextedit.quiedit._theme.theme[u'ref_color'])),
			(ur'^\s*\w+:', 0, self.format(color= \
				self.qtextedit.quiedit._theme.theme[u'ref_color'])),
			# Inline YAML
			(ur'%--[^\_]*--%', 0, self.format(color= \
				self.qtextedit.quiedit._theme.theme[u'ref_color'])),
			# Highlighted keywords
			(ur'\b(%s)\b' % u'|'.join(keywords), 0, self.format(color= \
				self.qtextedit.quiedit._theme.theme[u'highlight_foreground'], \
				background=self.qtextedit.quiedit._theme.theme[ \
				u'highlight_background'])),
			]

		# Build a QRegExp for each pattern
		self.rules = [(QRegExp(pat), index, fmt)
			for (pat, index, fmt) in rules]

	def format(self, family=None, color=None, background=None, bold=None, \
		italic=None):

		"""
		Creates a QTextCharFormat with the given attributes.

		Keyword arguments:
		family		--	A font family or None. (default=None)
		color		--	A color value or None. (default=None)
		background	--	A backgrund color value or None. (default=None)
		bold		--	True, False, or None. (default=None)
		italic		--	True, False, or None. (default=None)

		Returns:
		A QTextCharFormat.
		"""

		_format = QTextCharFormat()
		if family != None:
			_format.setFontFamily(family)
		if color != None:
			_color = QColor()
			_color.setNamedColor(color)
			_format.setForeground(_color)
		if background != None:
			_background = QColor()
			_background.setNamedColor(background)
			_format.setBackground(_background)
		if bold != None:
			if bold:
				_format.setFontWeight(QFont.Bold)
			else:
				_format.setFontWeight(QFont.Normal)
		if italic != None:
			if italic:
				_format.setFontItalic(True)
			else:
				_format.setFontItalic(False)
		return _format

	def highlightBlock(self, text):

		"""
		Apply syntax highlighting to the given block of text.

		Arguments:
		text		--	The text text block to process.
		"""

		for expression, nth, format in self.rules:
			index = expression.indexIn(text, 0)
			while index >= 0:
				# We actually want the index of the nth match
				index = expression.pos(nth)
				length = expression.cap(nth).length()
				self.setFormat(index, length, format)
				index = expression.indexIn(text, index + length)
		self.setCurrentBlockState(0)
