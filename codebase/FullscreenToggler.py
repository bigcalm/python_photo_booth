#! /usr/bin/env python

import pygtk, gtk, gobject

class FullscreenToggler(object):

    def __init__(self, window, keysym=gtk.keysyms.F11):
        self.window = window
        self.keysym = keysym
        self.window_is_fullscreen = False
        self.window.connect_object('window-state-event',
                                   FullscreenToggler.on_window_state_change,
                                   self)

    def on_window_state_change(self, event):
        self.window_is_fullscreen = bool(
            gtk.gdk.WINDOW_STATE_FULLSCREEN & event.new_window_state)

    def toggle(self, event):
        if event.keyval == self.keysym:
            if self.window_is_fullscreen:
                self.window.unfullscreen()
            else:
                self.window.fullscreen()
