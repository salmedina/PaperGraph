#!/usr/bin/python
'''
This class is used to store the the features of a paper
This object is comparable for equality
'''
class Paper(object):
	'This class stores the features of a scientific paper'

	#TODO: revise the attributes
	def __init__(self, authors, title, references):
		self.authors = authors
		self.title = title
		self.references = references

	#The next two functions allow to compare for equality
	#in attributes of the Paper object by comparing the
	#attributes as comparable strings
	def __str__(self):
		return str(self.__dict__)
	def __eq__(self, other):
		return self.__dict__ == other.__dict__
	def __ne__(self, other):
		return not self == other

	def getNumAuthors():
		return len(authors)