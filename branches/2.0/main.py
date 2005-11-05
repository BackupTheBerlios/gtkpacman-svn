#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk, os

from gtkPacman.Gui import *

fname = os.path.abspath('gtkpacman.glade')

if __name__ == "__main__":

    app = gui(fname)
    app.run()

