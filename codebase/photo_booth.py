#! /usr/bin/env python

# sudo apt-get install python-gst0.10
# sudo apt-get install gstreamer0.10-plugins-good

import sys, os
import pygtk, gtk, gobject
pygtk.require("2.0")
import pygst
pygst.require("0.10")
import gst

class PhotoBooth:
    
    def __init__(self):
        self.builder = gtk.Builder()
        self.builder.add_from_file("photo_booth.glade")
        
        # Main Window
        self.windowMain = self.builder.get_object("windowMain")
        self.windowMain.connect("destroy", gtk.main_quit)
        self.windowMain.show()

        self.windowMainMovieArea = self.builder.get_object("mainView")

        self.buttonLiveView = self.builder.get_object("buttonLiveView")
        self.buttonLiveView.connect("clicked", self.startWebcam)

        self.buttonFinished = self.builder.get_object("buttonFinished")
        # self.buttonFinished.connect("clicked", self.showFinised)

        self.buttonInformation = self.builder.get_object("buttonInformation")
        # self.buttonInformation.connect("clicked", self.showInformation)

        self.buttonAdmin = self.builder.get_object("buttonAdmin")
        self.buttonAdmin.connect("clicked", self.showPin)
        
        
        # Pin window
        self.windowPin = self.builder.get_object("windowPin")
        
        self.pin = '';
        self.entryPin = self.builder.get_object("entryPin")
        self.buttonPin1 = self.builder.get_object("buttonPin1")
        self.buttonPin2 = self.builder.get_object("buttonPin2")
        self.buttonPin3 = self.builder.get_object("buttonPin3")
        self.buttonPin4 = self.builder.get_object("buttonPin4")
        self.buttonPin5 = self.builder.get_object("buttonPin5")
        self.buttonPin6 = self.builder.get_object("buttonPin6")
        self.buttonPin7 = self.builder.get_object("buttonPin7")
        self.buttonPin8 = self.builder.get_object("buttonPin8")
        self.buttonPin9 = self.builder.get_object("buttonPin9")
        self.buttonPin0 = self.builder.get_object("buttonPin0")
        self.buttonPinStar = self.builder.get_object("buttonPinStar")
        self.buttonPinHash = self.builder.get_object("buttonPinHash")
        
        self.buttonPin1.connect("clicked", self.pinAddNumber, "1")
        self.buttonPin2.connect("clicked", self.pinAddNumber, "2")
        self.buttonPin3.connect("clicked", self.pinAddNumber, "3")
        self.buttonPin4.connect("clicked", self.pinAddNumber, "4")
        self.buttonPin5.connect("clicked", self.pinAddNumber, "5")
        self.buttonPin6.connect("clicked", self.pinAddNumber, "6")
        self.buttonPin7.connect("clicked", self.pinAddNumber, "7")
        self.buttonPin8.connect("clicked", self.pinAddNumber, "8")
        self.buttonPin9.connect("clicked", self.pinAddNumber, "9")
        self.buttonPin0.connect("clicked", self.pinAddNumber, "0")
        self.buttonPinStar.connect("clicked", self.pinSubmit, self.pin)
        self.buttonPinHash.connect("clicked", self.pinClear, self.pin)
        
        # Admin dialog
        self.dialogAdmin = self.builder.get_object("dialogAdmin")
        
        self.buttonFullscreen = self.builder.get_object("buttonFullscreen")
        # self.buttonFullscreen.connect("clicked", self.fullscreen)
        
        self.buttonLeaveFullscreen = self.builder.get_object("buttonLeaveFullscreen")
        # self.buttonLeaveFullscreen.connect("clicked", self.leaveFullscreen)
        
        self.buttonCancel = self.builder.get_object("buttonCancel")
        # self.buttonCancel.connect("clicked", self.hideAdmin)

        self.buttonQuit = self.builder.get_object("buttonQuit")
        # self.buttonQuit.connect("clicked", self.quitApp)
        
        
        # Set up the gstreamer pipepile
        self.player = gst.parse_launch ("v4l2src device=/dev/video0 !  autovideosink")
        # self.player = gst.parse_launch ("v4l2src ! ffmpegcolorspace ! videoscale ! video/x-raw-yuv,width=320,height=240  ! theoraenc quality=16 ! oggmux")

        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect('message', self.on_message)
        bus.connect('sync-message::element', self.on_sync_message)
    
    def threadsInit(self):
        gtk.gdk.threads_init()
    
    def main(self):
        gtk.main()
    
    # Pin functions
    
    def showPin(self, widget, data = None):
        self.windowPin.show()
    
    def pinAddNumber(self, widget, data = None):
        self.pin = self.pin + data
        self.entryPin.set_text(self.pin)
    
    def pinSubmit(self, widget, data = None):
        if self.pin == '123':
            self.showAdmin(None, None)
        else:
            print "%r" % self.pin
    
    def pinClear(self, widget, data = None):
        self.pin = '';
        self.entryPin.set_text(self.pin)
    
    # Webcam functions
    
    def startWebcam(self, widget, data = None):
        self.player.set_state(gst.STATE_PLAYING)
    
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
        self.dialogAdmin.show()
        adminResult = self.dialogAdmin.run()

    def hideAdmin(self, widget, data = None):
        self.dialogAdmin.hide()

    def fullscreen(self, widget, data = None):
        self.windowMain.fullscreen()
        
    def leaveFullscreen(self, widget, data = None):
        self.windowMain.unfullscreen()

    def quitApp(self, widget, data = None):
        self.dialogAdmin.destroy()
        self.windowMain.destroy()
        gtk.main_quit
    
if __name__ == "__main__":
    # Create an application of the PiText class and run the main function
    application = PhotoBooth()
    application.threadsInit()
    application.main()

