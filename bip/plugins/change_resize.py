#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bip.pluginbase import PluginBase
import pygtk
pygtk.require("2.0")
import gtk
import subprocess
import os.path

NAME = "Resize"
TYPE = "change"

class Plugin(PluginBase):
	def __init__(self, tmp_file):
		self.tmp_file = tmp_file
		
		self.builder = gtk.Builder()
		self.builder.add_from_file(os.path.splitext(__file__)[0] + ".xml")
		self.builder.connect_signals(self)

		self.settings_window = self.builder.get_object("settings_window")
		self.width_spinbutton = self.builder.get_object("width_spinbutton")
		self.height_spinbutton = self.builder.get_object("height_spinbutton")
		self.unit_combobox = self.builder.get_object("unit_combobox")
		self.keep_ratio_checkbutton = self.builder.get_object("keep_ratio_checkbutton")
		self.fastest_algorithm_checkbutton = self.builder.get_object("fastest_algorithm_checkbutton")
		self.filter_combobox = self.builder.get_object("filter_combobox")
		
		# don't know why it defaults to 0 even though it's set in Glade
		self.width_spinbutton.set_value(800)
		self.height_spinbutton.set_value(600)
	
	def show_settings(self):
		self.settings_window.show()
		
	def close_settings(self, widget, data=None):
		self.settings_window.hide()

		return True
		
	def process(self, current_path, original_path):
		command = ['convert']
		
		width = str(self.width_spinbutton.get_value_as_int())
		height = str(self.height_spinbutton.get_value_as_int())
		
		if self.unit_combobox.get_active_text() == '%':
			geometry = width + '%x' + height + '%'
		else:
			size = width + 'x' + height
			command.append('-size')
			command.append(size)
			geometry = size
			
		command.append(current_path)
		
		if not self.keep_ratio_checkbutton.get_active():
			geometry = geometry + '!'
		
		if self.fastest_algorithm_checkbutton.get_active():
			command.append('-scale')
		else:
			command.append('-resize')
		command.append(geometry)
		
		filter_name = self.filter_combobox.get_active_text()
		
		if filter_name != 'Auto':
			command.append('-filter')
			command.append(filter_name)
		
		command.append('-auto-orient')
		command.append('bmp:' + self.tmp_file)
		
		subprocess.call(command)
			
		return self.tmp_file

