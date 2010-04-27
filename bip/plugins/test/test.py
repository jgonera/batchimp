#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bip_pluginbase import PluginBase
import time

NAME = "Test plugin"
TYPE = "change"

class Plugin(PluginBase):
	def __init__(self, tmp_file):
		print "instancja testowego"
		self.tmp_file = tmp_file
	
	def __del__(self):
		print "kasowanie testowego"
	
	def prepare(self):
		print "preparing"
	
	def show_settings(self):
		print "settings!"
		
	def process(self, current_path, original_path):
		print "processing " + current_path + ", " + original_path
		time.sleep(1)
		return current_path
		
	def finalize(self):
		print "finalizing"
		time.sleep(0.5)
