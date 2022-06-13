import socket
import ssl
import os
import sys
import json
import subprocess
import threading
import argparse
from urllib.parse import unquote
CRLF = '\r\n'
ctype = {'html': 'text/html', 'htm': 'text/html', 'txt': 'text/html', 'ico': 'image/x-icon', 'css': 'text/css', 'js': 'application/javascript', 'jpg': 'image/jpeg', 'png': 'image/png', 'gif': 'image/gif', 'mp3': 'audio/mp3', 'ogg': 'audio/ogg', 'wav': 'audio/wav', 'opus': 'audio/opus', 'm4a': 'audio/mp4', 'mp4': 'video/mp4', 'webm': 'video/webm', 'pdf': 'application/pdf', 'other':'application/octet-stream'}
cache = {}
cache_num = []
cache_max_len = 512 * 1024
cgi_directories = ['cgi-bin', 'htbin']
MAX_LEN = int()
port = int()
SSL = False

def length(file):
    num = 0
    for i in file:
        num += len(i)
    return num

def setcache(data, path):
    global cache
    global cache_num
    if len(cache) < MAX_LEN:
        cache[path] = data
        cache_num.append(path)
    else:
        try:
            del cache[cache_num[0]]
            cache[path] = data
            cache_num.pop(0)
            cache_num.append(path)
        except:
            cache = {}
            cache_num = []

def socksend(sock, code, ext, data=None, datalen=0, fileobj=None, Accept_Ranges = False, Content_Range = False, Content_Range_Data = (), method='GET'):
    try:
        if data:
            datalen = len(data)
        sock.sendall((f'HTTP/1.1 {code}' + CRLF).encode())
        sock.sendall(('Server: Notum' + CRLF).encode())
        if Accept_Ranges:
            sock.sendall(('Accept-Ranges: bytes' + CRLF).encode())
        sock.sendall(('Connection: close' + CRLF).encode())
        if Content_Range:
            _range, lendata = Content_Range_Data
            sock.sendall((f'Content-Range: bytes {_range}-{lendata - 1}/{lendata}' + CRLF).encode())
        sock.sendall((f'Content-Length: {datalen}' + CRLF).encode())
        sock.sendall((f'Content-Type: {ctype[ext]}; charset=UTF-8' + CRLF * 2).encode())
        if method == 'GET' or method == 'POST':
            if fileobj == None:
                sock.sendall(data)
            else:
                if code == 206:
                    for i in fileobj:
                        sock.sendall(i)
                else:
                    sock.sendfile(fileobj)
    except BrokenPipeError:
        pass

def handler(sock):
    try:
        recv = sock.recv(4096)
        temp = recv.decode().split('\r\n')
        client_headers = {}
        try:
            method, path, _ = temp[0].split(' ')
            for i in temp[1:-2]:
                client_headers[i.split(': ')[0]] = i.split(': ')[1]
        except:
#---------------------------400---------------------------
            socksend(sock, 400, 'html', b'<h1>400 Bad Request</h>')
#---------------------------------------------------------

        else:
            if method == 'GET':
                if len(unquote(path).split('?', 1)) == 2:
                    path, cgiargs = unquote(path.replace('+', ' ')).split('?', 1)
                    print(path, cgiargs)

                elif len(unquote(path).split('?', 1)) == 1:
                    path = unquote(path)
                    cgiargs = str()

            elif method == 'POST':
                path = unquote(path)
                cgiargs = temp[-1]
#---------------------------200---------------------------
            if path == '/':
                
                if 'index.html' in os.listdir():
                    if path in cache:
                        socksend(sock, 200, 'html', cache[path])
                    else:
                        webfile = open('index.html', 'rb')
                        data = webfile.read()
                        webfile.seek(0)
                        socksend(sock, 200, 'html', data, webfile, method=method)
                        webfile.close()
                        if len(data) < cache_max_len:
                            threading.Thread(target=setcache, args=(data, path)).start()
                        
    
                elif 'index.htm' in os.listdir():
                    if path in cache:
                        socksend(sock, 200, 'htm', cache[path])
                    else:
                        webfile = open('index.htm', 'rb')
                        data = webfile.read()
                        webfile.seek(0)
                        socksend(sock, 200, 'html', data, webfile, method=method)
                        webfile.close()
                        if len(data) < cache_max_len:
                            threading.Thread(target=setcache, args=(data, path)).start()


                else:
                    if path in cache:
                        socksend(sock, 200, 'html', cache[path])
                    else:
                        data = f'<h1>Directory listing for {path}</h1>{CRLF}<hr>{CRLF}<ul>{CRLF}'.encode()
                        for i in os.listdir(os.getcwd() + path):
                            if os.path.isdir(os.getcwd() + path + "/" + i):
                                data += f'<li><a href="{i}/">{i}</a></li>{CRLF}'.encode()
                            else:
                                data += f'<li><a href="{i}">{i}</a></li>{CRLF}'.encode()
                        data += f'</ul>{CRLF}'.encode()
                        data += f'<hr>{CRLF}'.encode()
                        socksend(sock, 200, 'html', data, method=method)
                        if len(data) < cache_max_len:
                            threading.Thread(target=setcache, args=(data, path)).start()
                    
            
            else:
                if os.path.exists(path.split('/', 1)[1]):
                        if os.path.isfile(os.getcwd() + path):
                            ext = path.split('/', 1)[1].split('.')[-1]
#---------------------------206---------------------------
                            if 'Range' in client_headers:
                                _range = int(client_headers['Range'].split('=')[1][:-1])
                                webfile = open(path.split('/', 1)[1], 'rb')
                                with open(path.split('/', 1)[1], 'rb') as lenfile:
                                    lendata = length(lenfile)
                                webfile.seek(_range)
                                datalen = length(webfile)
                                webfile.seek(_range)
                                socksend(sock, 206, ext, datalen=datalen, fileobj=webfile, Accept_Ranges=True, Content_Range=True, Content_Range_Data=(_range, lendata), method=method)
                                webfile.close()
#---------------------------------------------------------
                            else:
#---------------------------cgi---------------------------
                                if CGI_enable:
                                    if path.split('/')[-2] in cgi_directories:
                                        if sys.platform == 'win32':
                                            interpreter = 'python'
                                            
                                        if sys.platform == 'linux' or sys.platform == 'linux2':
                                            interpreter = 'python3'
                                            
                                        args = [interpreter, path[1:], cgiargs, json.dumps(client_headers)]
                                        process = subprocess.Popen(args, stdout=subprocess.PIPE, universal_newlines=True)
                                        httpcode = 200
                                        content_type = 'html'
                                        data = process.communicate()[0][:-1]
                                        data = data.replace('\n', '')
                                        if '!ntc' in data:
                                            for i in data.split('::;')[:-1]:
                                                command, outarg = i.split('!ntc::')[1].split('=')
                                                if command == 'httpcode':
                                                    httpcode = int(outarg)
                                                if command == 'content-type':
                                                    if outarg in ctype:
                                                        content_type = outarg
                                            data = data.split('::;')[-1]
                                        socksend(sock, httpcode, content_type, data.encode(), method=method)
#---------------------------------------------------------
#---------------------------cache-------------------------
                                if path in cache:
                                    sock.sendall(cache[path])
#---------------------------------------------------------
                                else:
                                    webfile = open(path.split('/', 1)[1], 'rb')
#---------------------------in-ctype----------------------
                                    if ext in ctype:
                                        datalen = length(webfile)
                                        _type = (('HTTP/1.1 200 OK' + CRLF).encode())
                                        _type += (('Server: Notum' + CRLF).encode())
                                        _type += (('Accept-Ranges: bytes' + CRLF).encode())
                                        _type += ((f'Content-Length: {datalen}' + CRLF).encode())
                                        _type += ((f'Content-Type: {ctype[ext]}; charset=UTF-8' + CRLF * 2).encode())
                                        webfile.seek(0)
                                        socksend(sock, 200, ext, datalen=datalen, fileobj=webfile, Accept_Ranges=True, method=method)
#---------------------------------------------------------
                        
                                    else:
#---------------------------octet-stream------------------
                                        datalen = length(webfile)
                                        _type = (('HTTP/1.1 200 OK' + CRLF).encode())
                                        _type += (('Server: Notum' + CRLF).encode())
                                        _type += ((f'Content-Length: {datalen}' + CRLF).encode())
                                        _type += ((f'Content-Type: {ctype["other"]}' + CRLF * 2).encode())
                                        webfile.seek(0)
                                        socksend(sock, 200, 'other', datalen=datalen, fileobj=webfile, method=method)
#---------------------------------------------------------
                                    webfile.close()
                        
                        else:
#---------------------------cache-------------------------
                            if path in cache:
                                socksend(sock, 200, 'html', cache[path])
#---------------------------------------------------------
                            else:
#---------------------------other-directory-index.html----
                                if 'index.html' in os.listdir(os.getcwd() + path):
                                    webfile = open(path.split('/', 1)[1] + '/index.html', 'rb')
                                    data = webfile.read()
                                    webfile.seek(0)
                                    socksend(sock, 200, 'html', data, webfile, method=method)
                                    webfile.close()
                                    if len(data) < cache_max_len:
                                        threading.Thread(target=setcache, args=(data, path)).start()
#---------------------------------------------------------
#---------------------------other-directory-index.htm-----
                                elif 'index.htm' in os.listdir(os.getcwd() + path):
                                    webfile = open(path.split('/', 1)[1] + '/index.html', 'rb')
                                    data = webfile.read()
                                    webfile.seek(0)
                                    socksend(sock, 200, 'html', data, webfile, method=method)
                                    webfile.close()
                                    if len(data) < cache_max_len:
                                        threading.Thread(target=setcache, args=(data, path)).start()
#---------------------------------------------------------
                                else:
#---------------------------403---------------------------
                                    if path.split('/')[-2] in cgi_directories:
                                        socksend(sock, 403, 'html', '<h1>403 Forbidden</h>'.encode(), method=method)
#---------------------------------------------------------
                                    else:
#---------------------------other-directory-listing-------
                                        data = f'<h1>Directory listing for {path}</h1>{CRLF}'.encode()
                                        data += f'<hr>{CRLF}'.encode()
                                        data += f'<ul>{CRLF}'.encode()
                                        for i in os.listdir(os.getcwd() + path):
                                            if os.path.isdir(os.getcwd() + path + "/" + i):
                                                data += f'<li><a href="{path + i}/">{i}</a></li>{CRLF}'.encode()
                                            else:
                                                data += f'<li><a href="{path + i}">{i}</a></li>{CRLF}'.encode()
                                        data += f'</ul>{CRLF}'.encode()
                                        data += f'<hr>{CRLF}'.encode()
                                        socksend(sock, 200, 'html', data, method=method)
                                        if len(data) < cache_max_len:
                                            threading.Thread(target=setcache, args=(data, path)).start()
#---------------------------------------------------------
#---------------------------------------------------------
#---------------------------404---------------------------
                else:
                    socksend(sock, 404, 'html', b'<h1>404 Page not found</h>', method=method)
#---------------------------------------------------------
                
    except ConnectionResetError:
        pass

    except ConnectionAbortedError:
        pass

    except KeyboardInterrupt:
        sys.exit(0)
#---------------------------500---------------------------
    except Exception as ex:
        socksend(sock, 500, 'html', ('<h1>500 Internal Server Error</h><br>' + str(ex)).encode(), method=method)
#---------------------------------------------------------

    finally:
        sock.close()


#---------------------------start-------------------------
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--SSL', nargs='+')
    parser.add_argument('-p', '--port')
    parser.add_argument('-rd', '--root-dir')
    parser.add_argument('-mcl', '--max-cache-len')
    parser.add_argument('-cgi', '--CGI', action='store_true')
    args = parser.parse_args()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if not args.root_dir == None:
        os.chdir(args.root_dir)

    if args.CGI:
        CGI_enable = True
    else:
        CGI_enable = False

    if not args.max_cache_len == None:
        MAX_LEN = args.max_cache_len
    
    if not args.SSL == None:
        SSL = True

    if SSL:
        s = ssl.wrap_socket (s, certfile=args.SSL[0], keyfile=args.SSL[1], server_side=True, ssl_version="TLSv1")
        port = 443
    else:
        port = 80
        if not args.port == None:
            port = int(args.port)
    try:
        s.bind(('', port))
    except OSError as e:
        print('Error:', e)
        sys.exit(0)
    s.listen(0)

    while True:
        try:
            clientsock, clientaddress = s.accept()
            threading.Thread(target=handler, args=(clientsock,)).start()
        except KeyboardInterrupt:
            sys.exit(0)
        except:
            pass
#---------------------------------------------------------
