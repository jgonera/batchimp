#!/usr/bin/env python
# -*- coding: utf-8 -*-

from batchimpapp.pluginbase import PluginBase
import pygtk
pygtk.require("2.0")
import gtk
import subprocess

NAME = "Mirror"
TYPE = "change"

class Plugin(PluginBase):
	def __init__(self, tmp_file):
		self.tmp_file = tmp_file
		
	def process(self, current_path, original_path):
		command = ['convert', current_path]
		
		command.append('-auto-orient')
		command.append('-flop')
		
		command.append('bmp:' + self.tmp_file)
		
		subprocess.call(command)
			
		return self.tmp_file

