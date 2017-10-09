
#!/usr/bin/env python

##################################################################################
## License
'''
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/gpl-3.0.txt>.
'''
#
##################################################################################



from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
import telnetlib
import json
import threading
import time
import json
import ssl
import logging
import argparse
import signal
import os
import sys

DEFAULT_LISTENPORT  =  7777
DEFAULT_PORT_SNAPCAST = 1705
VERSION = "0.0.1"
AUTHOR="SW Engineer: Garzola Marco"

parser = argparse.ArgumentParser()
parser.add_argument("-d","--debug", action="store_true", default= False, help="add verbosity")
parser.add_argument("-p","--port", nargs = 1, metavar =("Daemon Listening port"), help="default is " + str(DEFAULT_LISTENPORT))
parser.add_argument("-s","--snapcastPort", nargs = 1, metavar =("snapcast port"), help="snapcast port")
parser.add_argument("-l","--log", nargs = 1, metavar =("log File"), default= False, help=" path file to save log")
parser.add_argument('-v', '--version', action='version', version= VERSION  + "\n" +  AUTHOR)
  


def handler(signum, frame):
    print('\r\nYou pressed Ctrl+C! Game Over...')
    os._exit(0)



class SnapCastHTTPServer(HTTPServer):

    def __init__(self, host, port ,*args, **kwargs):
        HTTPServer.__init__(self, *args, **kwargs)
        log.debug(host,port)  
        self.context = telnetlib.Telnet(host, port)



class SnapCastHttp(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        self.send_response(400)
#        self.wfile.write("<html><body><h1>hi!</h1></body></html>")

    def do_HEAD(self):
        self._set_headers()
        self.send_response(400)

    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        log.debug(str(post_data))
        try:
        	reply =  self.doRequestToSnapChat( post_data )
		self._set_headers()
                log.debug(json.dumps(reply)) 
  	  	self.wfile.write(json.dumps(reply))

        except:
               self._set_headers()
	       self.send_response(400)

    def doRequestToSnapChat(self,j):
	telnet= self.server.context
        if telnet is None :
		log.error("telnet obj is NONE!")
    	jobj = json.loads(j)
    	file = j.replace('\n', '')
    	log.debug(file  + "\r\n")
    	requestId = jobj['id']
    	telnet.write( file + "\r\n")
    	while (True):
        	response = telnet.read_until("\r\n", 2)
        	jResponse = json.loads(response)
        	if 'id' in jResponse:
            		if jResponse['id'] == requestId:
				log.debug(jResponse)	
                		return jResponse;
    	return;



def run(port , server_class=SnapCastHTTPServer, handler_class=SnapCastHttp , snapcastPort = DEFAULT_PORT_SNAPCAST):
    server_address = ('', port)
    httpd = server_class('127.0.0.1',snapcastPort,server_address, handler_class)
    log.info ('Starting Snapcast Httpd on port ' + str(port))
    httpd.serve_forever()


if __name__=='__main__':

	signal.signal(signal.SIGINT, handler)        
	args = parser.parse_args()
 	   
	portHttp = DEFAULT_LISTENPORT
	snapPort = DEFAULT_PORT_SNAPCAST 
	
    	log = logging.getLogger()
	
	if args.debug:
		log_level = logging.DEBUG 
	else:
		log_level = logging.INFO

	if args.log:    
		logging.basicConfig( filename=args.log[0],
				filemode='w',
				format='%(asctime)s,%(levelname)s %(message)s',
				datefmt='%H:%M:%S',
				level=log_level)    
	else:
		logging.basicConfig(format='%(asctime)s,%(levelname)s %(message)s',
				datefmt='%H:%M:%S',
				level=log_level)  
	if args.port:
		log.debug("Listenning on port:" + str(args.port[0]) )
		portHttp = int(args.port[0])

	if args.snapcastPort:
		log.debug("setting Snapcast port to: " + str(args.httsport[0]) )
                snapPort = int(args.httsport[0])

        run(port=portHttp ,snapcastPort= snapPort)

        os._exit(0)


