import urllib2, os

pdfxURL = 'http://pdfx.cs.man.ac.uk'
pdfHeader = {'Content-Type':'application/pdf'}
FilePath = "E:\\MCC\\CMU\\Devel\\PaperGraph\\pdfssa4met\\ChenMoSIFTCMU09.pdf"

FileData = open(FilePath, "rb")
FileLength = os.path.getsize(FilePath)

req = urllib2.Request(pdfxURL, data=FileData ,headers = pdfHeader)
req.add_header('Content-Length', '%d' % FileLength)

try:
	result = urllib2.urlopen(req)
	print result.read()
	# result.read() will contain the data
	# result.info() will contain the HTTP headers
except urllib2.HTTPError as e:
	error_message = e.read()
	print error_message
# To get say the content-length header
#length = result.info()['Content-Length']