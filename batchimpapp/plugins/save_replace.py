#!/usr/bin/env python
# -*- coding: utf-8 -*-

from batchimpapp.pluginbase import PluginBase
import subprocess

NAME = "Replace original files"
TYPE = "save"

class Plugin(PluginBase):
	def process(self, current_path, original_path):
		subprocess.call(('convert', current_path, original_path))
		return current_path

