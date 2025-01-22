#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Markus Thilo'
__version__ = '0.0.1_2025-01-22'
__license__ = 'GPL-3'
__email__ = 'markus.thilo@gmail.com'
__status__ = 'Testing'
__description__ = 'Zip directories triggered by file'

import logging
from pathlib import Path
from time import sleep
from datetime import datetime
from zipfile import ZipFile, ZIP_DEFLATED
from argparse import ArgumentParser, FileType

class Logger:
	'Advanced logging functionality'

	def __init__(self, path, debug=False):
		'''Define logging by given level and to given file'''
		self.path = path
		self.level = logging.DEBUG if debug else logging.INFO
		self._start()
	
	def _start(self):
		'''Create logfile and start logging'''
		if self.path.is_file():
			old_zip = self.path.parent / datetime.now().strftime(f'{self.path.stem}_%Y-%m-%d_%H%M%S.zip')
			with ZipFile(old_zip, 'w', ZIP_DEFLATED) as zf:
				zf.write(self.path, self.path.name)
			self.path.unlink()
		elif self.path.exists():
			raise RuntimeError(f'Unable to create log file {self.path}')
		logging.basicConfig(
			level = self.level,
			filename = self.path,
			format = '%(asctime)s %(levelname)s: %(message)s',
			datefmt = '%Y-%m-%d %H:%M:%S'
		)

	def rotate(self):
		'''Rotate and backup old logfile as zip'''
		logging.shutdown()
		self._start()

class Walker:
	'''Walk through root dir and zip if trigger file is in subdir'''

	def __init__(self, root, trigger):
		'''Set root dir and trigger file'''
		self.root = root
		self.trigger = trigger

	def run(self):
		'''Walk through root dir and zip if trigger file is in subdir'''
		for subdir in self.root.iterdir():
			if subdir.is_dir() and subdir.joinpath(self.trigger).is_file():
				zip_path = self.root / f'{subdir.name}.zip'
				if logging.root.level == logging.DEBUG:
					print(f'DEBUG zipping {subdir} to {zip_path}')
				if zip_path.exists():
					logging.debug(f'Zip file {zip_path} already exists, skipping')
					continue
				logging.info(f'Creating {zip_path}')
				with ZipFile(zip_path, 'w', ZIP_DEFLATED) as zf:
					for path in subdir.rglob('*'):
						if path.is_file() and path.name != self.trigger:
							zf.write(path, path.relative_to(subdir))

	def daemon(self):
		'''Endless loop for daemon mode'''
		while True:
			try:
				self.run()
			except Exception as e:
				logging.error(f'Something went wrong in main loop while checking:\n{e}')
			sleep(1)

if __name__ == '__main__':	# start here if called as application
	this_script_path = Path(__file__)
	argparser = ArgumentParser(description=__description__)
	argparser.add_argument('-d', '--debug', action='store_true', help = 'Debug mode')
	argparser.add_argument('-l', '--logfile',
		type = Path,
		help = 'Logfile (default: zipdaemon.log)',
		metavar = 'FILE',
		default = Path.cwd() / 'zipdaemon.log'
	)
	argparser.add_argument('-t', '--trigger',
		type = str,
		help = 'Trigger file (default: zipthis.txt)',
		metavar = 'FILE',
		default = 'zipthis.txt'
	)
	argparser.add_argument('root', nargs=1, type=Path, help='Root directory', metavar='DIRECTORY')
	args = argparser.parse_args()
	Logger(args.logfile, debug=args.debug)
	if args.debug:
		print(f'DEBUG: running in debug mode, logfile: {args.logfile}')
		logging.debug('Running in debug mode')
		Walker(args.root[0], args.trigger).run()
		logging.debug('Finished')
		print('DEBUG: finished, logfile:')
		print(args.logfile.read_text())
		
	else:
		logging.info('Starting main loop')
		Walker(args.root[0], args.trigger).daemon()