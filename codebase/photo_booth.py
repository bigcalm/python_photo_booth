#! /usr/bin/env python

# sudo apt-get install python-gst0.10
# sudo apt-get install gstreamer0.10-plugins-good

import sys, os
import pygtk, gtk, gobject
pygtk.require("2.0")
import pygst
pygst.require("0.10")
import gst
import json

from FullscreenToggler import *

class PhotoBooth:
    
    def __init__(self):
        self.settings = self.loadSettings()
        
        self.builder = gtk.Builder()
        self.builder.add_from_file("photo_booth.glade")
        
        # Main Window
        self.windowMain = self.builder.get_object("windowMain")
        self.windowMain.connect("destroy", gtk.main_quit)
        self.windowMain.show()

        self.togglerObject = FullscreenToggler(self.windowMain)
        self.windowMain.connect_object('key-press-event', FullscreenToggler.toggle, self.togglerObject)

        if (self.settings['start_fullscreen']):
            self.windowMain.fullscreen()


        self.windowMainMovieArea = self.builder.get_object("mainView")

        self.buttonLiveView = self.builder.get_object("buttonLiveView")
        self.buttonLiveView.connect("clicked", self.startStopLiveWebcam)

        self.buttonFinished = self.builder.get_object("buttonFinished")
        # self.buttonFinished.connect("clicked", self.showFinised)

        self.buttonInformation = self.builder.get_object("buttonInformation")
        # self.buttonInformation.connect("clicked", self.showInformation)

        self.buttonAdmin = self.builder.get_object("buttonAdmin")
        self.buttonAdmin.connect("clicked", self.showPin)
        
        
        # Pin window
        self.dialogPinEntry = self.builder.get_object("dialogPinEntry")
        
        self.pin = '';
        self.entryPin = self.builder.get_object("entryPin")
        self.buttonKP1 = self.builder.get_object("buttonKP1")
        self.buttonKP2 = self.builder.get_object("buttonKP2")
        self.buttonKP3 = self.builder.get_object("buttonKP3")
        self.buttonKP4 = self.builder.get_object("buttonKP4")
        self.buttonKP5 = self.builder.get_object("buttonKP5")
        self.buttonKP6 = self.builder.get_object("buttonKP6")
        self.buttonKP7 = self.builder.get_object("buttonKP7")
        self.buttonKP8 = self.builder.get_object("buttonKP8")
        self.buttonKP9 = self.builder.get_object("buttonKP9")
        self.buttonKP0 = self.builder.get_object("buttonKP0")
        self.buttonKPClear = self.builder.get_object("buttonKPClear")
        self.buttonKPCancel = self.builder.get_object("buttonKPCancel")
        self.buttonKPOK = self.builder.get_object("buttonKPOK")
        
        self.buttonKP1.connect("clicked", self.pinAddNumber, "1")
        self.buttonKP2.connect("clicked", self.pinAddNumber, "2")
        self.buttonKP3.connect("clicked", self.pinAddNumber, "3")
        self.buttonKP4.connect("clicked", self.pinAddNumber, "4")
        self.buttonKP5.connect("clicked", self.pinAddNumber, "5")
        self.buttonKP6.connect("clicked", self.pinAddNumber, "6")
        self.buttonKP7.connect("clicked", self.pinAddNumber, "7")
        self.buttonKP8.connect("clicked", self.pinAddNumber, "8")
        self.buttonKP9.connect("clicked", self.pinAddNumber, "9")
        self.buttonKP0.connect("clicked", self.pinAddNumber, "0")
        self.buttonKPClear.connect("clicked", self.pinClear)
        self.buttonKPCancel.connect("clicked", self.hideDialogPin)
        self.buttonKPOK.connect("clicked", self.pinSubmit, self.pin)
        
        
        # Admin dialog
        self.dialogAdmin = self.builder.get_object("dialogAdmin")

        self.buttonAdminClose = self.builder.get_object("buttonAdminClose")
        self.buttonAdminClose.connect("clicked", self.hideAdmin)

        # General tab
        self.buttonFullscreen = self.builder.get_object("buttonFullscreen")
        self.buttonFullscreen.connect("clicked", self.enterFullscreen)
        
        self.buttonLeaveFullscreen = self.builder.get_object("buttonLeaveFullscreen")
        self.buttonLeaveFullscreen.connect("clicked", self.leaveFullscreen)
        
        self.buttonQuit = self.builder.get_object("buttonQuit")
        self.buttonQuit.connect("clicked", self.quitApp)


        
        # Set up the gstreamer pipepile
        self.player = gst.parse_launch ("v4l2src device=/dev/video0 !  autovideosink")
        # self.player = gst.parse_launch ("v4l2src ! ffmpegcolorspace ! videoscale ! video/x-raw-yuv,width=320,height=240  ! theoraenc quality=16 ! oggmux")

        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect('message', self.on_message)
        bus.connect('sync-message::element', self.on_sync_message)
    
    def loadSettings(self):
        f = open('settings.json', 'r')
        settings = f.read()
        f.close()
        return json.loads(settings)
    
    def threadsInit(self):
        gtk.gdk.threads_init()
    
    def main(self):
        gtk.main()
    
    def setWindowSize(self, windowObject):
        if self.togglerObject.window_is_fullscreen:
            windowObject.fullscreen()
        else:
            windowObject.unfullscreen()
            
    # Pin functions
    
    def showPin(self, widget, data = None):
        self.dialogPinEntry.show()
        self.setWindowSize(self.dialogPinEntry)
        
    def hideDialogPin(self, widget, data = None):
        self.pin = '';
        self.entryPin.set_text(self.pin)
        self.dialogPinEntry.hide()
    
    def pinAddNumber(self, widget, data = None):
        self.pin = self.pin + data
        self.entryPin.set_text(self.pin)
    
    def pinSubmit(self, widget, data = None):
        if self.pin == self.settings['admin_pin']:
            self.entryPin.set_text('')
            self.pin = ''
            self.dialogPinEntry.hide()
            self.showAdmin(None, None)
    
    def pinClear(self, widget, data = None):
        self.pin = '';
        self.entryPin.set_text(self.pin)
    
    # Webcam functions
    
    def startLiveWebcam(self):
        self.player.set_state(gst.STATE_PLAYING)
        self.buttonLiveView.set_label('Gallery view')
        
    def stopLiveWebcam(self):
        self.player.set_state(gst.STATE_NULL)
        self.buttonLiveView.set_label('Live view')
    
    def startStopLiveWebcam(self, widget, data = None):
        if (self.buttonLiveView.get_label() == 'Gallery view'):
            self.stopLiveWebcam()
        else:
            self.startLiveWebcam()
    
    def on_message(self, bus, message):
        t = message.type
        if t == gst.MESSAGE_EOS:
            self.player.set_state(gst.STATE_NULL)
        elif t == gst.MESSAGE_ERROR:
            err, debug = message.parse_error()
            print "Error: %s" % err, debug
            self.player.set_state(gst.STATE_NULL)

    def on_sync_message(self, bus, message):
        if message.structure is None:
            return
        message_name = message.structure.get_name()
        if message_name == 'prepare-xwindow-id':
            # Assign the viewport
            imagesink = message.src
            imagesink.set_property('force-aspect-ratio', True)
            imagesink.set_xwindow_id(self.windowMainMovieArea.window.xid)
    
    
    
    # Admin dialog functions
    
    def showAdmin(self, widget, data = None):
        self.stopLiveWebcam()
        self.dialogAdmin.show()
        self.setWindowSize(self.dialogAdmin)

    def hideAdmin(self, widget, data = None):
#        self.stopTestWebcam()
        self.dialogAdmin.hide()


    # Admin dialog General tab functions
    
    def enterFullscreen(self, widget, data = None):
        self.windowMain.fullscreen()
        
    def leaveFullscreen(self, widget, data = None):
        self.windowMain.unfullscreen()

    def quitApp(self, widget, data = None):
#        self.stopTestWebcam()
        self.stopLiveWebcam()
        self.dialogAdmin.destroy()
        self.dialogPinEntry.destroy()
        self.windowMain.destroy()
        gtk.main_quit()
    
    
    # Admin dialog Webcam tab functions
    
    def detectVideoDevices(self):
        devDirList = os.listdir('/dev')
        
    
if __name__ == "__main__":
    # Create an application of the PiText class and run the main function
    application = PhotoBooth()
    application.threadsInit()
    application.main()

