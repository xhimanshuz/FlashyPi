#!/usr/bin/python3


# ========= TODO LIST ========= #
# FORMAT BUTTON WORKING
# FLASH BUTTON WORKING
# AUTO DOWNLOAD AND SELECT OS
# BOOTLOADER AUTO INSTALLER
# LOG ENGINE (DISPLAY ERRORS AND MESSAGES)
# PROGRESS DISPLAY

# ========= CONTRIBUTERS ========= #
# Himanshu Rastogi <hi.himanshu14@gmail.com> --> AUTHOR
# ...?




import gi
gi.require_version('Gtk','3.0')
from gi.repository import Gtk
import subprocess
import json

class FlashyPi(Gtk.Window):
    def __init__(self):
        #VARIABLE
        self.drive = '/dev/null'


        Gtk.Window.__init__(self)
        self.importObject()

    def importObject(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file('gui/main.glade')

        self.mainWin = self.builder.get_object('mainWin')
        self.mainWin.connect('delete-event',Gtk.main_quit)

        self.fileChooer = self.builder.get_object('fileChooser')
        self.fileReloadButton = self.builder.get_object('fileReloadButton')
        # self.fileReloadButton.connect('clicked', self.fileReloadButtonClicked)

        self.driveComboBox = self.builder.get_object('driveComboBox')
        self.listStoreCreate()
        self.driveComboBox.set_model(self.listStore)
        self.driveComboBox.pack_start(self.cellRenderer, 0)
        self.driveComboBox.add_attribute(self.cellRenderer, 'text', 1)
        self.addToListStore()
        self.driveComboBox.connect('changed', self.onChange)
        self.driveComboBox.set_active(0)

        # signal = {
        #     'fileReloadButtonClicked',self.fileReloadButtonClicked
        # }

        # self.builder.connect_signals(signal)

    def listStoreCreate(self):
        self.listStore = Gtk.ListStore(str, str)
        self.cellRenderer = Gtk.CellRendererText()

    def addToListStore(self):
        data = self.getFromJson()
        self.listStore.append(('null','--- Please Select Device ---'))
        for i in data:
            if i['tran'] == 'sata':
                tuple = (i['name'], '/dev/' + str(i['name'] + " | " + i['model'] + " | " + i['size']))
                print(tuple)
                self.listStore.append(tuple)

    def getFromJson(self):
        jsonData = json.loads(subprocess.getstatusoutput('lsblk -I 8 -d -n -J -O')[1])
        jsonData = jsonData['blockdevices']
        # print(jsonData)
        return jsonData

    def fileReloadButtonClicked(self, widget):
        self.fileChooer.set_filename('None')

    def onChange(self, widget):
        self.drive = '/dev/' + self.driveComboBox.get_model()[self.driveComboBox.get_active_iter()][0]
        print(self.drive)

    def run(self):
        self.mainWin.show_all()
        Gtk.main()
        pass

win = FlashyPi()
win.run()