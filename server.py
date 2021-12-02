from http.server import BaseHTTPRequestHandler, HTTPServer
import json

host_name = "127.0.0.1"
server_port = 8087


class MyServerRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Hello, world!')

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        data = json.loads(body)

        if self.path == '/filename':
            file = open(data['file_name'], 'w')
            file.close()
        elif self.path == '/posts':
            file_name = data.pop('file_name')
            parse_str = ' | '.join(data.values())
            with open(file_name, "a") as file:
                file.write(parse_str)
                file.write('\n')

        self.send_response(200)
        self.end_headers()



        # my_dict = {'first': 'hi', 'second': 'world'}
        #
        # myjson = json.dumps(my_dict)
        #
        # self.wfile.write(bytes(myjson, "utf-8"))

    def do_DELETE(self):
        pass

    def do_PUT(self):
        pass


if __name__ == "__main__":
    web_server = HTTPServer((host_name, server_port), MyServerRequestHandler)
    print("Server started http://%s:%s" % (host_name, server_port))

    try:
        web_server.serve_forever()
    except KeyboardInterrupt:
        web_server.server_close()
        print("Server stopped.")
