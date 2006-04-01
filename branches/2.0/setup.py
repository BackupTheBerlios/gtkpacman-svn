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

from distutils.core import setup

setup(name="gtkpacman",
      version="2.0-alpha1",
      description="Gtk package manager based on pacman",
      author="Stefano Esposito", author_email="ragnarok@email.it",
      url="http://gtkpacman.berlios.de",
      license="GNU General Public License",
      packages=["gtkPacman"],
      scripts=["gtkpacman"],
      data_files=[('share/gtkpacman/icons', ["data/icons/blank_box.png",
                                             "data/icons/green_box.png",
                                             "data/icons/pacman.png",
                                             "data/icons/red_box.png",
                                             "data/icons/yellow_box.png"]),
                  ('share/gtkpacman', ["data/gtkpacman.glade"])
                  ]
      )
