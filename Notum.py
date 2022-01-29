import socket
import ssl
import os
import sys
import threading
import argparse
from urllib.parse import unquote
CRLF = '\r\n'
ctype = {'html': 'text/html', 'htm': 'text/html', 'txt': 'text/html', 'ico': 'image/x-icon', 'css': 'text/css', 'js': 'application/javascript', 'jpg': 'image/jpeg', 'png': 'image/png', 'gif': 'image/gif', 'mp3': 'audio/mp3', 'ogg': 'audio/ogg', 'wav': 'audio/wav', 'opus': 'audio/opus', 'm4a': 'audio/mp4', 'mp4': 'video/mp4', 'webm': 'video/webm', 'pdf': 'application/pdf', 'other':'application/octet-stream'}
cache = {}
cache_num = []
cache_max_len = 512 * 1024
MAX_LEN = int()
port = int()
SSL = False

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
            


def handle(sock, addr):
    try:
        request = sock.recv(4096)
        temp = request.decode().split('\r\n')
        try:
            method, path, _http = temp[0].split(' ')
        except:
#---------------------------400---------------------------
            sock.send(('HTTP/1.1 400 Bad Request' + CRLF).encode())
            sock.send(('Server: Notum' + CRLF).encode())
            sock.send((f'Content-Type: {ctype["html"]}' + CRLF * 2).encode())
            sock.send(b'<h1>400 Bad Request</h>')
#---------------------------------------------------------
        else:
            protocol, headers = _http.split('/')
            path = unquote(path)
#---------------------------200---------------------------
            if path == '/':
                
                if 'index.html' in os.listdir():
                    if path in cache:
                        sock.send(('HTTP/1.1 200 OK' + CRLF).encode())
                        sock.send(('Server: Notum' + CRLF).encode())
                        sock.send(('Accept-Ranges: bytes' + CRLF).encode())
                        sock.send((f'Content-Length: {len(cache[path])}' + CRLF).encode())
                        sock.send((f'Content-Type: {ctype["html"]}; charset=UTF-8' + CRLF * 2).encode())
                        sock.send(cache[path])
                    else:
                        webfile = open('index.html', 'rb')
                        readfile = webfile.read()
                        sock.send(('HTTP/1.1 200 OK' + CRLF).encode())
                        sock.send(('Server: Notum' + CRLF).encode())
                        sock.send(('Accept-Ranges: bytes' + CRLF).encode())
                        sock.send((f'Content-Length: {len(readfile)}' + CRLF).encode())
                        sock.send((f'Content-Type: {ctype["html"]}; charset=UTF-8' + CRLF * 2).encode())
                        sock.send(readfile)
                        webfile.close()
                        if len(readfile) < cache_max_len:
                            threading.Thread(target=setcache, args=(readfile, path)).start()
                        
    
                elif 'index.htm' in os.listdir():
                    if path in cache:
                        sock.send(('HTTP/1.1 200 OK' + CRLF).encode())
                        sock.send(('Server: Notum' + CRLF).encode())
                        sock.send(('Accept-Ranges: bytes' + CRLF).encode())
                        sock.send((f'Content-Length: {len(cache[path])}' + CRLF).encode())
                        sock.send((f'Content-Type: {ctype["htm"]}; charset=UTF-8' + CRLF * 2).encode())
                        sock.send(cache[path])
                    else:
                        webfile = open('index.htm', 'rb')
                        readfile = webfile.read()
                        sock.send(('HTTP/1.1 200 OK' + CRLF).encode())
                        sock.send(('Server: Notum' + CRLF).encode())
                        sock.send(('Accept-Ranges: bytes' + CRLF).encode())
                        sock.send((f'Content-Length: {len(readfile)}' + CRLF).encode())
                        sock.send((f'Content-Type: {ctype["htm"]}; charset=UTF-8' + CRLF * 2).encode())
                        sock.send(readfile)
                        webfile.close()
                        if len(readfile) < cache_max_len:
                            threading.Thread(target=setcache, args=(readfile, path)).start()


                else:
                    if path in cache:
                        sock.send(('HTTP/1.1 200 OK' + CRLF).encode())
                        sock.send(('Server: Notum' + CRLF).encode())
                        sock.send(('Accept-Ranges: bytes' + CRLF).encode())
                        sock.send((f'Content-Length: {len(cache[path])}' + CRLF).encode())
                        sock.send((f'Content-Type: {ctype["html"]}; charset=UTF-8' + CRLF * 2).encode())
                        sock.send(cache[path])
                    else:
                        data = f'<h1>Directory listing for {path}</h1>{CRLF}<hr>{CRLF}<ul>{CRLF}'.encode()
                        for i in os.listdir(os.getcwd() + path):
                            if os.path.isdir(os.getcwd() + path + "/" + i):
                                data += f'<li><a href="{i}/">{i}</a></li>{CRLF}'.encode()
                            else:
                                data += f'<li><a href="{i}">{i}</a></li>{CRLF}'.encode()
                        data += f'</ul>{CRLF}'.encode()
                        data += f'<hr>{CRLF}'.encode()
                        sock.send(('HTTP/1.1 200 OK' + CRLF).encode())
                        sock.send(('Server: Notum' + CRLF).encode())
                        sock.send(('Accept-Ranges: bytes' + CRLF).encode())
                        sock.send((f'Content-Length: {len(data)}' + CRLF).encode())
                        sock.send((f'Content-Type: {ctype["html"]}; charset=UTF-8' + CRLF * 2).encode())
                        sock.send(data)
                        if len(data) < cache_max_len:
                            threading.Thread(target=setcache, args=(data, path)).start()
                    
            
            else:
                if os.path.exists(path.split('/', 1)[1]):
                        if os.path.isfile(os.getcwd() + path):
                            ext = path.split('/', 1)[1].split('.')[-1]
#---------------------------206---------------------------
                            range_temp = temp[5]
                            if range_temp.split(' ')[0] == 'Range:':
                                _range = int(range_temp.split(' ')[1][6:-1])
                                webfile = open(path.split('/', 1)[1], 'rb')
                                lenfile = open(path.split('/', 1)[1], 'rb')
                                lendata = len(lenfile.read())
                                lenfile.close()
                                readfile = webfile.read()[_range:]
                                webfile.close()
                                sock.send(('HTTP/1.1 206 Partial Content' + CRLF).encode())
                                sock.send(('Server: Notum' + CRLF).encode())
                                sock.send(('Accept-Ranges: bytes' + CRLF).encode())
                                sock.send(('Connection: Keep-Alive' + CRLF).encode())
                                sock.send((f'Content-Range: bytes {_range}-{lendata}/{lendata + 1}' + CRLF).encode())
                                sock.send((f'Content-Length: {len(readfile)}' + CRLF).encode())
                                sock.send((f'Content-Type: {ctype[ext]}' + CRLF * 2  ).encode())
                                sock.send(readfile)
#---------------------------------------------------------

                            else:
#---------------------------cache-------------------------
                                if path in cache:
                                    sock.send(cache[path])
#---------------------------------------------------------
                                else:
#---------------------------in-ctype----------------------
                                    webfile = open(path.split('/', 1)[1], 'rb')
                                    if ext in ctype:
                                        
                                        readfile = webfile.read()
                                        sock.send(('HTTP/1.1 200 OK' + CRLF).encode())
                                        sock.send(('Server: Notum' + CRLF).encode())
                                        sock.send(('Accept-Ranges: bytes' + CRLF).encode())
                                        sock.send((f'Content-Length: {len(readfile)}' + CRLF).encode())
                                        sock.send((f'Content-Type: {ctype[ext]}; charset=UTF-8' + CRLF * 2  ).encode())
                                        _type = (('HTTP/1.1 200 OK' + CRLF).encode())
                                        _type += (('Server: Notum' + CRLF).encode())
                                        _type += (('Accept-Ranges: bytes' + CRLF).encode())
                                        _type += ((f'Content-Length: {len(readfile)}' + CRLF).encode())
                                        _type += ((f'Content-Type: {ctype[ext]}; charset=UTF-8' + CRLF * 2).encode())
                                        sock.send(readfile)
#---------------------------------------------------------
                            
                                    else:
#---------------------------otcet-stream------------------
                                        readfile = webfile.read()
                                        sock.send(('HTTP/1.1 200 OK' + CRLF).encode())
                                        sock.send(('Server: Notum' + CRLF).encode())
                                        sock.send(('Accept-Ranges: bytes' + CRLF).encode())
                                        sock.send((f'Content-Length: {len(readfile)}' + CRLF).encode())
                                        sock.send((f'Content-Type: {ctype["other"]}' + CRLF * 2).encode())
                                        _type = (('HTTP/1.1 200 OK' + CRLF).encode())
                                        _type += (('Server: Notum' + CRLF).encode())
                                        _type += (('Accept-Ranges: bytes' + CRLF).encode())
                                        _type += ((f'Content-Length: {len(readfile)}' + CRLF).encode())
                                        _type += ((f'Content-Type: {ctype["other"]}' + CRLF * 2).encode())
                                        sock.send(readfile)
#---------------------------------------------------------
                                    if len(readfile) < cache_max_len:
                                        threading.Thread(target=setcache, args=((_type + readfile), path)).start()
                                    webfile.close()
                        
                        else:
#---------------------------cache-------------------------
                            if path in cache:
                                sock.send(('HTTP/1.1 200 OK' + CRLF).encode())
                                sock.send(('Server: Notum' + CRLF).encode())
                                sock.send(('Accept-Ranges: bytes' + CRLF).encode())
                                sock.send((f'Content-Length: {len(cache[path])}' + CRLF).encode())
                                sock.send((f'Content-Type: {ctype["html"]}; charset=UTF-8' + CRLF * 2).encode())
                                sock.send(cache[path])
#---------------------------------------------------------
                            else:
#---------------------------other-directory-index.html----
                                if 'index.html' in os.listdir(os.getcwd() + path):
                                    webfile = open(path.split('/', 1)[1] + '/index.html', 'rb')
                                    data = webfile.read()
                                    sock.send(('HTTP/1.1 200 OK' + CRLF).encode())
                                    sock.send(('Server: Notum' + CRLF).encode())
                                    sock.send(('Accept-Ranges: bytes' + CRLF).encode())
                                    sock.send((f'Content-Length: {len(data)}' + CRLF).encode())
                                    sock.send((f'Content-Type: {ctype["html"]}; charset=UTF-8' + CRLF * 2).encode())
                                    sock.send(data)
                                    webfile.close()
                                    if len(data) < cache_max_len:
                                        threading.Thread(target=setcache, args=(data, path)).start()
#---------------------------------------------------------
#---------------------------other-directory-index.htm-----
                                elif 'index.htm' in os.listdir(os.getcwd() + path):
                                    data = webfile.read()
                                    sock.send(('HTTP/1.1 200 OK' + CRLF).encode())
                                    sock.send(('Server: Notum' + CRLF).encode())
                                    sock.send(('Accept-Ranges: bytes' + CRLF).encode())
                                    sock.send((f'Content-Length: {len(data)}' + CRLF).encode())
                                    sock.send((f'Content-Type: {ctype["html"]}; charset=UTF-8' + CRLF * 2).encode())
                                    sock.send(data)
                                    webfile.close()
                                    if len(data) < cache_max_len:
                                        threading.Thread(target=setcache, args=(data, path)).start()
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
                                    sock.send(('HTTP/1.1 200 OK' + CRLF).encode())
                                    sock.send(('Server: Notum' + CRLF).encode())
                                    sock.send(('Accept-Ranges: bytes' + CRLF).encode())
                                    sock.send((f'Content-Length: {len(data)}' + CRLF).encode())
                                    sock.send((f'Content-Type: {ctype["html"]}; charset=UTF-8' + CRLF * 2).encode())
                                    sock.send(data)
                                    if len(data) < cache_max_len:
                                        threading.Thread(target=setcache, args=(data, path)).start()
#---------------------------------------------------------
#---------------------------------------------------------
#---------------------------404---------------------------
                else:
                    sock.send(('HTTP/1.1 404 Not Found' + CRLF).encode())
                    sock.send(('Server: Notum' + CRLF).encode())
                    sock.send(('Accept-Ranges: bytes' + CRLF).encode())
                    sock.send((f'Content-Type: {ctype["html"]}; charset=UTF-8' + CRLF * 2).encode())
                    sock.send(b'<h1>404 Page not found</h>')
#---------------------------------------------------------
                
    except ConnectionResetError:
        pass

    except ConnectionAbortedError:
        pass

    except KeyboardInterrupt:
        sys.exit(0)
#---------------------------500---------------------------
    except Exception as ex:
        sock.send(('HTTP/1.1 500 Internal Server Error' + CRLF).encode())
        sock.send(('Server: Notum' + CRLF).encode())
        sock.send((f'Content-Type: {ctype["html"]}; charset=UTF-8' + CRLF * 2).encode())
        sock.send(b'<h1>500 Internal Server Error</h>')
        sock.send(str(ex).encode())
#---------------------------------------------------------

    finally:
        sock.close()


#---------------------------start-------------------------
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--SSL', nargs='+')
    parser.add_argument('-p', '--port')
    parser.add_argument('-rd', '--root-dir')
    parser.add_argument('-mlc', '--max-cache-len')
    args = parser.parse_args()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if not args.root_dir == None:
        os.chdir(args.root_dir)
    
    if not args.max_cache_len == None:
        MAX_LEN = args.max_cache_len
    
    if not args.SSL == None:
        SSL = True
    
    if SSL:
        s = ssl.wrap_socket (s, certfile=args.SSL[0], keyfile=args.SSL[1], server_side=True)
        s.bind(('', 443))
    else:
        port = 80
        if not args.port == None:
            port = int(args.port)
        s.bind(('', port))
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.listen(0)

    while True:
        try:
            clientsock, clientaddress = s.accept()
            threading.Thread(target=handle, args=(clientsock, clientaddress)).start()
        except KeyboardInterrupt:
            sys.exit(0)
        except:
            pass
#---------------------------------------------------------
