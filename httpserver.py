import socket
import ssl
import os
import threading
from datetime import datetime
from urllib.parse import unquote
CRLF = '\r\n'
ctype = {'html': 'text/html', 'htm': 'text/html', 'txt': 'text/html', 'ico': 'image/x-icon', 'css': 'text/css', 'js': 'application/javascript', 'jpg': 'image/jpeg', 'png': 'image/png', 'gif': 'image/gif', 'mp3': 'audio/mp3', 'ogg': 'audio/ogg', 'wav': 'audio/wav', 'opus': 'audio/opus', 'mp4': 'video/mp4', 'webm': 'video/webm', 'other':'application/octet-stream'}
cache = {}
cache_num = []
MAX_LEN = 5
SSL = False
def handle(sock, addr):
    global cache
    global cache_num
    try:
        request = sock.recv(2048)
        temp = request.decode().split('\r\n')
        try:
            method, path, _http = temp[0].split(' ')
        except:
            pass
        else:
            protocol, headers = _http.split('/')
            path = unquote(path)
           
            if path == '/':
                sock.send(('HTTP/1.1 200 OK' + CRLF).encode())
                sock.send((f'Content-Type: {ctype["html"]}' + CRLF * 2).encode())
                sock.send(f'<meta charset="utf-8">{CRLF}'.encode())
                if 'index.html' in os.listdir():
                    if path in cache:
                        sock.send(cache[path])
                    else:
                        webfile = open('index.html', 'rb')
                        readfile = webfile.read()
                        sock.send(readfile)
                        webfile.close()
                        if not len(cache) > MAX_LEN:
                            cache[path] = readfile
                            cache_num.append(path)
                        else:
                            del cache[cache_num[0]]
                            cache[path] = readfile
                            cache_num.pop(0)
    
                elif 'index.htm' in os.listdir():
                    if path in cache:
                        sock.send(cache[path])
                    else:
                        webfile = open('index.htm', 'rb')
                        readfile = webfile.read()
                        sock.send(readfile)
                        webfile.close()
                        if not len(cache) > MAX_LEN:
                            cache[path] = readfile
                            cache_num.append(path)
                        else:
                            del cache[cache_num[0]]
                            cache[path] = readfile
                            cache_num.pop(0)
                            cache_num.append(path)

                else:
                    if path in cache:
                        sock.send(cache[path].encode())
                    else:
                        data = f'<h1>Directory listing for {path}</h1>{CRLF}<hr>{CRLF}<ul>{CRLF}'
                        for i in os.listdir(os.getcwd() + path):
                            if os.path.isdir(os.getcwd() + path + "/" + i):
                                data += f'<li><a href="{i}/">{i}</a></li>{CRLF}'
                            else:
                                data += f'<li><a href="{i}">{i}</a></li>{CRLF}'
                        data += f'</ul>{CRLF}'
                        data += f'<hr>{CRLF}'
                        sock.send(data.encode())
                        if len(cache) < MAX_LEN:
                            
                            cache[path] = data
                            cache_num.append(path)
                        else:
                            del cache[cache_num[0]]
                            cache[path] = data
                            cache_num.pop(0)
                            cache_num.append(path)
                    
            
            else:
                    if os.path.exists(path.split('/', 1)[1]):
                        sock.send(('HTTP/1.1 200 OK' + CRLF).encode())
                        if os.path.isfile(os.getcwd() + path):
                            ext = path.split('/', 1)[1].split('.')[-1]
                            if path in cache:
                                sock.send(cache[path])
                            else:
                                webfile = open(path.split('/', 1)[1], 'rb')
                                if ext in ctype:
                                    sock.send((f'Content-Type: {ctype[ext]}' + CRLF * 2).encode())
                                    _type = (f'Content-Type: {ctype[ext]}' + CRLF * 2).encode()
                                    readfile = webfile.read()
                                    sock.send(readfile)
                                    webfile.close()
                                    if len(cache) < MAX_LEN:
                                        cache[path] = _type + readfile
                                        cache_num.append(path)
                                    else:
                                        del cache[cache_num[0]]
                                        cache[path] = _type + readfile
                                        cache_num.pop(0)
                                        cache_num.append(path)
                        
                                else:
                                    sock.send((f'Content-Type: {ctype["other"]}' + CRLF * 2).encode())
                                    _type = (f'Content-Type: {ctype["other"]}' + CRLF * 2).encode()
                                    readfile = webfile.read()
                                    sock.send(readfile)
                                    webfile.close()
                                    if len(cache) < MAX_LEN:
                                        cache[path] = _type + readfile
                                        cache_num.append(path)
                                    else:
                                        del cache[cache_num[0]]
                                        cache[path] = _type + readfile
                                        cache_num.pop(0)
                                        cache_num.append(path)
                        else:
                            sock.send((f'Content-Type: {ctype["html"]}' + CRLF * 2).encode())
                            sock.send(f'<meta charset="utf-8">{CRLF}'.encode())
                            if path in cache:
                                sock.send(cache[path])
                            else:
                                
                                if 'index.html' in os.listdir(os.getcwd() + path):
                                    webfile = open(path.split('/', 1)[1] + '/index.html', 'rb')
                                    data = webfile.read()
                                    sock.send(data)
                                    webfile.close()
                                    if len(cache) < MAX_LEN:
                                        cache[path] = data
                                        cache_num.append(path)
                                    else:
                                        del cache[cache_num[0]]
                                        cache[path] = data
                                        cache_num.pop(0)
                                        cache_num.append(path)
    
                                elif 'index.htm' in os.listdir(os.getcwd() + path):
                                    data = webfile.read()
                                    sock.send(data)
                                    webfile.close()
                                    if len(cache) < MAX_LEN:
                                        cache[path] = data
                                        cache_num.append(path)
                                    else:
                                        del cache[cache_num[0]]
                                        cache[path] = data
                                        cache_num.pop(0)
                                        cache_num.append(path)
                                else:
                                    data = f'<h1>Directory listing for {path}</h1>{CRLF}'.encode()
                                    data += f'<hr>{CRLF}'.encode()
                                    data += f'<ul>{CRLF}'.encode()
                                    for i in os.listdir(os.getcwd() + path):
                                        if os.path.isdir(os.getcwd() + path + "/" + i):
                                            data += f'<li><a href="{path + "/" + i}/">{i}</a></li>{CRLF}'.encode()
                                        else:
                                            data += f'<li><a href="{path + "/" + i}">{i}</a></li>{CRLF}'.encode()
                                    data += f'</ul>{CRLF}'.encode()
                                    data += f'<hr>{CRLF}'.encode()
                                    sock.send(data)
                                    if len(cache) < MAX_LEN:
                                        cache[path] = data
                                        cache_num.append(path)
                                    else:
                                        del cache[cache_num[0]]
                                        cache[path] = data
                                        cache_num.pop(0)
                                        cache_num.append(path)
                    
                    else:
                        sock.send(('HTTP/1.1 404 Not Found' + CRLF).encode())
                        sock.send((f'Content-Type: {ctype["html"]}' + CRLF * 2).encode())
                        sock.send(b'<h1>404 Page not found</h>')
                
    except ConnectionResetError:
        pass

    except ConnectionAbortedError:
        pass
    
    except:
        sock.send(('HTTP/1.1 500 Internal Server Error' + CRLF).encode())
        sock.send((f'Content-Type: {ctype["html"]}' + CRLF * 2).encode())
        sock.send(b'<h1>500 Internal Server Error</h>')

    finally:
        sock.close()



if __name__ == '__main__':
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if SSL:
        s = ssl.wrap_socket (s, certfile='cert.crt', keyfile='private.key', server_side=True)
        s.bind(('', 443))
    else:
        s.bind(('', 80))
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.listen(0)

    while True:
        try:
            clientsock, clientaddress = s.accept()
            threading.Thread(target=handle, args=(clientsock, clientaddress)).start()
        except:
            pass

