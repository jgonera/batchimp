#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bip.pluginbase import PluginBase
import pygtk
pygtk.require("2.0")
import gtk
import subprocess
import os.path

NAME = "Levels"
TYPE = "change"

class Plugin(PluginBase):
	def __init__(self, tmp_file):
		self.tmp_file = tmp_file
		
		self.builder = gtk.Builder()
		self.builder.add_from_file(os.path.splitext(__file__)[0] + ".xml")
		self.builder.connect_signals(self)

		self.settings_window = self.builder.get_object("settings_window")
		self.black_point_scale = self.builder.get_object("black_point_scale")
		self.white_point_scale = self.builder.get_object("white_point_scale")
		self.gamma_spinbutton = self.builder.get_object("gamma_spinbutton")		
		
		# don't know why it defaults to 0 even though it's set in Glade
		self.white_point_scale.set_value(100)
		self.gamma_spinbutton.set_value(1.0)
	
	def show_settings(self):
		self.settings_window.show()
		
	def close_settings(self, widget, data=None):
		self.settings_window.hide()
		
		return True
		
	def process(self, current_path, original_path):
		command = ['convert', current_path]
		
		black_point = str(self.black_point_scale.get_value())
		white_point = str(self.white_point_scale.get_value())
		gamma = str(self.gamma_spinbutton.get_value())
		
		command.append('-level')
		command.append(black_point + '%,' + white_point + '%,' + gamma)	
		
		command.append('-auto-orient')
		command.append('bmp:' + self.tmp_file)
		
		subprocess.call(command)
			
		return self.tmp_file

