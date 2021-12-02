from http.server import BaseHTTPRequestHandler, HTTPServer
import json

host_name = "127.0.0.1"
server_port = 8087




class MyServerRequestHandler(BaseHTTPRequestHandler):

    # def __init__(self, request, client_address, server):
    #     super().__init__(request, client_address, server)
    #

    def parse_result_file(self, file_name):
        with open(file_name, "r") as file:
            posts_list = file.readlines()
        posts_dict = {(str(i), el.split(" | ")) for i, el in enumerate(posts_list, 1)}
        res_dict = {}
        for (key, value) in posts_dict.items():
            value_gen = (el for el in value)
            value_dict = {
                'unique_id': next(value_gen),
                'post_link': next(value_gen),
                'username': next(value_gen),
                'user_karma': next(value_gen),
                'user_cake_day': next(value_gen),
                'post_karma': next(value_gen),
                'comment_karma': next(value_gen),
                'post_date': next(value_gen),
                'number_of_comments': next(value_gen),
                'number_of_votes': next(value_gen),
                'post_category': next(value_gen)
            }
            res_dict[key] = value_dict

        return res_dict

    def do_GET(self):
        if self.path != '/posts' and not self.path.startswith('/posts/'):
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Server cannot handle unknown request. Please use only appropriate.")
        else:
            if self.is_result_file_valuable:
                posts_dict = self.parse_result_file(self.res_file_name)
                if self.path == '/posts':
                    self.send_response(200)
                    self.end_headers()
                    json_posts_dict = json.dumps(posts_dict)
                    self.wfile.write(bytes(json_posts_dict, "utf-8"))

                elif self.path.startswith('/posts/'):
                    pass
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'There is no file source to store you data. '
                                 b'Please, send necessary request to create a such source.')

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        data = json.loads(body)
        if self.path == '/filename':
            res_file_name = data['file_name']
            file = open(res_file_name, 'w')
            file.close()
            self.send_response(200)
            self.end_headers()
        elif self.path == '/posts':
            res_file_name = data.pop('file_name')
            try:
                file = open(res_file_name)
                file.close()
                parse_str = ' | '.join(data.values())
                print('file please', res_file_name)
                with open(res_file_name, "a") as file:
                    file.write(parse_str)
                    file.write('\n')
                self.send_response(200)
                self.end_headers()
            except IOError as e:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'There is no file source to store you data. '
                                 b'Please, send necessary request to create a such source.')
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Server cannot handle unknown request. Please use only appropriate.")



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
