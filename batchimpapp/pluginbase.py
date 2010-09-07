#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygtk
pygtk.require("2.0")
import gtk

class PluginError(Exception):
	def __init__(self, message):
		self.message = message

class PluginBase(object):
	def __init__(self, tmp_file):
		pass
	
	def prepare(self):
		return True
	
	def show_settings(self):
		dialog = gtk.MessageDialog(
			None,
			gtk.DIALOG_MODAL,
			gtk.MESSAGE_INFO,
			gtk.BUTTONS_OK,
			"This operation does not need any configuration.")
			
		dialog.run()
		dialog.destroy()

	def process(self, current_path, original_path):
		raise NotImplementedError("Need to define 'process' method!")
	
	def finalize(self):
		return True
