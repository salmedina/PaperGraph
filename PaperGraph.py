#!/usr/bin/python

# Imports
import os
from BeautifulSoup import BeautifulSoup
import sys, getopt, re
import urllib2
import scholar
import networkx as nx
from Paper import *
import Scholar as sch

# Globals
PdfXURL 	= 'http://pdfx.cs.man.ac.uk'
FreeCiteURL = 'http://freecite.library.brown.edu/citations/create'
PdfRepository = '.\\PDFs'
SeekDepth	= 4
TitleGraph = nx.Graph()
CurNodeId = 1

# Fuctions
def pdfToXml(pdfFile): #Full path to the pdf
	print 'Converting PDF to XML'
	fileData = open(pdfFile, "rb")
	fileLength = os.path.getsize(pdfFile)

	req = urllib2.Request(PdfXURL, data=fileData ,headers = {'Content-Type':'application/pdf'})
	req.add_header('Content-Length', '%d' % fileLength)

	try:
		result = urllib2.urlopen(req)
		xmlStr = result.read()
		return True, xmlStr
	except urllib2.HTTPError as e:
		error_message = e.read()
		print error_message
		return False, ""

# FreeParse requires to add "citation=" before the citation text
# The format can also be citations for a batch processing
def formatFreeCiteRequestTxt(txt):
	formatTxt = 'citation=%s'%(txt)
	return formatTxt

# Queries FreeParse.org to extract features from the citation text
def freeCiteParse(txt):
	print 'Requesting FreeCite Parse %s' % txt
	req = urllib2.Request(FreeCiteURL, data=formatFreeCiteRequestTxt(txt) ,headers = {'Accept':'text/xml'})
	try:
		res = urllib2.urlopen(req)
		return True, res.read()
	except urllib2.HTTPError as e:
		error_message = e.read()
		print "ERROR: FreeCite says " + error_message
		return False, ''

def extractPdfxAuths(xmlStr):
	soup = BeautifulSoup(xmlStr)
	authors = soup.findAll('contrib', attrs={'contrib-type' : 'author'})

	authList = []
	for author in authors:
		authList.append(author.contents[1].contents[0].encode('ascii', 'ignore')) #the first content is a '\n' in PDFX format

	return authList

def extractPdfxTitle(xmlStr):
	soup = BeautifulSoup(xmlStr)
	title = soup.findAll('article-title')
	if len(title) > 0:
		return title[0].contents[0].encode('ascii', 'ignore')
	return ""

#TODO: def extractPdfxAbstract(xmlStr):

def isValidFCCitation(xmlStr):
	soup = BeutifulSoup(xmlStr)
	return soup.find('citation', attrs={"valid" : "true"}) != None

# Returns a list of authors from a FreeCite response
def extractFCAuths(xmlStr):
	soup = BeautifulSoup(xmlStr)
	authors = soup.findAll('author')
	authList = []
	for author in authors:
		print author
		authList.append(author.contents[0])
	return authList

#Returns a the title of the article from a FreeCite response
def extractFCTitle(xmlStr):
	soup = BeautifulSoup(xmlStr)
	title = soup.find('title')
	return title.contents[0].encode('ascii', 'ignore')

def extractPdfxRefs(xmlStr):	#txt:pdf in XML
	print 'Extracting references'
	res = None

	soup = BeautifulSoup(xmlStr)
	refs = soup.findAll('ref')
	refList = []
	for ref in refs:
		parseOK, refXML = freeCiteParse(ref.contents[0].encode('ascii', 'ignore'))
		if parseOK:
			authors = extractFCAuths(refXML)
			title = extractFCTitle(refXML)
			paper = Paper(authors, title, [])
			refList.append(paper)
	return refList

def downloadFile(url, fileName):
	try:
		f = urllib2.urlopen(url)
		local_file = open(fileName, "wb")
		local_file.write(f.read())
		local_file.close()
	except HTTPError, e:
		print "HTTP Error:", e.code, url
		return False
	except URLError, e:
		print "URL Error:", e.reason, url
		return False

	return True

def formatPdfName(author, title):
	ilegalChars = ":?\\/*<>|\""
	pdfName = "[%s]-%s.pdf" % (author.translate(None, ilegalChars).replace(" ", "_"), title.translate(None, ilegalChars).replace(" ", "_"))
	return pdfName

def importPdf(pdfFile):
	print '>>> Importing PDF -  %s'%pdfFile

	paper = None
	if os.path.isfile(pdfFile):
		xmlIsOK, pdfXML = pdfToXml(pdfFile)
		if xmlIsOK:
			authors = extractPdfxAuths(pdfXML)
			title = extractPdfxTitle(pdfXML)
			refs = extractPdfxRefs(pdfXML)
			paper = Paper(authors, title, refs)
	
	return paper
# This downloads the first pdf that comes from the search 
# made by the title and stored into path, the pdf is named
# by convention: '[author]-title.pdf'
def fetchScholarPdf(title, path):

	return False

def createPaperNode(paper, graph):
	global SeekDepth
	global CurNodeId

	setId = CurNodeId
	CurNodeId = CurNodeId + 1

	mainAuth = ', '.join(paper.authors)
	print 'Adding node %d |  Author: %s  Tile: %s' %(setId, str(mainAuth), str(paper.title))
	graph.add_node(setId, {'Authors':str(mainAuth), 'Title':str(paper.title)})
	
	for ref in paper.references:
		mainAuth = ', '.join(ref.authors)
		graph.add_node(CurNodeId, {'Authors':str(mainAuth), 'Title':str(ref.title)})
		print 'Adding ref node - Auth: %s   Title: %s' %(mainAuth, ref.title)
		graph.add_edge(setId, CurNodeId)
		CurNodeId = CurNodeId + 1

		'''
		newPdfFile = formatPdfName(mainAuth, str(ref.title))
		if fetchScholarPdf(ref.title, newPdfFile):
			refPaper = importPdf(newPdfFile)
			refId = createPaperNode(refPaper, graph)
			graph.add_edge(setId, refId)
		'''
	return setId

### Main ################################
def main():
	global SeekDepth
	global PdfRepository
	global TitleGraph

	filePath = 'E:\\MCC\\CMU\\Research\\Papers\\Motion Analysis\\ChenMoSIFTCMU09.pdf'
	firstPaper = importPdf(filePath)
	createPaperNode(firstPaper, TitleGraph)

	nx.write_graphml(TitleGraph, 'DevelTest.graphml')

if __name__ == '__main__':
	main()
##########################################