#!/usr/bin/python
'''
This class is used to check how much time has passed between a call and another
'''

import time

class Stopwatch(object):
	'Calculates an elapsed time from a certain checkpoint'
	def __init__(self):
		self.start_time = time.time()
		self.stop_time = self.start_time
		self.total_time = 0

	def start(self):
		self.start_time = time.time()

	def lap(self):
		return time.time() - self.start_time

	def stop(self):
		self.stop_time = time.time()
		self.total_time = self.stop_time - self.start_time
		return self.total_time

	def curTime():
		return time.time()