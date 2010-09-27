#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
import subprocess
import tempfile

import pygtk
pygtk.require("2.0")
import gtk
import gobject


_tmp_file = tempfile.NamedTemporaryFile()
tmp_file = _tmp_file.name


class PluginError(Exception):
	def __init__(self, message):
		self.message = message


class MagickCommand(object):
	def __init__(self, use_gm=True, use_tmp_file=True):
		self.use_tmp_file = use_tmp_file
		if use_gm and False: # TODO: change this to some setting in GUI
			self.args = ['gm']
			self.gm = True
		else:
			self.args = []
			self.gm = False
	
	def append(self, *args):
		self.args.extend(args)
		return self
	
	def append_color(self, color):
		self.args.append('rgba(' + str(color['red']) + ',' + str(color['green']) + ',' + str(color['blue']) + ',' + str(color['alpha']) + ')')
		return self
	
	def run(self):
		if self.use_tmp_file:
			self.args.append('mpc:' + tmp_file)
		if not self.gm:
			self.args.insert(-1, '-auto-orient')
		
		subprocess.call(self.args)
		
		if self.use_tmp_file:
			return tmp_file
		else:
			return None


class PluginBase(object):
	def __init__(self, settings=None):
		self.settings = {}
		self.init()
		if settings:
			self.settings = settings
		
	def init(self):
		pass
	
	def show_settings(self):
		dialog = gtk.MessageDialog(
			None,
			gtk.DIALOG_MODAL,
			gtk.MESSAGE_INFO,
			gtk.BUTTONS_OK,
			"This operation does not need any configuration.")
			
		dialog.run()
		dialog.destroy()
	
	def prepare(self):
		pass

	def process(self, current_path, original_path, options):
		raise NotImplementedError("Need to define 'process' method!")
	
	def finalize(self):
		pass


class PluginSettingsBase(PluginBase):
	def __init__(self, settings=None):		
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
		
		PluginBase.__init__(self, settings)
		self.show_settings()
		
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
		
	def _add_widget(self, widget, width=1, xoptions=gtk.EXPAND|gtk.FILL, yoptions=gtk.EXPAND|gtk.FILL, xpadding=0, ypadding=0):
		if self.args.get('advanced'):
			self.plugin.advanced_table.attach(
				widget,
				self.plugin.advanced_x,
				self.plugin.advanced_x+width,
				self.plugin.advanced_y,
				self.plugin.advanced_y+1,
				xoptions,
				yoptions,
				xpadding,
				ypadding
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
				yoptions,
				xpadding,
				ypadding
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
	def init(self, value, digits=0, minimum=0, maximum=1000000, step_increment=1, page_increment=10, climb_rate=0, **kwargs):
		self._add_label()
		
		self.widget = gtk.SpinButton(gtk.Adjustment(value, minimum, maximum, step_increment, page_increment), climb_rate)
		self.widget.set_numeric(True)
		self.widget.set_digits(digits)
		self._add_widget(self.widget)
		
		if digits == 0:
			self._set_getter(self.widget.get_value_as_int)
		else:
			self._set_getter(self.widget.get_value)


class ScaleField(FieldBase):
	def init(self, value, digits=0, minimum=0, maximum=1000000, **kwargs):
		self._add_label()
		
		self.widget = gtk.HScale(gtk.Adjustment(value, minimum, maximum, 1, 10))
		self.widget.set_digits(digits)
		self.widget.set_value_pos(gtk.POS_RIGHT)
		self.widget.set_size_request(150, -1)
		self._add_widget(widget=self.widget, ypadding=3)
		
		self._set_getter(self.widget.get_value)


class CheckButtonField(FieldBase):
	def init(self, value, label, **kwargs):
		self.widget = gtk.CheckButton(label)
		self.widget.set_active(value)
		self._add_widget(widget=self.widget, width=2, ypadding=3)
		self._set_getter(self.widget.get_active)


class RadioButtonsField(FieldBase):
	def init(self, label, options, active_option=0, **kwargs):
		assert len(options) > 1
		self._add_label()
		
		self.widget = gtk.VBox()
		first_button = gtk.RadioButton(None, options[0])
		self.widget.add(first_button)
		first_button.show()
		self.radio_buttons = [first_button]
		for option in options[1:]:
			button = gtk.RadioButton(first_button, option)
			self.widget.add(button)
			self.radio_buttons.append(button)
			button.show()
		
		if 'value' not in self.args:
			self.args['value'] = active_option
		self.radio_buttons[self.args['value']].set_active(True)
		
		self._add_widget(self.widget)
		self._set_getter(self.get_value)
	
	def get_value(self):
		for i, button in enumerate(self.radio_buttons):
			if button.get_active():
				return i


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


class ColorButtonField(FieldBase):
	MAX_COLOR_VALUE = 65535
	
	def init(self, use_alpha=False, use_16bit=False, **kwargs):
		self.use_16bit = use_16bit
		self._add_label()
		
		self.widget = gtk.ColorButton()
		self.widget.set_use_alpha(use_alpha)
		alignment = gtk.Alignment()
		alignment.add(self.widget)
		self.widget.show()
		self._add_widget(alignment)
		self._set_getter(self.get_value)
		
		if 'value' not in self.args:
			self.args['value'] = self.get_value()
	
	def get_value(self):
		color = self.widget.get_color()
		
		if self.use_16bit:
			value = {
				'red': color.red,
				'green': color.green,
				'blue': color.blue,
				'alpha': self.widget.get_alpha()
			}
		else:
			value = {
				'red': color.red*255/self.MAX_COLOR_VALUE,
				'green': color.green*255/self.MAX_COLOR_VALUE,
				'blue': color.blue*255/self.MAX_COLOR_VALUE,
				'alpha': self.widget.get_alpha()*255/self.MAX_COLOR_VALUE
			}
		
		return value
		
