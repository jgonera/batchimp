#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygtk
pygtk.require("2.0")
import gtk
import gobject
import os
import subprocess
from threading import Thread
import time

from batchimpapp.pluginbase import PluginError

class ProcessThread(Thread):
	def __init__(self, progress_window, main_window):
		Thread.__init__(self)
		self.progress_window = progress_window
		self.main_window = main_window
		self.running = True
	
	def run(self):
		start_time = time.time()
		current_step = 1.0 / len(self.main_window.operations)
		# +1 for finalizing
		total_step = current_step / (len(self.main_window.files_store) + 1)
		
		self.progress_window.total_progressbar.set_fraction(0.0)
		
		for plugin_id, plugin in self.main_window.operations.items():
			try:
				plugin.prepare()
			except PluginError as e:
				gobject.idle_add(self.progress_window.show_error, e.message)
				self.running = False
		
		for item in self.main_window.files_store:
			self.progress_window.current_progressbar.set_text(item[1])
			self.progress_window.current_progressbar.set_fraction(0.0)
			
			current_path = original_path = item[2]
			
			# iterate through 'operations_store' instead of 'operations'
			# to include the changed order of operations
			for operation in self.main_window.operations_store:
				if not self.running:
					return
				
				plugin = self.main_window.operations[operation[1]]
				
				try:
					current_path = plugin.process(current_path, original_path)
				except PluginError as e:
					gobject.idle_add(self.progress_window.show_error, e.message)
					self.running = False
				
				self.progress_window.current_progressbar.set_fraction(self.progress_window.current_progressbar.get_fraction() + current_step)
				self.progress_window.total_progressbar.set_fraction(self.progress_window.total_progressbar.get_fraction() + total_step)
		
		self.progress_window.current_progressbar.set_text("Finalizing...")
		self.progress_window.current_progressbar.set_fraction(0.0)
		
		for plugin_id, plugin in self.main_window.operations.items():
			try:
				plugin.finalize()
			except PluginError as e:
				gobject.idle_add(self.progress_window.show_error, e.message)
				self.running = False
			
			self.progress_window.current_progressbar.set_fraction(self.progress_window.current_progressbar.get_fraction() + current_step)
		
		print time.time() - start_time
		gobject.idle_add(self.progress_window.window.hide)
			

class ProcessWindow(object):
	def __init__(self, main_window):
		self.main_window = main_window
		
		self.builder = gtk.Builder()
		
		base_dir = os.path.dirname(os.path.realpath(__file__))
		ui_file = os.path.join(base_dir, 'processwindow.xml')
		
		self.builder.add_from_file(ui_file)
		self.builder.connect_signals(self)

		self.window = self.builder.get_object("process_window")
		self.current_progressbar = self.builder.get_object("current_progressbar")
		self.total_progressbar = self.builder.get_object("total_progressbar")
	
	def run(self):
		self.window.show()
		
		self.processing_thread = ProcessThread(self, self.main_window)
		self.processing_thread.daemon = True
		self.processing_thread.start()
	
	def show_error(self, message):
		dialog = gtk.MessageDialog(
			self.window,
			gtk.DIALOG_MODAL,
			gtk.MESSAGE_ERROR,
			gtk.BUTTONS_OK,
			message)

		self.window.hide()
		dialog.run()
		dialog.destroy()
	
	def close(self, widget, data=None):
		dialog = gtk.MessageDialog(
			self.window,
			gtk.DIALOG_MODAL,
			gtk.MESSAGE_QUESTION,
			gtk.BUTTONS_YES_NO,
			"Do you want to cancel?")
		
		if dialog.run() == gtk.RESPONSE_YES:
			self.processing_thread.running = False
			self.window.hide()
		
		dialog.destroy()
		
		# prevent from destroying the window when delete-event occurs
		return True
		
