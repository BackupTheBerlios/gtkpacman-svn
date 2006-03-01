#!/usr/bin/env python

from os.path import abspath
from gtkpacman import app

if __name__ == "__main__":

    icons = {"green" : "data/pixmaps/green_box.png", 
             "red"   : "data/pixmaps/red_box.png",
             "yellow": "data/pixmaps/yellow_box.png", 
             "blank" : "data/pixmaps/blank_box.png",
             "pacman": "data/pixmaps/pacman.png" }
    fname = abspath("data/gtkpacman.glade")
    app = app(fname, icons)
