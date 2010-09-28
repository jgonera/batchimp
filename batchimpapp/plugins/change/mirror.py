#!/usr/bin/env python
# -*- coding: utf-8 -*-

from batchimpapp.pluginbase import PluginBase, MagickCommand

NAME = 'Mirror'
AUTHOR = 'Juliusz Gonera'
__version__ = '0.1'
__api_version__ = '0.1'


class Plugin(PluginBase):
	def process(self, current_path, original_path, options):
		return MagickCommand().append(
			'convert',
			current_path,
			'-flop'
		).run()

