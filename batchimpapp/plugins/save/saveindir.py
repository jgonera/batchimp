#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path

import pygtk
pygtk.require("2.0")
import gtk

from batchimpapp.pluginbase import PluginSettingsBase, MagickCommand, \
FileChooserButtonField, EntryField, LabelField

NAME = 'Save in a directory'
AUTHOR = 'Juliusz Gonera'
__version__ = '0.1'
__api_version__ = '0.1'

class Plugin(PluginSettingsBase):
	def init(self):
		FileChooserButtonField(self,
			name = 'directory',
			label = 'Directory:',
			title = 'Select a directory',
			action = FileChooserButtonField.SELECT_FOLDER
		)
		EntryField(self,
			name = 'file_name',
			label = 'File name:',
			value = 'modified_%f'
		)
		LabelField(self,
			left = 1,
			width = 2,
			label = '''Wildcards:
%f - original file (equal to %n.%e)
%n - original file name
%e - original file extension'''
		)
		
	def process(self, current_path, original_path, options):
		file_name = self.settings['file_name']
		original_file_name = os.path.basename(original_path)
		(original_basename, original_ext) = os.path.splitext(original_file_name)
		original_ext = original_ext[1:]
		
		file_name = file_name.replace('%f', original_file_name)
		file_name = file_name.replace('%n', original_basename)
		file_name = file_name.replace('%e', original_ext)
		
		file_path = os.path.join(self.settings['directory'], file_name)
		
		MagickCommand('convert', current_path, file_path).run()
		
		return current_path

