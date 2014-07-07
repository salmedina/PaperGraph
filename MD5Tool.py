#!/usr/bin/python
'''
This class calculates the MD5 hash for any given file
'''
import hashlib
import os

class MD5Tool(object):
	
	def __init__(self):
		self.md5 = hashlib.md5()

	def hash(self, file_path, block_size=2**10):
		md5File = open(file_path, 'rb')
		while True:
			data = md5File.read(block_size)
			if not data:
				break
			self.md5.update(data)

		return self.md5.hexdigest()