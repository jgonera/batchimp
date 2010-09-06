#!/usr/bin/env python
# -*- coding: utf-8 -*-

from batchimpapp.pluginbase import PluginBase
import pygtk
pygtk.require("2.0")
import gtk
import subprocess
import os
from zipfile import ZipFile

NAME = "Save as a web gallery"
TYPE = "save"

class Plugin(PluginBase):
	def __init__(self, tmp_file):
		self.builder = gtk.Builder()
		self.builder.add_from_file(os.path.splitext(__file__)[0] + ".xml")
		self.builder.connect_signals(self)

		self.settings_window = self.builder.get_object("settings_window")
		self.directory_chooser = self.builder.get_object("directory_chooser")
		self.gallery_name_entry = self.builder.get_object("gallery_name_entry")
		
	def show_settings(self):
		self.settings_window.show()
		
	def close_settings(self, widget, data=None):
		self.settings_window.hide()
		return True
	
	def prepare(self):
		self.directory = os.path.join(self.directory_chooser.get_current_folder(), 'gallery')
		gallery_name = self.gallery_name_entry.get_text()
		
		os.mkdir(self.directory)
		os.mkdir(os.path.join(self.directory, 'thumbnails'))
		os.mkdir(os.path.join(self.directory, 'images'))
		ZipFile(os.path.splitext(__file__)[0] + '.zip', 'r').extractall(self.directory)
		
		self.html = '''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
		<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
			<head>
				<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
				<meta name="generator" content="Batch Image Processor" />
				<title>''' + gallery_name + '''</title>
				<!--[if gte IE 6]><!-->
				<style type="text/css" media="screen">
				@import "design/screen.css";
				@import "design/thickbox.css";
				</style>
				<script type="text/javascript" src="design/jquery.js"></script>
				<script type="text/javascript" src="design/thickbox.js"></script>
				<!--<![endif]--> 
			</head>
			<body>
				<h1>''' + gallery_name + '''</h1>
		
				<ul>'''
		
		
	
	def process(self, current_path, original_path):
		original_file_name = os.path.basename(original_path)
		(original_basename, original_ext) = os.path.splitext(original_file_name)
		
		subprocess.call(('convert', '-size', '120x120', current_path, '-scale', '120x120', '-strip', '-auto-orient', os.path.join(self.directory, 'thumbnails', 't_' + original_basename + '.jpg')))
		subprocess.call(('convert', current_path, '-auto-orient', os.path.join(self.directory, 'images', original_basename + '.jpg')))
		
		self.html = self.html + '''
		<li>
			<a class="thickbox" rel="gallery" href="images/''' + original_basename + '''.jpg">
				<img src="thumbnails/t_''' + original_basename + '''.jpg" alt="Thumbnail" />
				<span>''' + original_basename + '''</span>
			</a>
		</li>
		'''
		
		return current_path
		
	def finalize(self):
		self.html = self.html + '</ul></body></html>'
		
		htmlFile = open(os.path.join(self.directory, 'index.html'), 'w')
		htmlFile.write(self.html)
		htmlFile.close()

