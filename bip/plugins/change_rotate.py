#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bip.pluginbase import PluginBase
import pygtk
pygtk.require("2.0")
import gtk
import subprocess
import os.path

NAME = "Rotate"
TYPE = "change"

MAX_COLOR_VALUE = 65535

class Plugin(PluginBase):
	def __init__(self, tmp_file):
		self.tmp_file = tmp_file
		
		self.builder = gtk.Builder()
		self.builder.add_from_file(os.path.splitext(__file__)[0] + ".xml")
		self.builder.connect_signals(self)

		self.settings_window = self.builder.get_object("settings_window")
		self.angle_spinbutton = self.builder.get_object("angle_spinbutton")
		self.always_radiobutton = self.builder.get_object("always_radiobutton")
		self.width_radiobutton = self.builder.get_object("width_radiobutton")
		self.height_radiobutton = self.builder.get_object("height_radiobutton")
		self.background_colorbutton = self.builder.get_object("background_colorbutton")
		
		# don't know why it defaults to 0 even though it's set in Glade
		self.background_colorbutton.set_alpha(MAX_COLOR_VALUE)
			
	def show_settings(self):
		self.settings_window.show()
		
	def close_settings(self, widget, data=None):
		self.settings_window.hide()

		return True
		
	def process(self, current_path, original_path):
		command = ['convert', current_path]
		
		color = self.background_colorbutton.get_color()
		red = str(color.red*255/MAX_COLOR_VALUE)
		green = str(color.green*255/MAX_COLOR_VALUE)
		blue = str(color.blue*255/MAX_COLOR_VALUE)
		alpha = str(self.background_colorbutton.get_alpha()*255/MAX_COLOR_VALUE)
		
		command.append('-background')
		command.append('rgba(' + red + ',' + green + ',' + blue + ',' + alpha + ')')
		
		degrees = str(self.angle_spinbutton.get_value_as_int())
		
		if self.width_radiobutton.get_active():
			degrees = degrees + '>'
		elif self.height_radiobutton.get_active():
			degrees = degrees + '<'
		
		command.append('-rotate')
		command.append(degrees)
		
		command.append('-auto-orient')
		command.append('bmp:' + self.tmp_file)
		
		subprocess.call(command)
			
		return self.tmp_file

