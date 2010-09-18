#!/usr/bin/env python
# -*- coding: utf-8 -*-

from batchimpapp.pluginbase import PluginSettingsBase, MagickCommand, \
	SpinButtonField, CheckButtonField, ComboBoxField

NAME = 'Resize'
AUTHOR = 'Juliusz Gonera'
__version__ = '0.1'
__api_version__ = '0.1'


class Plugin(PluginSettingsBase):
	def init(self):
		# Main settings
		SpinButtonField(self,
			name = 'width',
			label = 'Width:',
			value = 800
		)
		SpinButtonField(self,
			name = 'height',
			label = 'Height:',
			value = 600
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
			name = 'fastest_method',
			label = 'Use the _fastest method (ignores filter setting)',
			value = False
		)
		ComboBoxField(self,
			advanced = True,
			name = 'filter',
			label = 'Filter:',
			options = [
				'Auto',
				'Point',
				'Box',
				'Triangle',
				'Hermite',
				'Hanning',
				'Hamming',
				'Blackman',
				'Gaussian',
				'Quadratic',
				'Cubic',
				'Catrom',
				'Mitchell',
				'Lanczos',
				'Bessel',
				'Sinc'
			]
		)
	
	def process(self, current_path, original_path, options):
		command = MagickCommand().append('convert')
		
		width = str(self.settings['width'])
		height = str(self.settings['height'])
		
		if self.settings['unit'] == '%':
			geometry = width + '%x' + height + '%'
		else:
			size = width + 'x' + height
			command.append('-size')
			command.append(size)
			geometry = size
			
		command.append('-')
		
		if not self.settings['keep_ratio']:
			geometry = geometry + '!'
		
		if self.settings['fastest_method']:
			command.append('-scale')
		else:
			command.append('-resize')
		command.append(geometry)
		
		if self.settings['filter'] != 'Auto':
			command.append('-filter')
			command.append(self.settings['filter'])
		
		command.append('bmp:-')
		
		return command.run(current_path)

