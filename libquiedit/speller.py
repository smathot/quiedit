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

import sys
import os
import os.path

class speller:
	
	"""A basic spelling checker, currently wraps around pyhunspell"""

	def __init__(self, quiedit):

		"""
		Constructor
		
		Arguments:
		quiedit -- a qtquiedit instance
		"""

		self.quiedit = quiedit
		_dic = os.path.join(self.quiedit.hunspell_path, self.quiedit.hunspell_dict) + ".dic"
		_aff = os.path.join(self.quiedit.hunspell_path, self.quiedit.hunspell_dict) + ".aff"
		try:
			import hunspell
			self.hunspell = hunspell.HunSpell(_dic, _aff)
		except:
			if self.quiedit.debug:
				print "libquiedit.speller.__init__(): failed to load hunspell"
			self.hunspell = None

	def check(self, word):

		"""
		Checks if a word is spelled correctly

		Returns:
		True if correct, False otherwise
		"""

		if self.hunspell == None:
			return True
		return self.hunspell.spell(word) or word.lower() in self.quiedit.speller_ignore

	def suggest(self, word):

		"""
		Suggest alternatives to a word

		Returns:
		A list of suggestions
		"""

		if self.hunspell == None:
			return ["No suggestions"]
		return self.hunspell.suggest(word)[:self.quiedit.speller_max_suggest]

def locate_hunspell_path():

	"""
	Find the hunspell path

	Returns:
	The path to the hunspell dictionaries
	"""

	if os.name == "posix":
		return "/usr/share/hunspell"
	else:
		return "resources"