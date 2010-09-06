#!/usr/bin/env python
# -*- coding: utf-8 -*-

from batchimpapp.pluginbase import PluginBase
import pygtk
pygtk.require("2.0")
import gtk
import subprocess
import os.path

NAME = "Save in a directory"
TYPE = "save"

class Plugin(PluginBase):
	def __init__(self, tmp_file):
		self.builder = gtk.Builder()
		self.builder.add_from_file(os.path.splitext(__file__)[0] + ".xml")
		self.builder.connect_signals(self)

		self.settings_window = self.builder.get_object("settings_window")
		self.directory_chooser = self.builder.get_object("directory_chooser")
		self.filename_entry = self.builder.get_object("filename_entry")
	
	def show_settings(self):
		self.settings_window.show()
		
	def close_settings(self, widget, data=None):
		self.settings_window.hide()
		return True
		
	def process(self, current_path, original_path):
		file_name = self.filename_entry.get_text()
		original_file_name = os.path.basename(original_path)
		(original_basename, original_ext) = os.path.splitext(original_file_name)
		original_ext = original_ext[1:]
		
		file_name = file_name.replace("%f", original_file_name)
		file_name = file_name.replace("%n", original_basename)
		file_name = file_name.replace("%e", original_ext)
		
		file_path = self.directory_chooser.get_current_folder() + "/" + file_name
		subprocess.call(('convert', current_path, file_path))
		
		return current_path

