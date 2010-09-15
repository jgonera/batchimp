#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
import subprocess

import pygtk
pygtk.require("2.0")
import gtk
import gobject


class PluginError(Exception):
	def __init__(self, message):
		self.message = message


class MagickCommand(object):
	def __init__(self, graphics_magick=True):
		if graphics_magick:
			self.args = ['gm']
		else:
			self.args = []
	
	def append(self, *args):
		self.args.extend(args)
		return self
	
	def run(self):
		subprocess.call(self.args)


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


class PluginSettingsBase(PluginBase):
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


class FieldBase(object):
	def __init__(self, plugin, left=0, **kwargs):
		self.plugin = plugin
		self.args = kwargs
		
		if not self.args.get('same_row'):
			if self.args.get('advanced'):
				self.plugin.advanced_y += 1
				self.plugin.advanced_x = left
			else:
				self.plugin.main_y += 1
				self.plugin.main_x = left
		
		self.init(**kwargs)
		
		if self.args.get('name'):
			self.plugin.settings[self.args['name']] = self.args['value']
	
	def _set_getter(self, getter):
		self.plugin._settings_getters[self.args['name']] = getter
		
	def _add_widget(self, widget, width=1, xoptions=gtk.EXPAND|gtk.FILL, yoptions=gtk.FILL):
		if self.args.get('advanced'):
			self.plugin.advanced_table.attach(
				widget,
				self.plugin.advanced_x,
				self.plugin.advanced_x+width,
				self.plugin.advanced_y,
				self.plugin.advanced_y+1,
				xoptions,
				yoptions
			)
			self.plugin.advanced_expander.show()
			self.plugin.advanced_x += width
		else:
			self.plugin.main_table.attach(
				widget,
				self.plugin.main_x,
				self.plugin.main_x+width,
				self.plugin.main_y,
				self.plugin.main_y+1,
				xoptions,
				yoptions
			)
			self.plugin.main_x += width
		widget.show()
	
	def _add_label(self):
		if 'label' in self.args:
			label_widget = gtk.Label(self.args['label'])
			label_widget.set_alignment(0.0, 0.5)
			self._add_widget(label_widget, 1, gtk.FILL)


class LabelField(FieldBase):
	def init(self, width=1, **kwargs):
		self.widget = gtk.Label(self.args['label'])
		#label_widget.set_alignment(0.0, 0.5)
		self._add_widget(self.widget, width, gtk.FILL)


class EntryField(FieldBase):
	def init(self, value, **kwargs):
		self._add_label()
		
		self.widget = gtk.Entry()
		self.widget.set_text(value)
		
		self._add_widget(self.widget)
		self._set_getter(self.widget.get_text)


class SpinButtonField(FieldBase):
	def init(self, value, integer=False, minimum=0, maximum=1000000, **kwargs):
		self._add_label()
		
		self.widget = gtk.SpinButton(gtk.Adjustment(value, minimum, maximum, 1, 10))
		self.widget.set_numeric(True)
		self._add_widget(self.widget)
		
		if integer:
			self._set_getter(self.widget.get_value_as_int)
		else:
			self._set_getter(self.widget.get_value)


class CheckButtonField(FieldBase):
	def init(self, value, label, **kwargs):
		self.widget = gtk.CheckButton(label)
		self.widget.set_active(value)
		self._add_widget(self.widget, 2)
		self._set_getter(self.widget.get_active)


class ComboBoxField(FieldBase):
	def init(self, options, active_option=0, **kwargs):
		self._add_label()
		
		self.widget = gtk.combo_box_new_text()
		for option in options:
			self.widget.append_text(option)
		self.widget.set_active(active_option)
		
		self._add_widget(self.widget)
		self._set_getter(self.widget.get_active_text)
		
		if 'value' not in self.args:
			self.args['value'] = options[0]


class FileChooserButtonField(FieldBase):
	OPEN = gtk.FILE_CHOOSER_ACTION_OPEN
	SAVE = gtk.FILE_CHOOSER_ACTION_SAVE
	SELECT_FOLDER = gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER
	CREATE_FOLDER = gtk.FILE_CHOOSER_ACTION_CREATE_FOLDER
	
	def init(self, title, action, **kwargs):
		self._add_label()
		
		self.widget = gtk.FileChooserButton(title)
		self.widget.set_action(action)
		
		self._add_widget(self.widget)
		if action == self.SELECT_FOLDER or action == self.CREATE_FOLDER:
			self._set_getter(self.widget.get_current_folder)
		else:
			raise NotImplementedError("Oops, need to implement")
		
		if 'value' not in self.args:
			self.args['value'] = self.widget.get_current_folder()
		
		
