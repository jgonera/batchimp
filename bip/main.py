#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygtk
pygtk.require("2.0")
import gtk
import os
import random
import subprocess
import gobject
import imp
from threading import Thread

from bip.process import ProcessWindow

base_dir = os.path.dirname(os.path.realpath(__file__))

class ThumbnailsThread(Thread):
	def __init__(self, files_store, tmp_file):
		Thread.__init__(self)
		self.files_store = files_store
		self.tmp_file = tmp_file
	
	def run(self):
		for item in self.files_store:
			if item[0]:
				continue
			
			rc = subprocess.call(('convert', '-size', '120x120', item[2], '-scale', '120x120', '-strip', '-auto-orient', 'bmp:' + self.tmp_file))
			if rc == 0:
				gobject.idle_add(self.add_thumbnail, item, gtk.gdk.pixbuf_new_from_file(self.tmp_file))
	
	def add_thumbnail(self, item, pixbuf):
		item[0] = pixbuf


class MainWindow(object):
	def test(self, widget, data=None):
		print "test"
		
	def __init__(self):
		global base_dir
	
		gobject.threads_init()

		# TODO: change to Python's temp file
		self.tmp_file = '/tmp/bip' + str(random.randint(10000000, 99999999))
	
		self.builder = gtk.Builder()
		
		ui_file = os.path.join(base_dir, 'mainwindow.xml')
		
		self.builder.add_from_file(ui_file)
		self.builder.connect_signals(self)
		
		self.window = self.builder.get_object("main_window")
		
		self.files_store = self.builder.get_object("files_store")
		self.files_store.set_sort_column_id(1, gtk.SORT_ASCENDING)
		
		self.files_view = self.builder.get_object("files_view")
		
		self.filechooserdialog = self.builder.get_object("filechooserdialog")
		self.aboutdialog = self.builder.get_object("aboutdialog")
		
		self.plugins_combobox = self.builder.get_object("plugins_combobox")
		self.plugins_store = self.builder.get_object("plugins_store")
		self.plugins_store_change = self.plugins_store.append(None, ('Change', 0, False))
		self.plugins_store_save = self.plugins_store.append(None, ('Save', 0, False))
		
		self.operations_view = self.builder.get_object("operations_view")
		self.operations_view.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
		self.operations_view.get_selection().connect("changed", self.set_sensitivity)
		self.operations_store = self.builder.get_object("operations_store")
		
		self.process_window = ProcessWindow(self);
		
		self.operation_id = 0
		self.plugins = []
		self.operations = {}
		self.load_plugins()

		self.set_sensitivity(None)
		
		self.window.show()
		
		gtk.main()
	
	def load_plugins(self):
		global base_dir
		
		plugins_dir = os.path.join(base_dir, 'plugins')
		dir_list = os.listdir(plugins_dir)
		
		for item in sorted(dir_list):
			(name, ext) = os.path.splitext(item)
			plugin_file = os.path.join(plugins_dir, item)
			
			if not os.path.isfile(plugin_file) or not ext == '.py':
				continue
			
			plugin = imp.load_source(name, plugin_file)
			self.plugins.append(plugin)
			
			if plugin.TYPE == "change":
				self.plugins_store.append(self.plugins_store_change, (plugin.NAME, len(self.plugins)-1, True))
			elif plugin.TYPE == "save":
				self.plugins_store.append(self.plugins_store_save, (plugin.NAME, len(self.plugins)-1, True))
		
	def on_quit(self, widget, data=None):
		if os.path.exists(self.tmp_file):
			os.remove(self.tmp_file)
			
		gtk.main_quit()
	
	def show_aboutdialog(self, widget, data=None):
		self.aboutdialog.run()
		self.aboutdialog.hide()
	
	def show_filechooserdialog(self, widget, data=None):
		response = self.filechooserdialog.run()
		self.filechooserdialog.hide()
		
		if response == 1:
			self.add_files(self.filechooserdialog.get_filenames())
			
	def on_filechooserdialog_file_activated(self, widget, data=None):
		if os.path.isfile(self.filechooserdialog.get_filename()):
			self.filechooserdialog.hide()
			self.add_files(self.filechooserdialog.get_filenames())
	
	def add_files(self, items):
		for item in items:
			if not os.path.isfile(item):
				continue
			
			self.files_store.append((None, os.path.basename(item), item))
		
		thumbnail_thread = ThumbnailsThread(self.files_store, self.tmp_file)
		thumbnail_thread.daemon = True
		thumbnail_thread.start()
	
	def remove_files(self, widget, data=None):
		items = self.files_view.get_selected_items()
		
		for item in items:
			self.files_store.remove(self.files_store.get_iter(item))
			
	def open_file(self, widget, data=None):
		subprocess.Popen(('xdg-open', self.files_store.get_value(self.files_store.get_iter(self.files_view.get_selected_items()[0]), 2)))
			
	def select_all_files(self, widget, data=None):
		self.files_view.select_all()
	
	def set_sensitivity(self, widget, data=None):
		if self.files_view.get_selected_items():
			files_selected = True
		else:
			files_selected = False
		
		self.builder.get_object("remove_files_menuitem").set_sensitive(files_selected)
		self.builder.get_object("remove_files_toolbutton").set_sensitive(files_selected)
		self.builder.get_object("open_file_menuitem").set_sensitive(files_selected)
		
		if self.plugins_combobox.get_active() == -1:
			self.builder.get_object("add_operation_toolbutton").set_sensitive(False)
		else:
			self.builder.get_object("add_operation_toolbutton").set_sensitive(True)
		
		selected_operations = self.operations_view.get_selection().count_selected_rows()
		
		self.builder.get_object("remove_operation_toolbutton").set_sensitive(selected_operations > 0)
		self.builder.get_object("operation_settings_toolbutton").set_sensitive(selected_operations == 1)
	
	def on_plugins_combobox_changed(self, widget, data=None):
		self.add_operation(widget)
		self.set_sensitivity(widget)
	
	def add_operation(self, widget, data=None):
		plugin_id = self.plugins_store.get_value(self.plugins_combobox.get_active_iter(), 1)
		plugin = self.plugins[plugin_id]
		self.operations[self.operation_id] = plugin.Plugin(self.tmp_file)
		self.operations_store.append((plugin.NAME, self.operation_id, plugin.TYPE == "save"))
		
		self.operation_id = self.operation_id + 1
		
	def remove_operation(self, widget, data=None):
		selection = self.operations_view.get_selection()
		(model, pathlist) = selection.get_selected_rows()
		
		for path in reversed(pathlist):
			operation_iter = self.operations_store.get_iter(path)
			operation_id = self.operations_store.get_value(operation_iter, 1)
			self.operations_store.remove(operation_iter)
			self.operations.pop(operation_id)
			
	def on_operations_view_row_activated(self, widget, path, view_column, data=None):
		operation_iter = self.operations_store.get_iter(path)
		operation_id = self.operations_store.get_value(operation_iter, 1)
		self.operations[operation_id].show_settings()
		
	def show_operation_settings(self, widget, data=None):
		selection = self.operations_view.get_selection()
		(model, pathlist) = selection.get_selected_rows()
		
		operation_iter = self.operations_store.get_iter(pathlist[0])
		operation_id = self.operations_store.get_value(operation_iter, 1)
		self.operations[operation_id].show_settings()
		
	def apply_operations(self, widget, data=None):
		if len(self.operations) == 0 or len(self.files_store) == 0:
			dialog = gtk.MessageDialog(
			self.window,
			gtk.DIALOG_MODAL,
			gtk.MESSAGE_INFO,
			gtk.BUTTONS_OK,
			"You have to add at least one file and one operation.")
			
			dialog.run()
			dialog.destroy()
			
			return
		
		last_operation_iter = self.operations_store.iter_nth_child(None, len(self.operations_store)-1)
		if self.operations_store.get_value(last_operation_iter, 2) == False:
			dialog = gtk.MessageDialog(
			self.window,
			gtk.DIALOG_MODAL,
			gtk.MESSAGE_QUESTION,
			gtk.BUTTONS_YES_NO,
			"The last operation does not save changed images.\nAre you sure you want to continue?")
			
			response = dialog.run()
			dialog.destroy()
			
			if response == gtk.RESPONSE_NO:
				return
		
		self.process_window.run();


if __name__ == "__main__":
	MainWindow()

