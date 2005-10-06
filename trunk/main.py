#!/usr/bin/env python
# This file is part of gtkPacman.

# gtkPacman is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# gtkPacman is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with gtkPacman; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
# gtkPacman is copyright (C)2005 by Stefano Esposito

import pygtk
pygtk.require('2.0')
import gtk
import thread
from gtkPacman import Gui

import locale
import gettext
locale.setlocale(locale.LC_ALL, '')
gtk.glade.bindtextdomain('gtkPacman', 'share/locale')
gtk.glade.textdomain('gtkPacman')
gettext.install('gtkPacman', 'share/locale', unicode=1)

icons = {"green" : "share/pixmaps/green_box.png", 
	 "red"   : "share/pixmaps/red_box.png",
         "yellow": "share/pixmaps/yellow_box.png", 
	 "blank" : "share/pixmaps/blank_box.png",
         "pacman": "share/pixmaps/pacman.png" }

gtk.threads_init()

gtk.threads_enter()
my_app = Gui.gui("gtkpacman.glade", "gtkpacman.conf", icons)
my_app.run()
gtk.threads_leave()
