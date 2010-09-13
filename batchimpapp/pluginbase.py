#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygtk
pygtk.require("2.0")
import gtk
import os.path
from pprint import PrettyPrinter as pp

class PluginError(Exception):
	def __init__(self, message):
		self.message = message


class PluginBase(object):
	def __init__(self, tmp_file, settings=None):
		self.tmp_file = tmp_file
		self.settings = {}
		self.init()
		if settings:
			self.settings = settings
		
	def init(self):
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


class PluginBaseSettings(PluginBase):
	def __init__(self, tmp_file, settings=None):		
		self.builder = gtk.Builder()
		self.builder.add_from_file(os.path.join(os.path.dirname(__file__), 'pluginsettings.xml'))
		self.builder.connect_signals(self)
		
		self.settings_window = self.builder.get_object("settings_window")
		self.main_table = self.builder.get_object("main_table")
		self.advanced_table = self.builder.get_object("advanced_table")
		self.advanced_expander = self.builder.get_object("advanced_expander")
		
		self.main_y = -1
		self.main_x = 0
		self.advanced_y = -1
		self.advanced_x = 0
		self._settings_getters = {}
		
		PluginBase.__init__(self, tmp_file, settings)
		
	def init(self):
		raise NotImplementedError("Need to initialize settings in 'init' method!")
	
	def show_settings(self):
		self.settings_window.show()
		
	def close_settings(self, widget, data=None):
		for name in self.settings.keys():
			self.settings[name] = self._settings_getters[name]()
	
		self.settings_window.hide()
		return True
	
	def _set_getter(self, getter, **args):
		self._settings_getters[args['name']] = getter
		
	def _add_widget(self, widget, width=1, **args):
		if args.get('advanced'):
			self.advanced_table.attach(widget, self.advanced_x, self.advanced_x+width, self.advanced_y, self.advanced_y+1)
			self.advanced_expander.show()
			self.advanced_x += width
		else:
			self.main_table.attach(widget, self.main_x, self.main_x+width, self.main_y, self.main_y+1)
			self.main_x += width
		widget.show()
	
	def add_label(self, **args):
		if not args.get('same_row'):
			if args.get('advanced'):
				self.advanced_y += 1
				self.advanced_x = 0
			else:
				self.main_y += 1
				self.main_x = 0
	
		if 'label' in args:
			label_widget = gtk.Label(args['label'])
			label_widget.set_alignment(0.0, 0.5)
			self._add_widget(label_widget, **args)
	
	def add_field(self, widget, width=1, **args):
		self._add_widget(widget, width, **args)
		self.settings[args['name']] = args['value']

	def add_spin_button(self, integer=False, minimum=0, maximum=1000000, **args):
		self.add_label(**args)
		
		widget = gtk.SpinButton(gtk.Adjustment(args['value'], minimum, maximum, 1, 10))
		widget.set_numeric(True)
		self.add_field(widget, **args)
		
		if integer:
			self._set_getter(widget.get_value_as_int, **args)
		else:
			self._set_getter(widget.get_value, **args)
	
	def add_check_button(self, **args):
		widget = gtk.CheckButton(args['label'])
		widget.set_active(args['value'])
		self.add_field(widget, 2, **args)
		self._set_getter(widget.get_active, **args)


	
		
