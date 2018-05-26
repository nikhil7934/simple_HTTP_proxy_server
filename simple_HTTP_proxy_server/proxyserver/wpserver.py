import os
import time
import sys
import socket
import select

cache_title={}
k=-1
cache_data={}
cache_time={}
cache_count={}

HOST = ""
PORT = 12345

def find_n(fname):
	for i,j in cache_title.items():

		if j == fname:
			return i


def cache_mod(request,conn,client_addr,num):
	first_line = request.split('\n')[0]

	# extracting url from firstline of data
	if first_line.split(' ')[0] == "GET":
		url = first_line.split(' ')[1]

		http_pos = url.find("://")
		if (http_pos==-1):
			temp = url
		else:
			temp = url[(http_pos+3):]
		port_pos = temp.find(":")
		webserver_pos = temp.find("/")
		if webserver_pos == -1:
			webserver_pos = len(temp)
		webserver = ""
		port = -1
		if (port_pos==-1 or webserver_pos < port_pos):
			port = 20000
			webserver = temp[:webserver_pos]
		else:
			port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
			webserver = temp[:port_pos]
		print "Connect to:", webserver, port
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		time.sleep(0.01)
		s.connect(("",port))
		request = request.split('\n')
		l1 = request[0].split(' ')
		lw = url[::-1]
		l1[1] = (lw[:lw.find('/')+1])[::-1]
		request[0] = ' '.join(l1)
		request = '\n'.join(request)
		s.sendall(request)
		print "request After", request
		cache=''
		data=s.recv(4096)
		time.sleep(0.1)
		if data.split('\n')[0].split(' ')[1]=='304':
			print(cache_data[num])
			time.sleep(0.1)
			conn.send(cache_data[num])
			time.sleep(0.1)
			cache_count[num]=0
		else:	
			cache+=data
			time.sleep(0.1)
			conn.send(data)
			time.sleep(0.1)
			while 1:
				data = s.recv(4096)
				time.sleep(0.1)
				if (len(data) > 0):
					time.sleep(0.1)
					conn.send(data)
					time.sleep(0.1)
					cache=cache+data
				else:
					break
		

			if cache.split('\n')[0].split(' ')[1]!='404' and 'no-cache' not in cache.split('\n')[6]:
				#print("sdhgjsgdk\n\n")
				cache_data[num]=cache
				cache_time[num]=cache.split('\n')[5].split('Last-Modified: ')[1].strip('\r')
				cache_count[num]=0
		s.close()
		time.sleep(1)				



try:
    na = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    na.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    na.bind((HOST, PORT)) # associate the socket to host and port
    na.listen(5) # listenning
    print "Serving on port 12345"
except socket.error, (value, message):
    if na:
        na.close()
    print "Could not open socket:", message
    sys.exit(1)
# Now getting requests from client
tu = 1
while 1:
	# accepting the client request
	conn, client_addr = na.accept()
	# read the http message from client
	time.sleep(0.1)
	request = conn.recv(4096)
	print request
	if request.split('\n')[0].split(' ')[0] == "GET":
		fname=request.split('\n')[0].split('://')[1].split('/')[1].split(' ')[0]
		print(fname)
	
	if request.split('\n')[0].split(' ')[0] == "GET" and fname in cache_title.values():
		num=find_n(fname)
		print(num)
		cache_count[num]+=1

		if(cache_count[num]>=2):
			ff=request.split('\n')
			kk='If-Modified-Since: '+cache_time[num]
			ff.insert(1,kk)
			request='\n'.join(ff)
			cache_mod(request,conn,client_addr,num)
		else:
			time.sleep(0.1)
			conn.send(cache_data[num])
	else:	
		first_line = request.split('\n')[0]

		# extracting url from firstline of data
		if first_line and first_line.split(' ')[0] == "GET":
			url = first_line.split(' ')[1]

			http_pos = url.find("://")
			if (http_pos==-1):
				temp = url
			else:
				temp = url[(http_pos+3):]
			port_pos = temp.find(":")
			webserver_pos = temp.find("/")
			if webserver_pos == -1:
				webserver_pos = len(temp)
			webserver = ""
			port = -1
			if (port_pos==-1 or webserver_pos < port_pos):
				port = 20000
				webserver = temp[:webserver_pos]
			else:
				port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
				webserver = temp[:port_pos]
			print "Connect to:", webserver, port
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			time.sleep(0.01)
			s.connect(("",port))
			request = request.split('\n')
			l1 = request[0].split(' ')
			lw = url[::-1]
			l1[1] = (lw[:lw.find('/')+1])[::-1]
			request[0] = ' '.join(l1)
			request = '\n'.join(request)
			s.sendall(request)
			print "request After\n", request
			cache=''
			while 1:
				data = s.recv(4096)
				time.sleep(0.1)
				if (len(data) > 0):
					time.sleep(0.1)
					conn.send(data)
					time.sleep(0.1)
					cache=cache+data
				else:
					break
		

			if cache.split('\n')[0].split(' ')[1]!='404' and 'no-cache' not in cache.split('\n')[6]:
				k=(k+1)%3
				cache_title[k]=fname
				cache_data[k]=cache
				cache_time[k]=cache.split('\n')[5].split('Last-Modified: ')[1]
				cache_count[k]=int(0)
				print(cache_time)				
			s.close()
			time.sleep(1)
	conn.close()
na.close()