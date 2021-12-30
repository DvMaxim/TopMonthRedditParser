"""The module for HTTP server which works with parser client."""

from http.server import BaseHTTPRequestHandler, HTTPServer
import json

HOST_NAME = "127.0.0.1"
SERVER_PORT = 8087

curr_launch_time = ''


class MyServerRequestHandler(BaseHTTPRequestHandler):
    """Handle client's http requests.

    Methods:

    get_posts_num(self, file_name: str): Get posts count.
    parse_result_file(self, file_name: str): Get dictionary of all the posts.
    get_necessary_post(self, posts_dict: dict, post_id: str): Receive necessary post.
    separate_path(self, path: str): Separate current resource path.
    is_source_file_valuable(self, file_name: str): Check the source file for a possibility to work.
    parse_query_file_name(self, params_dict: dict): Parse the file name.
    write_posts_in_file(self, file_name: str, posts_dict: dict): Write all of the posts in the file.
    work_with_file(self, file_name: str, path: str): Process a necessary file.
    get_query_file_name(self, path: str): Get file name from query parameters.
    do_GET(self): Handle GET requests.
    do_POST(self): Handle POST requests.
    do_DELETE(self): Handle DELETE requests.
    do_PUT(self): Handle PUT requests.
    show_no_file_source_error(self): Send error respond - no file source.
    show_no_necessary_post(self): Send error respond - no necessary post to work with.
    show_unknown_request_error(self): Send error respond - unknown request occurs.
    show_post_is_already_exists(self): Send error respond - the necessary post is already exists.
    """

    def get_posts_num(self, file_name: str):
        """Get posts count from the necessary file.

        :param file_name: name of the necessary file
        :return: posts count
        """
        with open(file_name, "r") as file:
            posts_list = file.readlines()
        return len(posts_list)

    def parse_result_file(self, file_name: str):
        """Get dictionary of all the posts from the necessary file.

        :param file_name: name of the necessary file
        :return: dictionary with the posts
        """
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

    def get_necessary_post(self, posts_dict: dict, post_id: str):
        """Receive necessary post from the hole posts dictionary

        :param posts_dict: dictionary with all of the posts from the necessary file.
        :param post_id: id of the necessary post
        :return: a necessary post
        """
        necessary_post = {}
        for post in posts_dict.values():
            if post['unique_id'] == post_id:
                necessary_post = post.copy()
        if len(necessary_post) == 0:
            return None
        else:
            return necessary_post

    def separate_path(self, path: str):
        """Separate current resource path to a simple one and query parameters.

        :param path: current resource path
        :return: a tuple of the simple resource path and parameters dictionary
                or a None value
        """
        if '?' in path:
            path, params_str = path.split('?')[0], path.split('?')[1]
            params_list = params_str.split("&")
            params_dict = {el.split("=")[0]: el.split("=")[1] for el in params_list}
            return path, params_dict
        else:
            return None

    def is_source_file_valuable(self, file_name: str):
        """Check the source file for a possibility to work

        :param file_name: name of the necessary file
        :return: bool signal
        """
        try:
            file = open(file_name)
            file.close()
            return True
        except IOError as e:
            self.show_no_file_source_error()
            return False

    def parse_query_file_name(self, params_dict: dict):
        """Parse the file name from the query parameters dictionary.

        :param params_dict: the query parameters dictionary
        :return: file name or None
        """
        if 'file_name' in params_dict:
            if self.is_source_file_valuable(params_dict['file_name']):
                return params_dict['file_name']
            else:
                return None
        else:
            return curr_launch_time

    def write_posts_in_file(self, file_name: str, posts_dict: dict):
        """Write all of the posts in the necessary file.

        :param file_name: a necessary file name
        :param posts_dict: a dictionary with all the posts
        :return: None
        """
        file = open(file_name, "w")
        for post in posts_dict.values():
            parse_str = ' | '.join(post.values())
            file.write(parse_str)
        file.close()

    def work_with_file(self, file_name: str, path: str):
        """Process a necessary file.

        :param file_name: a necessary file name
        :param path: a simple resource path
        :return: a tuple of the posts dictionary, post id and necessary post
        """
        posts_dict = self.parse_result_file(file_name)
        post_id = path.replace('/posts/', '')
        if post_id.endswith('/'):
            post_id = post_id.replace('/', '')
        necessary_post = self.get_necessary_post(posts_dict, post_id)
        return posts_dict, post_id, necessary_post

    def get_query_file_name(self, path: str):
        """Get file name from query parameters.

        :param path: a full resource path
        :return: a tuple of the current file name and simple resource path
        """
        if self.separate_path(path):
            path, params_dict = self.separate_path(path)
            curr_file_name = self.parse_query_file_name(params_dict)
        else:
            curr_file_name = curr_launch_time
        return curr_file_name, path

    def do_GET(self):
        """Handle GET requests.

        Receive all posts' content from the necessary source file if there is no
        unique identifier determined. Otherwise receive content from the post
        with such special id. Moreover checks a full resource path for a file_name
        query parameter. If it presents it will become a current resource file.
        """
        path = self.path
        if not path.startswith('/posts'):
            self.show_unknown_request_error()
        else:
            curr_file_name, path = self.get_query_file_name(path)
            print(curr_file_name)
            if curr_file_name is None:
                return
            posts_dict, post_id, necessary_post = self.work_with_file(curr_file_name, path)
            if path == '/posts' or path == '/posts/':
                self.send_response(200)
                self.end_headers()
                json_posts_dict = json.dumps(posts_dict)
                self.wfile.write(bytes(json_posts_dict, "utf-8"))
            else:
                if necessary_post is not None:
                    self.send_response(200)
                    self.end_headers()
                    json_posts_dict = json.dumps(necessary_post)
                    self.wfile.write(bytes(json_posts_dict, "utf-8"))
                else:
                    self.show_no_necessary_post()

    def do_POST(self):
        """Handle POST requests.

        Adds a new post to the source file. If there is no file - creates a new one.
        Checks the contents of the file for duplicates by the UNIQUE_ID field before
        adding the new post. Returns the operation code 201 and a JSON in special format.
        Moreover checks a full resource path for a file_name query parameter. If it presents
        it will become a current resource file.
        """
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        data = json.loads(body)
        global curr_launch_time
        path = self.path
        if path == '/filename':
            res_file_name = data['file_name']
            file = open(res_file_name, 'w')
            file.close()
            last_res_file = res_file_name
            self.send_response(200)
            self.end_headers()
        elif not path.startswith('/posts'):
            self.show_unknown_request_error()
        else:
            curr_file_name, path = self.get_query_file_name(path)
            if curr_file_name is None:
                return
            post_id = data['unique_id']
            posts_dict = self.parse_result_file(curr_file_name)
            if posts_dict is not None:
                necessary_post = self.get_necessary_post(posts_dict, post_id)
                if necessary_post is None:
                    posts_count = self.get_posts_num(curr_file_name)
                    new_post_num = posts_count + 1
                else:
                    self.show_post_is_already_exists()
                    return
            else:
                new_post_num = 1
            parse_str = ' | '.join(data.values())
            with open(curr_file_name, "a") as file:
                file.write(parse_str)
                file.write('\n')
            self.send_response(201)
            self.end_headers()
            json_posts_dict = json.dumps({post_id: new_post_num})
            self.wfile.write(bytes(json_posts_dict, "utf-8"))

    def do_DELETE(self):
        """Handle DELETE requests.

        Deletes the post with the special unique identifier from the file.
        Moreover checks a full resource path for a file_name query parameter. If it presents
        it will become a current resource file.
        """
        path = self.path
        if not path.startswith('/posts'):
            self.show_unknown_request_error()
        else:
            curr_file_name, path = self.get_query_file_name(path)
            if curr_file_name is None:
                return
            posts_dict, post_id, necessary_post = self.work_with_file(curr_file_name, path)
            if necessary_post is not None:
                for key, value in dict(posts_dict).items():
                    if value['unique_id'] == post_id:
                        del posts_dict[key]
                    self.write_posts_in_file(curr_file_name, posts_dict)
                self.send_response(200)
                self.end_headers()
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'Sorry, but there is no necessary post. Please, choose another one.')

    def do_PUT(self):
        """Handle PUT requests.

        Change post from the file source on a necessary one with the special unique identifier.
        Moreover checks a full resource path for a file_name query parameter. If it presents
        it will become a current resource file.
        """
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        data = json.loads(body)
        path = self.path
        if not path.startswith('/posts'):
            self.show_unknown_request_error()
        else:
            curr_file_name, path = self.get_query_file_name(path)
            if curr_file_name is None:
                return
            posts_dict, post_id, necessary_post = self.work_with_file(curr_file_name, path)
            if necessary_post is not None:
                for key, value in dict(posts_dict).items():
                    if value['unique_id'] == post_id:
                        posts_dict[key] = data
                    self.write_posts_in_file(curr_file_name, posts_dict)

                self.send_response(200)
                self.end_headers()
            else:
                self.show_no_necessary_post()

    def show_no_file_source_error(self):
        """Send error respond when there is no source file for storing data."""
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b'There is no file source to store you data. '
                         b'Please, send necessary request to create a such source.')

    def show_no_necessary_post(self):
        """Send error respond when there is no necessary post to work with."""
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b'Sorry, but there is no necessary post. Please, choose another one.')

    def show_unknown_request_error(self):
        """Send error respond when there is unknown request occurs."""
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b"Server cannot handle unknown request. Please use only appropriate.")

    def show_post_is_already_exists(self):
        """Send error respond when the necessary post is already exists."""
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b'Impossible to store the post which already exists on the source. '
                         b'Please, try to send request with another post.')


if __name__ == "__main__":
    web_server = HTTPServer((HOST_NAME, SERVER_PORT), MyServerRequestHandler)
    print("Server started http://%s:%s" % (HOST_NAME, SERVER_PORT))

    try:
        web_server.serve_forever()
    except KeyboardInterrupt:
        web_server.server_close()
        print("Server stopped.")
