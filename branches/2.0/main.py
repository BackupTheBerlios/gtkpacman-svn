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
# gtkPacman is copyright (C)2005-2006 by Stefano Esposito


def get_fname_and_icons():

    from os.path import exists, abspath, join

    path = "/usr/share/gtkpacman/"
    if not exists(path):
        path = abspath("data/")

    icons = {}
    fname = join(path, "gtkpacman.glade")
    icons["red"] = join(path, "icons/red_box.png")
    icons["yellow"] = join(path, "icons/yellow_box.png")
    icons["green"] = join(path, "icons/green_box.png")
    icons["pacman"] = join(path, "icons/pacman.png")
    

    return fname, icons

def make_icons(icons):
    from gtk.gdk import pixbuf_new_from_file
    from gtk import IconSet, IconFactory
    
    for icon_name in icons.keys():
        icon = pixbuf_new_from_file(icons[icon_name])
        icon_set = IconSet(icon)
        icon_factory = IconFactory()
        icon_factory.add(icon_name, icon_set)
        icon_factory.add_default()
        continue

if __name__ == "__main__":

    from gtk import main
    from gtkpacman import gui, database
    
    
    database = database()
    
    fname, icons = get_fname_and_icons()
    make_icons(icons)
    
    gui = gui(fname, database)

    main()
