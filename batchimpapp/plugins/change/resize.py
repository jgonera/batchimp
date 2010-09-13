#!/usr/bin/env python
# -*- coding: utf-8 -*-

from batchimpapp.pluginbase import PluginBaseSettings, SpinButtonField, CheckButtonField, ComboBoxField
import subprocess

NAME = "Resize"
__author__ = 'Juliusz Gonera'
__version__ = '0.1'

class Plugin(PluginBaseSettings):
	def init(self):
		# Main settings
		SpinButtonField(self,
			name = 'width',
			label = 'Width:',
			value = 800,
			integer = True
		)
		SpinButtonField(self,
			name = 'height',
			label = 'Height:',
			value = 600,
			integer = True
		)
		ComboBoxField(self,
			same_row = True,
			name = 'unit',
			options = ['px', '%']
		)
		CheckButtonField(self,
			name = 'keep_ratio',
			label = 'Keep aspect _ratio',
			value = True
		)
		
		# Advanced settings
		CheckButtonField(self,
			advanced = True,
			name = 'fastest_algorithm',
			label = 'Use the _fastest algorithm (ignores filter setting)',
			value = False
		)
		ComboBoxField(self,
			advanced = True,
			name = 'filter',
			label = 'Filter:',
			options = ['anana', 'uuu']
		)
	
	def process(self, current_path, original_path):
		print self.settings['width']
	
		command = ['convert']
		
		width = str(self.width())
		height = str(self.height())
		
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

