#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk, os

from gtkPacman.Gui import *

fname = os.path.abspath('gtkpacman.glade')
icons = { "green"  : os.path.abspath('share/pixmaps/green_box.png'),
          "red"    : os.path.abspath('share/pixmaps/red_box.png'),
          "yellow" : os.path.abspath('share/pixmaps/yellow_box.png'),
          "pacman" : os.path.abspath('share/pixmaps/pacman.png') }

if __name__ == "__main__":

    app = gui(fname, icons)
    app.run()

