import mimetypes
import pathlib
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import socket
import threading
from datetime import datetime
import ast
import json


class HttpHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        print(data)
        data_parse = urllib.parse.unquote_plus(data.decode())
        print(data_parse)
        data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
        print(data_dict)
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server = "127.0.0.1", 5000
        data = str(data_dict)
        sock.sendto(data.encode(), server)
        print(f'Send data: {data} to server: {server}')
        sock.close()

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/message':
            self.send_html_file('message.html')
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file('error.html', 404)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())


def run(server_class=HTTPServer, handler_class=HttpHandler):
    print("http server start")
    server_address = ('',3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        print("http close")
        http.server_close()


def run_server():
    print("udp server start")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = "127.0.0.1", 5000
    sock.bind(server)
    while True:
        try:
            data, address = sock.recvfrom(1024)
            data_decoded=data.decode()
            data_dict=ast.literal_eval(data_decoded)
            date=datetime.now()
            date=str(date)
            json_dict={}
            json_dict[date]=data_dict
            with open("storage/data.json","a",encoding="utf-8") as file:
                json.dump(json_dict,file,ensure_ascii=False,indent=4)
            print(f'Received data: {json_dict} from: {address}')
            json_dict={}
        except KeyboardInterrupt:
            break
    print(f'Destroy server')
    sock.shutdown()
    sock.close()


if __name__ == '__main__':
    http_server=threading.Thread(target=run)
    udp_server=threading.Thread(target=run_server)
    http_server.start()
    udp_server.start()
    http_server.join()
    udp_server.join()
    print("all closed")
