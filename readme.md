Overview
--------

- [About QuiEdit](#about)
- [Download and installation](#download)
- [Spell checking](#spell-checking)
- [File formats](#file-formats)
- [Themes](#themes)
- [Keybindings](#keybindings)

About QuiEdit {#about}
-------------

QuiEdit is a distraction-free, full-screen text editor (a **qui**et **edit**or). I initially wrote it for personal use, to write blog posts and such. It supports theming, basic text formatting, [Markdown][] syntax, and spell checking.

<object width="640" height="480"> <param name="flashvars" value="offsite=true&lang=en-us&page_show_url=%2Fphotos%2Fcogsci%2Fsets%2F72157632308320281%2Fshow%2F&page_show_back_url=%2Fphotos%2Fcogsci%2Fsets%2F72157632308320281%2F&set_id=72157632308320281&jump_to="></param> <param name="movie" value="http://www.flickr.com/apps/slideshow/show.swf?v=122138"></param> <param name="allowFullScreen" value="true"></param><embed type="application/x-shockwave-flash" src="http://www.flickr.com/apps/slideshow/show.swf?v=122138" allowFullScreen="true" flashvars="offsite=true&lang=en-us&page_show_url=%2Fphotos%2Fcogsci%2Fsets%2F72157632308320281%2Fshow%2F&page_show_back_url=%2Fphotos%2Fcogsci%2Fsets%2F72157632308320281%2F&set_id=72157632308320281&jump_to=" width="640" height="480"></embed></object>

QuiEdit is freely available under the [GNU General Public License v3][gpl]

Download and installation {#download}
-------------------------

The current version is 0.23. For older versions, see [here][archive].

- [Download Windows installer (.exe)][win-exe]
- [Download Windows portable (.zip)][win-zip]
- [Ubuntu/ Linux mint repository][ppa]
- [Source code and development][github]

To install QuiEdit from the Cogsci.nl repository on Ubuntu/ Linux Mint, type the following commands in a terminal:

	sudo add-apt-repository ppa:smathot/cogscinl
	sudo apt-get update
	sudo apt-get install quiedit

In other Linux distributions, you can download the latest source code, extract it to a location of your choice and type the following commands in a terminal:

	cd [location where you extracted the source]
	sudo python setup.py install

Spell checking {#spell-checking}
--------------

For spell checking, QuiEdit uses [Hunspell][], the same engine that is used by OpenOffice, LibreOffice, Thunderbird and Firefox. Installing PyHunspell (the Python bindings for hunspell) under Linux is fairly simple. Under Ubuntu you can do this with the following commands (or install from the [Cogsci.nl PPA][ppa] if available for your distribution):

	sudo apt-get install python-dev libhunspell-dev
	wget -O pyhunspell.tar.gz https://github.com/smathot/pyhunspell/tarball/master
	tar -xvf pyhunspell.tar.gz 
	cd smathot-pyhunspell-*
	sudo python setup.py install

Unfortunately I haven't been able to get PyHunspell working under Windows.

File formats and Markdown syntax {#file-formats}
--------------------------------

QuiEdit saves files in `.html` format or in plain text, as `.txt`, `.md`, or `.markdown` files (which differ only in extension). If you use `.html`, you can format your text as you are probably used to, by pressing `control+i` for italics etc. If you use plain text, you can add formatting using [Markdown][] syntax, which offers more precise control. You can preview your Markdown document by pressing `control+shift+m`, and export the Markdown source to HTML by pressing (by default) `control+shift+e`. QuiEdit uses [python-markdown][] to perform the parsing.

Themes and keybindings {#themes}
----------------------

Examples of theme files and the file `keybinding.conf` can be found in the QuiEdit `resources` folder. They should be fairly self-explanatory. You can select a theme using the preferences Window (by default `Control+Shift+P`).

On Windows, resources are located in the resources subfolder of the QuiEdit folder:

	[path to quiedit]\resources

On Linux, resources are in one of the following folders

	/home/[username]/.quiedit/resources
	/usr/share/quiedit/resources

[markdown]: http://daringfireball.net/projects/markdown/syntax
[gpl]: http://www.gnu.org/copyleft/gpl.html
[archive]: http://files.cogsci.nl/software/quiedit/
[hunspell]: http://hunspell.sourceforge.net/
[python-markdown]: http://packages.python.org/Markdown/
[ppa]: https://launchpad.net/~smathot/+archive/cogscinl
[github]: https://github.com/smathot/quiedit
[win-exe]: http://files.cogsci.nl/software/quiedit/quiedit_0.23-win32-1.exe
[win-zip]: http://files.cogsci.nl/software/quiedit/quiedit_0.23-win32-1.zip