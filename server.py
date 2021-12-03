from http.server import BaseHTTPRequestHandler, HTTPServer
import json

HOST_NAME = "127.0.0.1"
SERVER_PORT = 8087

last_res_file = ''


class MyServerRequestHandler(BaseHTTPRequestHandler):

    # def __init__(self, request, client_address, server):
    #     super().__init__(request, client_address, server)
    #

    def get_posts_num(self, file_name):
        with open(file_name, "r") as file:
            posts_list = file.readlines()
        return len(posts_list)

    def parse_result_file(self, file_name):
        with open(file_name, "r") as file:
            posts_list = file.readlines()
        if len(posts_list) == 0:
            return None
        else:
            posts_dict = {str(i): el.split(" | ") for i, el in enumerate(posts_list, 1)}
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

    def get_necessary_post(self, posts_dict, post_id):
        necessary_post = {}
        for post in posts_dict.values():
            if post['unique_id'] == post_id:
                necessary_post = post.copy()
        if len(necessary_post) == 0:
            return None
        else:
            return necessary_post

    def do_GET(self):
        if not self.path.startswith('/posts'):
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Server cannot handle unknown request. Please use only appropriate.")
        else:
            try:
                file = open(last_res_file)
                file.close()
                posts_dict = self.parse_result_file(last_res_file)
                if self.path == '/posts' or self.path == '/posts/':
                    self.send_response(200)
                    self.end_headers()
                    json_posts_dict = json.dumps(posts_dict)
                    self.wfile.write(bytes(json_posts_dict, "utf-8"))
                else:
                    post_id = self.path.replace('/posts/', '')
                    if post_id.endswith('/'):
                        post_id = post_id.replace('/', '')
                    necessary_post = self.get_necessary_post(posts_dict, post_id)
                    if necessary_post is not None:
                        self.send_response(200)
                        self.end_headers()
                        json_posts_dict = json.dumps(necessary_post)
                        self.wfile.write(bytes(json_posts_dict, "utf-8"))
                    else:
                        self.send_response(404)
                        self.end_headers()
                        self.wfile.write(b'Sorry, but there is no necessary post. Please, choose another one.')

            except IOError as e:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'There is no file source to store you data. '
                                 b'Please, send necessary request to create a such source.')

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        data = json.loads(body)
        global last_res_file
        if self.path == '/filename':
            res_file_name = data['file_name']
            file = open(res_file_name, 'w')
            file.close()
            last_res_file = res_file_name
            self.send_response(200)
            self.end_headers()

        elif self.path == '/posts' or self.path == '/posts/':
            res_file_name = data.pop('file_name')
            try:
                file = open(res_file_name)
                file.close()
                post_id = data['Unique_id']
                posts_dict = self.parse_result_file(res_file_name)
                if posts_dict is not None:
                    necessary_post = self.get_necessary_post(posts_dict, post_id)
                    if necessary_post is None:
                        posts_count = self.get_posts_num(res_file_name)
                        new_post_num = posts_count + 1
                    else:
                        self.send_response(404)
                        self.end_headers()
                        self.wfile.write(b'Impossible to store the post which already exists on the source. '
                                         b'Please, try to send request with another post.')
                        return
                else:
                    new_post_num = 1

                parse_str = ' | '.join(data.values())
                with open(last_res_file, "a") as file:
                    file.write(parse_str)
                    file.write('\n')
                self.send_response(201)
                self.end_headers()
                json_posts_dict = json.dumps({post_id: new_post_num})
                self.wfile.write(bytes(json_posts_dict, "utf-8"))



            except IOError as e:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'There is no file source to store you data. '
                                 b'Please, send necessary request to create a such source.')
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Server cannot handle unknown request. Please use only appropriate.")

    def write_posts_in_file(self, file_name, posts_dict):
        file = open(file_name, "w")
        for post in posts_dict.values():
            parse_str = ' | '.join(post.values())
            file.write(parse_str)
            #file.write('\n')
        file.close()

    def do_DELETE(self):
        if not self.path.startswith('/posts/'):
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Server cannot handle unknown request. Please use only appropriate.")
        else:
            try:
                file = open(last_res_file)
                file.close()
                posts_dict = self.parse_result_file(last_res_file)
                post_id = self.path.replace('/posts/', '')
                if post_id.endswith('/'):
                    post_id = post_id.replace('/', '')
                necessary_post = self.get_necessary_post(posts_dict, post_id)
                if necessary_post is not None:

                    for key, value in dict(posts_dict).items():
                        if value['unique_id'] == post_id:
                            del posts_dict[key]
                        self.write_posts_in_file(last_res_file, posts_dict)

                    self.send_response(200)
                    self.end_headers()
                else:
                    self.send_response(404)
                    self.end_headers()
                    self.wfile.write(b'Sorry, but there is no necessary post. Please, choose another one.')

            except IOError as e:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'There is no file source to store you data. '
                                 b'Please, send necessary request to create a such source.')

    def do_PUT(self):
        pass


if __name__ == "__main__":
    web_server = HTTPServer((HOST_NAME, SERVER_PORT), MyServerRequestHandler)
    print("Server started http://%s:%s" % (HOST_NAME, SERVER_PORT))

    try:
        web_server.serve_forever()
    except KeyboardInterrupt:
        web_server.server_close()
        print("Server stopped.")
