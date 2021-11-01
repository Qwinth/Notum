import socket
import os
import threading
from datetime import datetime
from urllib.parse import unquote
CRLF = '\r\n'
ctype = {'html': 'text/html', 'htm': 'text/html', 'txt': 'text/html', 'ico': 'image/x-icon', 'css': 'text/css', 'js': 'application/javascript', 'jpg': 'image/jpeg', 'png': 'image/png', 'gif': 'image/gif', 'mp3': 'audio/mp3', 'ogg': 'audio/ogg', 'wav': 'audio/wav', 'mp4': 'video/mp4', 'webm': 'video/webm'}

def handle(sock, addr):
    try:
        request = sock.recv(1024)
        temp = request.decode().split('\r\n')
        try:
            method, path, _http = temp[0].split(' ')
        except:
            pass
        else:
            protocol, headers = _http.split('/')
            path = unquote(path)
            if os.path.exists(os.getcwd() + path):
                print(f'[{str(datetime.now()).split(".")[0]}] {addr[0]} {method} {path} 200 OK')

            elif not os.path.exists(path.split('/', 1)[1]):
                print(f'[{str(datetime.now()).split(".")[0]}] {addr[0]} {method} {path} 404 File not found')

            #print(method, path, _http)
            sock.send(('HTTP/1.1' + CRLF).encode())
            if path == '/':
                sock.send((f'Content-Type: {ctype["html"]}' + CRLF * 2).encode())
                sock.send(b'<meta charset="utf-8">')
                if 'index.html' in os.listdir():
                    webfile = open('index.html', 'rb')
                    sock.send(webfile.read())
                    webfile.close()
    
                elif 'index.htm' in os.listdir():
                    webfile = open('index.htm', 'rb')
                    sock.send(webfile.read())
                    webfile.close()

                else:
                    for i in os.listdir(os.getcwd() + path):
                        if os.path.isdir(os.getcwd() + path + "/" + i):
                            sock.send(f'<a href="{i}/">{i}</a><br>'.encode())
                        else:
                            sock.send(f'<a href="{i}">{i}</a><br>'.encode())
            
            else:
                    if os.path.exists(path.split('/', 1)[1]):
                        if os.path.isfile(os.getcwd() + path):
                            ext = path.split('/', 1)[1].split('.')[-1]
                            webfile = open(path.split('/', 1)[1], 'rb')
                            if ext in ctype:
                                sock.send((f'Content-Type: {ctype[ext]}' + CRLF * 2).encode())
                                sock.send(webfile.read())
                                webfile.close()
                        
                            else:
                                sock.send(webfile.read())
                                webfile.close()
                        else:
                            sock.send((f'Content-Type: {ctype["html"]}' + CRLF * 2).encode())
                            sock.send(b'<meta charset="utf-8">')
                            if 'index.html' in os.listdir(os.getcwd() + path):
                                webfile = open(path.split('/', 1)[1] + '/index.html', 'rb')
                                sock.send(webfile.read())
                                webfile.close()
    
                            elif 'index.htm' in os.listdir(os.getcwd() + path):
                                webfile = open(path.split('/', 1)[1] + '/index.htm', 'rb')
                                sock.send(webfile.read())
                                webfile.close()
                            else:
                                for i in os.listdir(os.getcwd() + path):
                                    if os.path.isdir(os.getcwd() + path + "/" + i):
                                        sock.send(f'<a href="{path + "/" + i}/">{i}</a><br>'.encode())
                                    else:
                                        sock.send(f'<a href="{path + "/" + i}">{i}</a><br>'.encode())
                    
                    else:
                        sock.send((f'Content-Type: {ctype["html"]}' + CRLF * 2).encode())
                        sock.send(b'<h1>404 Page not found</h>')
                
                
            sock.close()
    except ConnectionResetError:
        pass



if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 80))
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.listen(0)

    while True:
        clientsock, clientaddress = s.accept()
        threading.Thread(target=handle, args=(clientsock, clientaddress)).start()
