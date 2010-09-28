#!/usr/bin/env python
# -*- coding: utf-8 -*-

from batchimpapp.pluginbase import PluginSettingsBase, MagickCommand, \
	SpinButtonField, ColorButtonField, RadioButtonsField

NAME = 'Rotate'
AUTHOR = 'Juliusz Gonera'
__version__ = '0.1'
__api_version__ = '0.1'


class Plugin(PluginSettingsBase):
	def init(self):
		SpinButtonField(self,
			name = 'angle',
			label = 'Angle:',
			value = 0,
			maximum = 360
		)
		
		ColorButtonField(self,
			advanced = True,
			name = 'background_color',
			label = 'Background:'
		)
		RadioButtonsField(self,
			advanced = True,
			name = 'condition',
			label = 'Rotate',
			options = [
				'Always',
				'When width is greater than height',
				'When height is greater than width'
			]
		)
		
	def process(self, current_path, original_path, options):
		command = MagickCommand().append('convert', current_path)
		
		command.append('-background')
		command.append_color(self.settings['background_color'])
		
		degrees = str(self.settings['angle'])
		
		if self.settings['condition'] == 1:
			degrees = degrees + '>'
		elif self.settings['condition'] == 2:
			degrees = degrees + '<'
		
		command.append('-rotate')
		command.append(degrees)
		
		return command.run()

