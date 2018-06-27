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



from sys import argv
import gi
gi.require_version('Gtk','3.0')
from gi.repository import Gtk
import subprocess
import json

class FlashyPi(Gtk.Window):
    def __init__(self):
        self.dType = 'usb'
        # if self.dType is None:
        #     self.dType = 'usb'
        #VARIABLE
        self.drive = '/dev/null'
        self.choice = ''
        self.bootloaderChoice = ''

        Gtk.Window.__init__(self)
        self.importObject()

    def importObject(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file('gui/main.glade')

        self.mainWin = self.builder.get_object('mainWin')
        self.mainWin.connect('delete-event',Gtk.main_quit)

        self.radioSelectOS = self.builder.get_object('radioSelectOS')
        self.radioSelectOS.connect('toggled',self.onChoiceToggled, 'selectOS')
        self.radioSelectImage = self.builder.get_object('radioSelectImage')
        self.radioSelectImage.connect('toggled',self.onChoiceToggled, 'selectImage')
        self.radioSelectManager = self.builder.get_object('radioSelectManager')
        self.radioSelectManager.connect('toggled', self.onChoiceToggled, 'selectBootloader')


        self.radioNoobs = self.builder.get_object('radioNoobs')
        self.radioBerryboot = self.builder.get_object('radioBerryboot')
        self.radioPinns = self.builder.get_object('radioPinns')

        self.radioNoobs.connect('toggled',self.bootloaderToggled, 'noobs')
        self.radioBerryboot.connect('toggled',self.bootloaderToggled, 'berryboot')
        self.radioPinns.connect('toggled',self.bootloaderToggled, 'pinns')
        

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

        self.formatButton = self.builder.get_object('formatButton')
        self.otherButton = self.builder.get_object('otherButton')
        
        self.loading = self.builder.get_object('loading')

        self.textView = self.builder.get_object('textView')
        self.textBuffer = Gtk.TextBuffer()
        self.textView.set_buffer(self.textBuffer)

        signal = {
            'fileReloadButtonClicked':self.fileReloadButtonClicked,
            'formatButtonClicked':self.formatButtonClicked,
            'flashButtonClicked':self.flashButtonClicked,
            'otherButtonClicked':self.otherButtonClicked
        }

        self.builder.connect_signals(signal)


    def bootloaderToggled(self, widget, bootloader):
        self.bootloaderChoice = bootloader
        self.msg(self.bootloaderChoice, " Selected")

    def onChoiceToggled(self, widget, choice):
        self.choice = choice

    def listStoreCreate(self):
        self.listStore = Gtk.ListStore(str, str)
        self.cellRenderer = Gtk.CellRendererText()

    def addToListStore(self):
        data = self.getFromJson()
        self.listStore.append(('null','--- Please Select Device ---'))
        for i in data:
            if i['tran'] == self.dType:
                tuple = (i['name'], '/dev/' + str(i['name'] + " | " + i['model'] + " | " + i['size']))
                print(tuple)
                self.listStore.append(tuple)

    def getFromJson(self):
        self.jsonData = json.loads(subprocess.getstatusoutput('lsblk -I 8 -n -J -O')[1])
        self.jsonData = self.jsonData['blockdevices']
        # print(jsonData)
        return self.jsonData

    def fileReloadButtonClicked(self, widget):
        self.fileChooer.set_filename('None')

    def onChange(self, widget):
        self.drive = '/dev/' + self.driveComboBox.get_model()[self.driveComboBox.get_active_iter()][0]  #SETTING DRIVE LOCATION eg: '/dev/sdb1'
        print(self.drive,'mountpoint',self.mountpoint())

    def mountpoint(self):
        mp = " ".join(subprocess.getstatusoutput('lsblk -I 8 -l -n | grep {}'.format(self.drive.replace('/dev/','')+'1'))[1].split()[6:]) 
        return mp

    def formatDrive(self):
        print('Formatting ',self.drive+'1')
        flag = subprocess.getstatusoutput('sudo umount {}*'.format(self.drive))
        if flag[0]:
            self.msg('Error in Unmounting\n', flag[1])
        else:
            self.msg('Successfully Unmounted')
        flag = subprocess.getstatusoutput('sudo parted {} mklabel msdos mkpart primary fat32 1MiB 100% set 1 boot on -s'.format(self.drive))
        if flag[0]:
            print('Error in Partitioning: {}'.format(self.drive), flag[1])
        else:
            self.loading.pulse()
            print('Successfully Partitoned..!\n', flag[1])
            flag = subprocess.getstatusoutput('sudo mkfs.vfat {}'.format((self.drive+'1')))
            if flag[0]:
                print('Error in Formating Drive: {}'.format((self.drive+'1')), flag[1])
                return False
            else:
                self.loading.pulse()
                print('Successfully Formated Drive: {}'.format(self.drive+'1'), flag[1])
                if self.mountDrive():
                    return True
                else:
                    return False

    def mountDrive(self):
        subprocess.getstatusoutput('sudo mkdir /media/usb')
        flag = subprocess.getstatusoutput('mount {} /media/usb'.format(self.drive+'1'))
        if flag[0]:
            print('Error in mounting {}'.format(self.drive+'1'), flag[1])
            print('New Mountpoint: ',self.mountpoint())
            return False
        else:
            print('New Mountpoint: ',self.mountpoint())
            return True

    def noobsInstaller(self):
        print('noobs installer')
        # flag = subprocess.call('wget https://downloads.raspberrypi.org/NOOBS_lite_latest -O /tmp/noobs.zip -s'.split())
        # if flag:
        if 0:
            self.msg('Error in Downloading Noobs Installer')
            # return True
        else:
            self.msg('Noobs Installer successfully downloaded now preparing to install for Noobs in USB Drive')
            if self.formatDrive():
                flag = subprocess.getstatusoutput('sudo unzip -o /tmp/noobs.zip -d {}'.format(self.mountpoint()))
                if flag[0]:
                    self.msg('Error in installing Noobs')
                else:
                    self.msg('Noobs Successfully Installed in {}'.format(self.mountpoint()), flag[1])
            else:
                print('Error in formating Drive')
                # return True        

    def berrybootInstaller(self):
        pass
        

    def formatButtonClicked(self, widget):
        self.loading.pulse()
        self.formatDrive()

    def flashButtonClicked(self, widget):
        if self.choice == 'selectImage':
            print('Image')
        elif self.choice == 'selectOS':
            print('SelectOS')
        elif self.choice == 'selectBootloader':
            if self.bootloaderChoice == 'noobs':
                self.noobsInstaller()
            elif self.bootloaderChoice == 'pinns':
                print('Pinns')
            elif self.bootloaderChoice == 'berryboot':
                print('berryboot')
            else:
                self.msg('Please select Bootloader')
        else:
            self.msg('Please Choose Method')

    def otherButtonClicked(self, widget,):
        # self.textBuffer.insert(self.textBuffer.get_end_iter(), "AS saod D", -1)
        self.loading.pulse()
        print(self.mountpoint())

    def msg(self, *text):
        # print(text)
        self.textBuffer.insert(self.textBuffer.get_start_iter(), str(text)+'\n', -1)

    def run(self):
        self.mainWin.show_all()
        Gtk.main()
        pass


# if len(argv)>0:
#     argv = argv[1]
# else:
#     agrv = None

# print(len(argv))
win = FlashyPi()
win.run()



#sudo parted /dev/{} mklabel msdos mkpart primary fat32 1MiB 100% set 1 boot on

# sudo mkfs.vfat /dev/sdb1