#!/usr/bin/python

'''
This class is a wrapper to neo4jrestclient to 
manipulate data in the neo4j Graph DB
'''
#Imports
from neo4jrestclient.client import Node
from neo4jrestclient.client import GraphDatabase
from neo4jrestclient.query import Q

#Class definition
class GraphDB(object):

	def __init__(self, database="http://localhost:7474/db/data"):
		self.gdb = GraphDatabase(database)

	def addPaper(self, uid, title, authors):
		new_node = self.gdb.node()
		new_node.labels.add('Paper')
		new_node['uid'] = uid
		new_node['title'] = title
		new_node['authors'] = authors

	def getNode(self, uid):
		get_query = 'MATCH (n:Paper) WHERE n.uid=%d RETURN n'%uid
		qRes = self.gdb.query(q=get_query, returns=Node)
		if qRes == None:
			return None
		return qRes[0][0] #First element of first result is the expected node

	def editPaper(self, uid, key, value):
		node = self.getNode(uid)
		if not node:
			return False

		node.set(key, value)

	def deletePaper(self, uid):
		delQuery = 'MATCH (n { uid: %d })-[r]-() DELETE n, r'%uid
		try:
			self.gdb.query(q = delQuery)
		except e:
			return False

		return True

	def setReference(self, sourceUID, targetUID):
		srcNode = self.getNode(sourceUID)
		targetNode = self.getNode(targetUID)
		if srcNode ==None or targetNode ==None:
			return False

		newRel = srcNode.relationships.create("REFERENCE", targetNode)
		return True