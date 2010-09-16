#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from zipfile import ZipFile

from batchimpapp.pluginbase import PluginSettingsBase, MagickCommand, \
	PluginError, FileChooserButtonField, EntryField

NAME = 'Save as a web gallery'
AUTHOR = 'Juliusz Gonera'
__version__ = '0.1'
__api_version__ = '0.1'


class Plugin(PluginSettingsBase):
	def init(self):
		FileChooserButtonField(self,
			name = 'directory',
			label = 'Directory:',
			title = 'Select a directory',
			action = FileChooserButtonField.SELECT_FOLDER
		)
		EntryField(self,
			name = 'gallery_name',
			label = 'Gallery name:',
			value = 'Gallery'
		)
	
	def prepare(self):
		self.directory = os.path.join(self.settings['directory'], self.settings['gallery_name'])
		
		if os.path.exists(self.directory):
			raise PluginError("A gallery with a given name already exists in the given directory.")
		
		os.mkdir(self.directory)
		os.mkdir(os.path.join(self.directory, 'thumbnails'))
		os.mkdir(os.path.join(self.directory, 'images'))
		ZipFile(os.path.splitext(__file__)[0] + '.zip', 'r').extractall(self.directory)
		
		self.html = '''<!DOChtml PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
		<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
			<head>
				<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
				<meta name="generator" content="Batch Image Processor" />
				<title>''' + self.settings['gallery_name'] + '''</title>
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
				<h1>''' + self.settings['gallery_name'] + '''</h1>
		
				<ul>'''
		
	
	def process(self, current_path, original_path, options):
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

