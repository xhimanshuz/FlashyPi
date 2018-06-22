import gi
gi.require_version('Gtk','3.0')
from gi.repository import Gtk
import subprocess
import json

class FlashyPi(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self)
        self.importObject()

    def importObject(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file('gui/main.glade')

        self.mainWin = self.builder.get_object('mainWin')
        self.mainWin.connect('delete-event',Gtk.main_quit)
        

    def run(self):
        self.mainWin.show_all()
        Gtk.main()
        pass

win = FlashyPi()
win.run()