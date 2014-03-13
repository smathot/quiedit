## Overview

%--
toc:
 exclude: [overview]
 mindepth: 2
--%

## About QuiEdit

QuiEdit is a distraction-free, full-screen text editor (a *qui*et *edit*or) focused on writing in [Markdown]. QuiEdit supports theming, Markdown syntax highlighting, and spell checking.

QuiEdit is freely available under the [GNU General Public License v3][gpl]

## Download and installation

The current version is %-- python: "from libquiedit.qtquiedit import qtquiedit; print qtquiedit.version," --%.

### Packages

You can download the latest packages and source code from GitHub:

- <https://github.com/smathot/quiedit/releases>

### Ubuntu PPA

To install QuiEdit from the [Cogsci.nl] repository on Ubuntu/ Linux Mint, type the following commands in a terminal:

	sudo add-apt-repository ppa:smathot/cogscinl
	sudo apt-get update
	sudo apt-get install quiedit

### Other Linux distributions

In other Linux distributions, you can download the latest source code, extract it to a location of your choice and type the following commands in a terminal:

	cd [location where you extracted the source]
	sudo python setup.py install

### Older versions

Older versions can be found here:

- <http://files.cogsci.nl/software/quiedit/>

## Spell checking

For spell checking, QuiEdit uses [Hunspell], the same engine that is used by OpenOffice, LibreOffice, Thunderbird and Firefox. Installing PyHunspell (the Python bindings for hunspell) under Linux is fairly simple. Under Ubuntu you can do this with the following commands (or install from the [Cogsci.nl PPA][ppa] if available for your distribution):

	sudo apt-get install python-dev libhunspell-dev
	wget -O pyhunspell.tar.gz https://github.com/smathot/pyhunspell/tarball/master
	tar -xvf pyhunspell.tar.gz
	cd smathot-pyhunspell-*
	sudo python setup.py install

Unfortunately I haven't been able to get PyHunspell working under Windows.

## Academic Markdown

QuiEdit uses [Markdown] (`.md`), a plain-text format that allows you to write formatted documents that can easily be converted to other formats, such as `.pdf` or `.html`. If available, [Academic Markdown] is used to generate formatted previews. Academic Markdown is an extension of Markdown that includes functionality that is useful when writing academic manuscripts.

## Automatic saving

Modifications are saved __automatically and immediately__ when you exit QuiEdit, when you open another document, or when you start a new document. Use with care!

## Help

In QuiEdit, type Control+H to open the help page, which lists all keybindings.

## Screenshot

%--
figure:
 id: ScreenShotA
 source: http://img.cogsci.nl/uploads/528b91bbdea73.jpg
 caption: |
  A screenshot of QuiEdit.
--%

[markdown]: http://daringfireball.net/projects/markdown/syntax
[gpl]: http://www.gnu.org/copyleft/gpl.html
[archive]: http://files.cogsci.nl/software/quiedit/
[hunspell]: http://hunspell.sourceforge.net/
[academic markdown]: https://github.com/smathot/academicmarkdown
[ppa]: https://launchpad.net/~smathot/+archive/cogscinl
[github]: https://github.com/smathot/quiedit
[win-exe]: http://files.cogsci.nl/software/quiedit/quiedit_0.3.0-win32-1.exe
[win-zip]: http://files.cogsci.nl/software/quiedit/quiedit_0.3.0-win32-1.zip
[cogsci.nl]: www.cogsci.nl/

