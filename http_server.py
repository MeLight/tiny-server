import socket
import time
import urllib
import re
import os

LISTEN_SOCKET = 20959
WWW_DIR = 'www'

def headers2json(str):
	req_decoded = urllib.unquote(request).decode('utf8')
	arr = req_decoded.split('\r\n')
	request_line = arr.pop(0)
	#print(arr)
	return (request_line, arr,)

def getTemplateString(filename):
	with open(filename, 'r') as myfile:
		data=myfile.read()
		return data

def getPathAndQuery(req_line):
	matches = re.search('GET (.*)\?.* HTTP', req_line)
	if matches is not None:
		path = matches.group(1)
	else:
		matches = re.search('GET (.*) HTTP', req_line)
		if matches is not None:
			path = matches.group(1)
		else:
			path = ""

	#this part gets the query part of the URL
	matches = re.search('GET .*\?(.*) HTTP', req_line)
	if matches is not None:
		query = matches.group(1)
	else:
		query = ""

	return (path, query,)

#create an INET, STREAMing socket
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#bind the socket to a public host,
# and a well-known port
print("Host name: {}".format(socket.gethostname()))
serversocket.bind(('', LISTEN_SOCKET,))
#become a server socket
serversocket.listen(5)


keep_listening = True
#accept connections from outside
while keep_listening:
	(clientsocket, address) = serversocket.accept()
	request = clientsocket.recv(2048)
	print("request:----->\n{}".format(request))
	req_line, headers, = headers2json(request)

	#this part gets the path part of the URL
	path, query, = getPathAndQuery(req_line)
	#print("req_line: {}\n, headers: {}\n, query: {}".format(req_line, headers, query))
	status = 200

	print("Path: {}, query: {}".format(path, query))

	rel_server_path = WWW_DIR+path
	if os.path.isdir(rel_server_path):
		os.path.isdir(rel_server_path)
		if rel_server_path[-1:] != '/':
			rel_server_path += '/'
		filename = rel_server_path + 'index.yws'
		if not os.path.isfile(filename):
			status = 404
	else:
		filename = rel_server_path+'.yws'
		if not os.path.isfile(filename):
			status = 404
	

	#page not found
	if status == 404:
		r_msg = "<html><head><title>Not found</title><body><h2>404<h2><span style=\"color:darkred\">{} not found</span></body></html>".format(filename)

	#kill server 
	elif query == 'die':
		r_msg = "<html><head><title>end</title><body><span style=\"color:red\">terminating</span></body></html>"
		print("Got a DIE request. Quitting")
		keep_listening = False

	#this is the normal case
	else:
		template = getTemplateString(filename)
		r_msg = template.format(query, path)
	
	#print("MSG:  {}".format(template))
	header = """
	HTTP/1.1 {} OK
	Content-Length: {}

	""".format(status, len(r_msg))

	clientsocket.send(header + r_msg)
	clientsocket.close()


