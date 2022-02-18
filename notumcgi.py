import json
import sys
class CGI:
    def __init__(self):
        self.args = sys.argv[1]
        self.client_headers = json.loads(sys.argv[2])
        self.fargs = {}

    def getclheaders(self, inkey=None):
        if inkey == None:
            data = self.client_headers
        else:
            try:
                data = self.client_headers[inkey]
            except:
                data = None
        return data

    def getargs(self, inkey=None):
        data = self.args.split('&')
        for i in data:
            key = i.split('=')[0]
            if not key:
                key = None
            try:
                value = i.split('=')[1]
                self.fargs[key] = value
            except:
                self.fargs[key] = None
        if inkey == None:
            temp = self.fargs
        else:
            try:
                temp = self.fargs[inkey]
            except:
                temp = None
        return temp

    def setcode(self, code):
        sys.stdout.write(f'!ntc::httpcode={code}::;')
    
    def setctype(self, ctype):
        sys.stdout.write(f'!ntc::content-type={ctype}::;')