#!/usr/bin/env python
# -*- coding: utf-8 -*-

from batchimpapp.pluginbase import PluginSettingsBase, MagickCommand, \
	ScaleField, SpinButtonField

NAME = 'Levels'
AUTHOR = 'Juliusz Gonera'
__version__ = '0.1'
__api_version__ = '0.1'


class Plugin(PluginSettingsBase):
	def init(self):
		ScaleField(self,
			name = 'black_point',
			label = 'Black point (%):',
			value = 0,
			maximum = 100
		)
		ScaleField(self,
			name = 'white_point',
			label = 'White point (%):',
			value = 100,
			maximum = 100
		)
		SpinButtonField(self,
			name = 'gamma',
			label = 'Gamma:',
			value = 1.0,
			digits = 2,
			minimum = 0.01,
			maximum = 10,
			step_increment = 0.01,
			page_increment = 0.1,
			climb_rate = 0.1
		)
		
	def process(self, current_path, original_path, options):
		command = MagickCommand().append('convert', current_path)
		
		black_point = str(self.settings['black_point'])
		white_point = str(self.settings['white_point'])
		gamma = str(self.settings['gamma'])
		
		command.append('-level')
		if command.gm:
			command.append(black_point + ',' + gamma + ',' + white_point + '%')
		else:
			command.append(black_point + ',' + white_point + '%,' + gamma)
		
		return command.run()

