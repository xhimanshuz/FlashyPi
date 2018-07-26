#!/usr/bin/python3


# ========= TODO LIST ========= #
# FORMAT BUTTON WORKING [X]
# FLASH BUTTON WORKING  [X]
# AUTO DOWNLOAD AND SELECT OS [X]
# BOOTLOADER AUTO INSTALLER [X]
# LOG ENGINE (DISPLAY ERRORS AND MESSAGES) [*]
# PROGRESS DISPLAY  [*]
# AUTOMATIC DOWNLOAD AND INSTALL OS CHOOSING WITH DROPDOWN MENU [*]
# [X] = DONE, [*] = IN DEVELOPMENT

# ========= CONTRIBUTERS ========= #
# Himanshu Rastogi <hi.himanshu14@gmail.com> --> AUTHOR
# ...?


import gi                           # IMPORTING GTK MODULES
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import subprocess                   # CONTROL GNU/LINUX PROCESS
import json                         # JSON API - TO FETCH JSON DATA
import os


# GLOBAL VAIRABLE FOR COLOR
RED = "\033[91m"
WHITE = "\033[00m"
GREEN = "\033[92m"
YELLOW = "\033[93m"


class FlashyPi(Gtk.Window):
    def __init__(self):
        self.dType = 'usb'
        self.drive = '/dev/null'
        self.choice = ''
        self.bootloaderChoice = ''
        self.ejectDrive = True

        Gtk.Window.__init__(self)
        self.importObject()

    def importObject(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file('gui/main.glade')

        self.mainWin = self.builder.get_object('mainWin')
        self.mainWin.connect('delete-event', Gtk.main_quit)

        self.radioSelectImage = self.builder.get_object('radioSelectImage')
        self.radioSelectImage.connect(
            'toggled', self.onChoiceToggled, 'selectImage')
        self.radioSelectManager = self.builder.get_object('radioSelectManager')
        self.radioSelectManager.connect(
            'toggled', self.onChoiceToggled, 'selectBootloader')

        self.radioNoobs = self.builder.get_object('radioNoobs')
        self.radioBerryboot = self.builder.get_object('radioBerryboot')
        self.radioPinn = self.builder.get_object('radioPinn')

        self.radioNoobs.connect('toggled', self.bootloaderToggled, 'noobs')
        self.radioBerryboot.connect(
            'toggled', self.bootloaderToggled, 'berryboot')
        self.radioPinn.connect('toggled', self.bootloaderToggled, 'pinn')

        self.fileChooer = self.builder.get_object('fileChooser')
        self.fileChooer.connect('selection-changed', self.onSelectFile)
        self.fileReloadButton = self.builder.get_object('fileReloadButton')
        # self.fileReloadButton.connect('clicked', self.fileReloadButtonClicked)

        self.driveComboBox = self.builder.get_object('driveComboBox')
        self.driveComboBox.connect('changed', self.onChange)
        self.listStoreCreate()
        self.addToListStore()
        self.driveComboBox.set_active(0)
        self.deviceReloadButton = self.builder.get_object('deviceReloadButton')

        self.driveLabelEntry = self.builder.get_object('driveLabelEntry')
        self.driveLabelEntry.set_text("FlashyPi")

        self.formatButton = self.builder.get_object('formatButton')
        self.otherButton = self.builder.get_object('otherButton')

        self.loading = self.builder.get_object('loading')

        self.ejectCheckBox = self.builder.get_object('ejectCheckBox')
        self.ejectCheckBox.connect('toggled', self.ejectCheckBoxToggled)
        self.ejectCheckBox.set_active(self.ejectDrive)

        self.textView = self.builder.get_object('textView')
        self.textBuffer = Gtk.TextBuffer()
        self.textView.set_buffer(self.textBuffer)

        self.about = self.builder.get_object('about')
        self.about.connect('response', self.aboutClose)

        signal = {
            'fileReloadButtonClicked':  self.fileReloadButtonClicked,
            'formatButtonClicked':      self.formatButtonClicked,
            'flashButtonClicked':       self.flashButtonClicked,
            'aboutButtonClicked':       self.aboutButtonClicked,
            'deviceReloadButtonClicked': self.deviceReloadButtonClicked
        }

        self.builder.connect_signals(signal)

    def aboutClose(self, action, param):        # CLOSING ABOUT DIALOG
        action.hide()

    def aboutButtonClicked(self, widget,):      # CALLED WHEN ABOUT BUTTON CLICKED
        self.about.run()
        print(self.mountpoint())

    # RELOAD CURRENT USB DRIVE LIST
    def deviceReloadButtonClicked(self, widget):
        self.addToListStore()

    # CALLED WHEN BOOTLOADER RADIO BUTTON SELECTED
    def bootloaderToggled(self, widget, bootloader):
        self.bootloaderChoice = bootloader
        self.msg(self.bootloaderChoice, " Selected")

    # CALLED WHEN FLASH METHOD RADIO BUTTON SELECTED
    def onChoiceToggled(self, widget, choice):
        self.choice = choice

    # IS USED TO CREATE LIST OF AVAILABLE USB DRIVE
    def listStoreCreate(self):
        self.listStore = Gtk.ListStore(str, str)
        self.cellRenderer = Gtk.CellRendererText()
        self.driveComboBox.set_model(self.listStore)
        self.driveComboBox.pack_start(self.cellRenderer, 0)
        self.driveComboBox.add_attribute(self.cellRenderer, 'text', 1)

    # IS USED TO ADD AVAILABLE USB DRIVE TO LIST
    def addToListStore(self):
        data = self.getFromJson()
        self.listStore.clear()
        self.listStore.append(('null', '--- Please Select Device ---'))
        self.driveComboBox.set_active(0)
        for i in data:
            if i['tran'] == self.dType:
                tuple = (i['name'], '/dev/' + str(i['name'] +
                                                  " | " + i['model'] + " | " + i['size']))
                print(tuple)
                self.listStore.append(tuple)

    def getFromJson(self):                         # FETCH JSON DATA FOR DRIVE DETAIL
        self.jsonData = json.loads(
            subprocess.getstatusoutput('lsblk -I 8 -n -J -O')[1])
        self.jsonData = self.jsonData['blockdevices']
        # print(jsonData)
        return self.jsonData

    # EMPTY SELECTED FILE FROM FILE CHOOSER
    def fileReloadButtonClicked(self, widget):
        self.fileChooer.set_filename('None')

    def onChange(self, widget):                     # CALLED WHEN YOU SELECT USB DRIVE
        if widget.get_active_iter() is not None:
            # SETTING DRIVE LOCATION eg: '/dev/sdb1'
            self.drive = '/dev/' + \
                self.driveComboBox.get_model(
                )[self.driveComboBox.get_active_iter()][0]
        print(self.drive, 'mountpoint', self.mountpoint())

    def ejectCheckBoxToggled(self, widget):  # EJECT DRIVE AFTER FORMATTING
        if self.ejectCheckBox.get_active():
            print('Auto Eject is ON')
        else:
            print('Auto Eject is OFF')

    def mountpoint(self):
        mp = " ".join(subprocess.getstatusoutput(
            'lsblk -I 8 -l -n | grep {}'.format(self.drive.replace('/dev/', '')+'1'))[1].split()[6:])
        return mp

    # THIS FUCTION IS USED TO FORMAT SELECTED DRIVE
    def formatDrive(self):
        print('Formatting ', self.drive+'1')
        flag = subprocess.getstatusoutput(
            'sudo umount {}*'.format(self.drive))  # UNMOUNTING SELECTED DRIVE
        if flag[0]:
            # ERROR IF THERE IS PROBLEM IN UNMOUNTING
            self.msg('Error in Unmounting\n', flag[1])
        else:
            self.msg('Successfully Unmounted')
            # RENAMING DRIVE LABEL
        flag = subprocess.getstatusoutput('sudo fatlabel {} {}'.format(
            self.drive+'1', self.driveLabelEntry.get_text()))   #
        if flag[0]:
            self.msg('Error in Renaming ', flag[1])
        else:
            self.msg('Successfully Renamed ', flag[1])
        flag = subprocess.getstatusoutput(
            'sudo parted {} mklabel msdos mkpart primary fat32 1MiB 100% set 1 boot on -s'.format(self.drive))
        if flag[0]:
            print('Error in Partitioning: {}'.format(self.drive), flag[1])
        else:
            self.loading.pulse()
            self.msg('Successfully Partitoned..!\n', flag[1])
            flag = subprocess.getstatusoutput(
                'sudo mkfs.vfat {}'.format((self.drive+'1')))
            if flag[0]:
                self.msg('Error in Formating Drive: {}'.format(
                    (self.drive+'1')), flag[1])
                return False
            else:
                self.loading.pulse()
                self.msg('Successfully Formated Drive: {}'.format(
                    self.drive+'1'), flag[1])
                self.mountDrive()
                if self.ejectCheckBox.get_active():
                    self.driveEject()
                return True

    def driveEject(self):
        if subprocess.call(['sudo', 'eject', '{}'.format(self.drive+'1')]):
            self.msg('Error in Ejecting!')
            self.notify("Error in Ejecting!")
        else:
            self.msg('Successfully Ejected')
            self.notify("Successfully Ejected")

    def mountDrive(self):                                   # MOUNTING THE SELECT DRIVE
        subprocess.getstatusoutput('sudo mkdir /media/usb')
        flag = subprocess.getstatusoutput(
            'mount {} /media/usb'.format(self.drive+'1'))
        if flag[0]:
            print('Error in mounting {}'.format(self.drive+'1'), flag[1])
            print('New Mountpoint: ', self.mountpoint())
            return False
        else:
            self.msg('New Mountpoint: ', self.mountpoint())
            return True

    # DOWNLOAD AND INSTALL PINN BOOTLOADER IN USB DRIVE OR SD CARD AUTOMATICALLY
    def pinnInstaller(self):
        print('PINN installer')
        self.lmsg('Wait for 5 mins and make some coffee')
        flag = subprocess.call(
            "wget -L https://sourceforge.net/projects/pinn/files/latest/download -O /tmp/pinn.zip".split())
        if flag:
            self.msg('Error in Downloading PINN Installer')
            # return True
        else:
            self.msg(
                'PINN Installer successfully downloaded now preparing to install for Noobs in USB Drive')
            if self.formatDrive():
                flag = subprocess.getstatusoutput(
                    'sudo unzip -o /tmp/pinn.zip -d {}'.format(self.mountpoint()))
                if flag[0]:
                    self.msg('Error in installing PINN')
                else:
                    self.msg('PINN Successfully Installed in {}'.format(
                        self.mountpoint()), flag[1])
                    self.notify("PINN Successfully Install, Please Eject it")
            else:
                print('Error in formating Drive')
                # return True

    # DOWNLOAD AND INSTALL NOOBS BOOTLOADER IN USB DRIVE OR SD CARD AUTOMATICALLY
    def noobsInstaller(self):
        print('noobs installer')
        flag = subprocess.call(
            "wget -L https://downloads.raspberrypi.org/NOOBS_lite_latest -O /tmp/noobs.zip".split())
        if flag:
            self.msg('Error in Downloading Noobs Installer')
            # return True
        else:
            self.msg(
                'Noobs Installer successfully downloaded now preparing to install for Noobs in USB Drive')
            if self.formatDrive():
                flag = subprocess.getstatusoutput(
                    'sudo unzip -o /tmp/noobs.zip -d {}'.format(self.mountpoint()))
                if flag[0]:
                    self.msg('Error in installing Noobs')
                else:
                    self.msg('Noobs Successfully Installed in {}'.format(
                        self.mountpoint()), flag[1])
            else:
                print('Error in formating Drive')
                # return True

    # DOWNLOAD AND INSTALL BERRYBOOT BOOTLOADER IN USB DRIVE AND SD CARD AUTOMATICALLY
    def berrybootInstaller(self):
        self.lmsg('Wait for 5 mins and make some coffee')
        flag = subprocess.getstatusoutput(
            "wget -L http://downloads.sourceforge.net/project/berryboot/berryboot-20180405-pi0-pi1-pi2-pi3.zip -O /tmp/berryboot.zip")
        if flag[0]:
            self.msg('Error in Downloading BerryBoot Installer', flag[1])
            self.lmsg('Error in Downloading BerryBoot Installer')
            # return True
        else:
            self.msg(
                'Berry Installer successfully downloaded now preparing to install for Noobs in USB Drive')
            self.lmsg(
                'Berry Installer successfully downloaded now preparing to install for Noobs in USB Drive')
            if self.formatDrive():
                flag = subprocess.getstatusoutput(
                    'sudo unzip -o /tmp/berryboot.zip -d {}'.format(self.mountpoint()))
                if flag[0]:
                    self.msg('Error in installing Berryboot')
                    print(flag[1])
                else:
                    self.msg('Berryboot Successfully Installed in {}'.format(
                        self.mountpoint()), flag[1])
            else:
                print('Error in formating Drive')
                # return True

    # THIS FUCTION CALL WHEN FORMAT BUTTON CLICKED
    def formatButtonClicked(self, widget):
        self.loading.pulse()
        self.formatDrive()

    def flashImage(self):
        file = self.fileChooer.get_filename()
        print(file, self.drive+"1")
        if(self.formatDrive()):
            flag = subprocess.getstatusoutput(
                "dd bs=4M if='{}' of={} conv=fsync".format(str(file), self.drive+'1'))
            if flag[0]:
                self.msg('Error in flashing {}'.format(flag[1]))
            else:
                self.msg("Successfully Flashed!, {}".format(flag[1]))

    # THIS FUNCTION CALL WHEN FLASH BUTTON CLICKED
    def flashButtonClicked(self, widget):
        if self.choice == 'selectImage':        # CHECK RADIO BUTTON THEN ACT ACCORDINGLY
            self.flashImage()
        elif self.choice == 'selectBootloader':
            if self.bootloaderChoice == 'noobs':
                self.noobsInstaller()
            elif self.bootloaderChoice == 'pinn':
                self.pinnInstaller()
            elif self.bootloaderChoice == 'berryboot':
                self.berrybootInstaller()
            else:
                self.msg('Please select Bootloader')
        else:
            self.msg('Please Choose Method')

    # MESSAGES PASSING IN LOG ENGINE - Little fix todo for text[0]

    def msg(self, *text):
        if(isinstance(text, (tuple))):
            string = " "
            for t in text:
                string += t
                string += " "
            text = string
        # print(text)
        self.textBuffer.insert(
            self.textBuffer.get_start_iter(), str(text)+'\n', -1)

    def notify(self, msg):
        print(subprocess.call(["notify-send", msg]))

    # MESSAGES PASSING ON LOADING BAR
    def lmsg(self, text):
        print('loading text ', text)
        self.loading.pulse()
        self.loading.set_text(text)
        self.loading.set_show_text(True)

    def run(self):
        # THIS FUNCTION IS CALLED WHEN YOU RUN THIS PROGRAM
        self.notify("FlashyPi Started")
        self.mainWin.show_all()
        Gtk.main()
        pass

    def onSelectFile(self, widget):
        string = widget.get_filename()
        self.msg(str(string) + " Selected")

 # RUN THE ENGINE
if not os.getuid():  # CHECKING ROOT USER
    print(YELLOW)
    win = FlashyPi()
    win.run()
else:
    print("{}[!] {}flashypi {}must run as {}root".format(
        RED, GREEN, YELLOW, RED))
    print("{}try {}sudo ./flashypi.py".format(YELLOW, WHITE))
