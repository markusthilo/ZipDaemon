#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Markus Thilo'
__version__ = '0.0.1_2025-01-22'
__license__ = 'GPL-3'
__email__ = 'markus.thilo@gmail.com'
__status__ = 'Testing'
__description__ = 'Use PyInstaller to build executable'

from pathlib import Path
from shutil import rmtree
import PyInstaller.__main__

if __name__ == '__main__':	# start here
	name = 'zipdaemon'
	PyInstaller.__main__.run(['--onefile', '--name', name])
	Path(f'{name}.spec').unlink(missing_ok=True)
	rmtree('build')
