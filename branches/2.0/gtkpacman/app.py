from os.path import abspath
from gtk import main

from gui import gui

class app:

    def __init__(self, fname, icons):

        self.gui = gui(fname, icons)
        main()
