#!/usr/bin/env python
# -*- coding: utf-8 -*-

from batchimpapp.pluginbase import PluginSettingsBase, MagickCommand, \
	SpinButtonField, ComboBoxField, CheckButtonField

NAME = 'Liquid resize'
AUTHOR = 'Juliusz Gonera'
__version__ = '0.1'
__api_version__ = '0.1'


class Plugin(PluginSettingsBase):
	def init(self):
		SpinButtonField(self,
			name = 'width',
			label = 'Width:',
			value = 100
		)
		SpinButtonField(self,
			name = 'height',
			label = 'Height:',
			value = 100
		)
		ComboBoxField(self,
			same_row = True,
			name = 'unit',
			options = ['px', '%'],
			active_option = 1
		)
		CheckButtonField(self,
			name = 'keep_ratio',
			label = 'Keep aspect _ratio',
			value = False
		)

	def process(self, current_path, original_path, options):
		command = MagickCommand(False).append('convert', current_path)
		
		width = str(self.settings['width'])
		height = str(self.settings['height'])
		
		if self.settings['unit'] == '%':
			geometry = width + '%x' + height + '%'
		else:
			geometry = width + 'x' + height
			
		if not self.settings['keep_ratio']:
			geometry = geometry + '!'
		
		command.append('-liquid-rescale', geometry)
		
		return command.run()

