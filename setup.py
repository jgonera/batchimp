#!/usr/bin/env python
# BatchImP's setup.py
from distutils.core import setup

setup(
	name = "batchimp",
	version = "0.1",
	description = "Graphical utility for performing batch operations on images (using ImageMagick)",
	author = "Juliusz Gonera",
	author_email = "jgonera@gmail.com",
	url = "http://github.com/jgonera/bip",
	#download_url = "http://github.com/jgonera/bip/tarball/0.1",
	keywords = ["imagemagick", "gui", "image", "batch", "processing"],
	classifiers = [
		"Programming Language :: Python",
		"Programming Language :: Python :: 2.6",
		"Development Status :: 3 - Alpha",
		"Environment :: X11 Applications :: GTK",
		"Environment :: X11 Applications :: Gnome",
		"Intended Audience :: End Users/Desktop",
		"License :: OSI Approved :: GNU General Public License (GPL)",
		"Operating System :: POSIX",
		"Topic :: Desktop Environment :: Gnome",
		"Topic :: Multimedia :: Graphics :: Graphics Conversion"
	],
	long_description = open("README.txt").read(),
	license = "GPLv3",
	
	packages = ["batchimpapp", "batchimpapp.plugins"],
	package_data = {
		'': ['*.xml'],
		'batchimpapp.plugins': ['*']
    },
	scripts = ['batchimp'],
	data_files = [
		('bin', ['batchimp'])
	]
)
