#!/usr/bin/python

# Imports
import os
import sys, getopt, re
import urllib2
import time
from Paper import *
import networkx as nx
import Scholar as sch
import Stopwatch as sw
from BeautifulSoup import BeautifulSoup

# Globals
PdfXURL 	= 'http://pdfx.cs.man.ac.uk'
FreeCiteURL = 'http://freecite.library.brown.edu/citations/create'
CachePath = os.path.join('.', 'cache')
SeekDepth	= 3
SeekLevel = 0
CurNodeId = 1

TitleGraph = nx.Graph()
OutputGraphName = 'Devel.graphml'
QueryChrono = sw.Stopwatch()

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
		return isValidPdfx(xmlStr), xmlStr
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
		ans = urllib2.urlopen(req)
		res = ans.read()
		return isValidFCCitation(res), res
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
		return title[0].string.encode('ascii', 'ignore')
	return ""

#TODO: def extractPdfxAbstract(xmlStr):
def isValidPdfx(xmlStr):
	soup = BeautifulSoup(xmlStr)
	return soup.find('error') == None

def isValidFCCitation(xmlStr):
	soup = BeautifulSoup(xmlStr)
	return soup.find('citation', attrs={"valid" : "true"}) != None

# Returns a list of authors from a FreeCite response
def extractFCAuths(xmlStr):
	soup = BeautifulSoup(xmlStr)
	authors = soup.findAll('author')
	authList = []
	for author in authors:
		authList.append(author.string)
	return authList

#Returns a the title of the article from a FreeCite response
def extractFCTitle(xmlStr):
	soup = BeautifulSoup(xmlStr)
	title = soup.find('title')
	return title.string.encode('ascii', 'ignore')

# xmlStr is PDFX format
# returns empty string if problem while parsing
def extractPdfxRefs(xmlStr):
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
		else:
			print 'Oops, there was a problem with FC parse'
			print refXML
	return refList

def getMainAuthor(authors):
	if len(authors) < 1:
		return 'Unknown'
	return authors[0]

def fileNameNoExt(filePath):
	return os.path.basename(os.path.splitext(filePath)[0])

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
	global CachePath
	ilegalChars = ":?\\/*<>|\""

	sAuthor = author.decode('unicode_escape').encode('ascii','ignore')
	pdfName = "[%s]-%s.pdf" % (sAuthor.translate(None, ilegalChars).replace(" ", "_"), title.translate(None, ilegalChars).replace(" ", "_"))
	
	return os.path.join(CachePath, pdfName)

def formatXmlName(author, title):
	global CachePath
	ilegalChars = ":?\\/*<>|\""

	sAuthor = author.decode('unicode_escape').encode('ascii','ignore')
	xmlName = "[%s]-%s.pdf" % (sAuthor.translate(None, ilegalChars).replace(" ", "_"), title.translate(None, ilegalChars).replace(" ", "_"))
	
	return os.path.join(CachePath, xmlName)

def saveXMLToFile(xmlStr, filePath, overwrite):
	if xmlStr and filePath and filePath != '':
		if not os.path.isfile(filePath) or \
				(os.path.isfile(filePath) and overwrite):
			print 'Saving PDF annotations: %s' % filePath
			xmlFile = open(filePath, 'w')
			xmlFile.write(xmlStr)
			xmlFile.close()

def importPdf(pdfFile):
	print '>>> Importing PDF -  %s'%pdfFile

	paper = None
	if os.path.isfile(pdfFile):
		xmlIsOK, pdfXML = pdfToXml(pdfFile)
		if xmlIsOK:
			saveXMLToFile(pdfXML, os.path.splitext(pdfFile)[0]+'.xml', True)
			authors = extractPdfxAuths(pdfXML)
			title = extractPdfxTitle(pdfXML)
			refs = extractPdfxRefs(pdfXML)
			paper = Paper(authors, title, refs)
		else:
			print "Oops, there was a problem on PDFX"
			print pdfXML
	
	return paper


# This downloads the first pdf that comes from the search 
# made by the title and stored into path, the pdf is named
# by convention: '[author]-title.pdf'
def fetchScholarPdf(title, path):
	global QueryChrono

	print 'Fetching pdf from Scholar: %s' % title
	querier = sch.ScholarQuerier()
	settings = sch.ScholarSettings()

	querier.apply_settings(settings)

	query = sch.SearchScholarQuery()
	query.set_phrase(title)
	query.set_scope(True)

	#Be good to Google and they will be good with you
	print 'Calming the beast (waiting 60 [s])'
	time.sleep(60)

	querier.send_query(query)
	
	if len(querier.articles) < 1:
		print 'Google Scholar did not find articles for %s'%title
		return False

	pdfURL = querier.articles[0]['url_pdf']
	try:
		print 'Trying to download from: %s' % pdfURL
		downloadFile(pdfURL, path)
	except:
		print 'There was a problem while trying to downlaoad %s'%title
		return False

	return True

def saveOutputGraph():
	global TitleGraph
	global OutputGraphName

	nx.write_graphml(TitleGraph, OutputGraphName)


def createPaperNode(paper, graph):
	global SeekDepth
	global CurNodeId
	global SeekLevel

	SeekLevel = SeekLevel + 1

	setId = CurNodeId
	CurNodeId = CurNodeId + 1

	mainAuth = ', '.join(paper.authors)
	print 'Adding node %d |  Author: %s  Tile: %s' %(setId, str(mainAuth), str(paper.title))
	graph.add_node(setId, {'Authors':str(mainAuth), 'Title':str(paper.title)})
	
	saveOutputGraph()

	if SeekLevel > SeekDepth:
		return setId

	for ref in paper.references:
		mainAuth = ', '.join(ref.authors)
		graph.add_node(CurNodeId, {'Authors':str(mainAuth), 'Title':str(ref.title)})

		newPdfFile = formatPdfName(mainAuth, str(ref.title))
		if fetchScholarPdf(ref.title, newPdfFile):
			refPaper = importPdf(newPdfFile)
			if refPaper:
				refId = createPaperNode(refPaper, graph)
				graph.add_edge(setId, refId)
				saveOutputGraph()
			else:
				print 'ERROR: while creating reference paper'
		else:
			print 'ERROR: Could not fetch PDF file from Scholar'

	return setId

### Main ################################
def main():
	global PdfRepository
	global TitleGraph
	global QueryChrono

	QueryChrono.start()

	filePath = 'E:\\MCC\\CMU\\Research\\Papers\\Motion Analysis\\ChenMoSIFTCMU09.pdf'
	firstPaper = importPdf(filePath)
	createPaperNode(firstPaper, TitleGraph)

	saveOutputGraph()

if __name__ == '__main__':
	main()
##########################################