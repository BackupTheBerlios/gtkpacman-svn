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
#
# The 'capture' function is part of FreeSpeak.
# Freespeak is Copyright 2005 by Italian Python User Group and is released
# uder the term of GPL

from distutils.core import setup, Extension
import os

def capture(cmd): return os.popen(cmd).read().strip()

setup(name="gtkPacman",
      version="1.2",
      description="ArchLinux pacman's pygtk frontend",
      author="Stefano Esposito",
      author_email="ragnarok@email.it",
      url="https://gna.org/projects/gtkpacman",
      packages=['gtkPacman'],
      ext_modules=[
            Extension("trayicon",
                      ["gtkPacman/trayicon/trayicon.c",
                       "gtkPacman/trayicon/trayiconmodule.c",
                       "gtkPacman/trayicon/eggtrayicon.c"],
                      extra_compile_args = capture("pkg-config --cflags gtk+-2.0 pygtk-2.0").split(),
                      extra_link_args = capture("pkg-config --libs gtk+-2.0 pygtk-2.0").split()
                      )
            ],
      scripts=['gtkpacman'],
      data_files=[('../etc/', ['gtkpacman.conf']),
                  ('share/locale/it/LC_MESSAGES',
                   ['share/locale/it/LC_MESSAGES/gtkPacman.mo']),
                  ('share/locale/fr/LC_MESSAGES',
                   ['share/locale/fr/LC_MESSAGES/gtkPacman.mo']),
                  ('share/locale/de/LC_MESSAGES',
                   ['share/locale/de/LC_MESSAGES/gtkPacman.mo']),
                  ('share/locale/sv/LC_MESSAGES',
                   ['share/locale/sv/LC_MESSAGES/gtkPacman.mo']),
                  ('share/gtkpacman', ['share/pixmaps/blank_box.png',
                                       'share/pixmaps/green_box.png',
                                       'share/pixmaps/pacman.png',
                                       'share/pixmaps/red_box.png',
                                       'share/pixmaps/yellow_box.png',
                                       'gtkpacman.glade']),
                  ('../opt/gnome/share/applications',
                   ['share/applications/gnome/gtkpacman.desktop']),
                  ('../opt/kde/share/applications/kde',
                   ['share/applications/kde/gtkpacman.desktop'])])
      
      
      

