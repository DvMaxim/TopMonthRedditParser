"""The module for HTTP server which works with parser client and MongoDB."""

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import time
from pymongo import MongoClient

HOST_NAME = "127.0.0.1"
SERVER_PORT = 8087
MONGODB_SERVER_PORT = 27017


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

    def get_current_launch_time(self) -> str:
        """Calculate a launch time of the current input query session.

        Calculate a launch time of the program based on the current date using
        the next time template: year/month/day/hours/minutes.

        :return: a launch time of the program
        :rtype: str
        """
        time_tuple = time.localtime(time.time())

        return time.strftime('%d.%m.%Y, %H:%M:%S', time_tuple)

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

    def find_query_parameter(self, param_name: str, params_dict: dict):
        """Find necessary query parameter in the params dict

        :param param_name: necessary param name
        :param params_dict: dictionary with parameters
        :return: param value if it's in the params dict and None value if it's not
        """
        if params_dict is not None:
            if param_name in params_dict:
                param_value = params_dict[param_name]
                if param_value.endswith('/'):
                    param_value = param_value.replace('/', '')
                return param_value
        return None

    def get_query_params(self, path: str):
        """Divide full path for params and simple path.

        :param path: a full resource path
        :return: a tuple of the simple path and params dict
        """
        params_dict = None
        if self.separate_path(path):
            path, params_dict = self.separate_path(path)
        return path, params_dict

    def store_db_data(self, data):
        """Store data to the database.

        :param data: data to store
        :return: boolean flag which show if the storing process was successful or not
        """
        is_data_stored = False

        try:
            # create user_karma collection

            user_karma = {}
            user_karma["post_karma"] = data.get("post_karma")
            user_karma["comment_karma"] = data.get("comment_karma")
            user_karma["general_user_karma"] = data.get("user_karma")
            result_user_karma = user_karma_coll.insert_one(user_karma)

            # create user collection
            user = {}
            user["user_name"] = data.get("username")
            user["user_cake_day"] = data.get("user_cake_day")
            user["user_karma"] = result_user_karma.inserted_id
            result_user = user_coll.insert_one(user)

            # create post collection
            post = {}
            post["post_date"] = data.get("post_date")
            post["number_of_comments"] = data.get("number_of_comments")
            post["number_of_votes"] = data.get("number_of_votes")
            post["post_category"] = data.get("post_category")
            result_post = post_coll.insert_one(post)

            # create user_post_info collection
            user_post_info = {}
            user_post_info["_id"] = data.get('unique_id', data.get('_id', None))
            user_post_info["user_id"] = result_user.inserted_id
            user_post_info["post_id"] = result_post.inserted_id
            user_post_info["time_of_processing"] = self.get_current_launch_time()
            result_user_post_info = user_post_info_coll.insert_one(user_post_info)

            is_data_stored = True

        except KeyError as e:
            self.show_no_necessary_attr()

        return is_data_stored

    def send_posts(self, necessary_posts):
        """Send posts to the client.

        :param necessary_posts: posts to send
        :return: None
        """
        response_dict = {}

        if isinstance(necessary_posts, dict):
            response_dict = self.join_collections(necessary_posts)
        else:

            posts_count = 1

            necessary_posts_generator = (post for post in necessary_posts)

            while True:
                try:
                    curr_post = next(necessary_posts_generator)
                    joined_dict = self.join_collections(curr_post)
                    response_dict[str(posts_count)] = joined_dict
                    posts_count += 1
                except StopIteration as e:
                    break
                except Exception as e:
                    print("Exception in send_posts_func: ", str(e))
                    break

        self.send_response(200)
        self.end_headers()
        json_posts_dict = json.dumps(response_dict)
        self.wfile.write(bytes(json_posts_dict, "utf-8"))

    def join_collections(self, necessary_post):
        """Join data from the different collections of the post to a one dict

        :param necessary_post:
        :return: dict with post data
        """
        response_dict = necessary_post.copy()

        user_id = response_dict.pop('user_id')
        post_id = response_dict.pop('post_id')

        user_dict = user_coll.find_one({'_id': user_id})
        del user_dict['_id']

        user_karma_id = user_dict.pop('user_karma')

        user_karma_dict = user_karma_coll.find_one({'_id': user_karma_id})
        del user_karma_dict['_id']

        post_dict = post_coll.find_one({'_id': post_id})
        del post_dict['_id']

        response_dict.update(user_dict)
        response_dict.update(user_karma_dict)
        response_dict.update(post_dict)

        return response_dict

    def do_GET(self):
        """Handle GET requests.

        Receives all posts' content from the database. Moreover if there is
        a special post its data will be received by the client.
        """
        path = self.path
        if not path.startswith('/posts'):
            self.show_unknown_request_error()
        else:
            path, params_dict = self.get_query_params(path)

            post_id = self.find_query_parameter("post_id", params_dict)

            if params_dict is not None and post_id is not None:

                necessary_post = user_post_info_coll.find_one({'_id': post_id})

                if necessary_post is not None:
                    self.send_posts(necessary_post)
                else:
                    self.show_no_necessary_post()
                    return

            else:
                necessary_posts = user_post_info_coll.find()
                self.send_posts(necessary_posts)

    def do_POST(self):
        """Handle POST requests.

        Adds a new post to the database. Check for existing one's before adding.
        """
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        data = json.loads(body)

        if not self.path.startswith('/posts'):
            self.show_unknown_request_error()
        else:

            post_id = data.get('unique_id', data.get('_id', None))

            if post_id is None:
                self.show_no_necessary_attr()
                return

            if "user_post_info" not in db.list_collection_names():
                new_post_num = 0
            else:

                necessary_post = user_post_info_coll.find({'_id': post_id})
                necessary_post_list = list(necessary_post)
                if len(necessary_post_list) == 0:

                    # get db elements count

                    new_post_num = user_post_info_coll.count_documents({}) + 1

                else:
                    self.show_post_is_already_exists()
                    return

            # add data in db

            is_data_stored = self.store_db_data(data)

            if not is_data_stored:
                return

            self.send_response(201)
            self.end_headers()
            json_posts_dict = json.dumps({post_id: new_post_num})
            self.wfile.write(bytes(json_posts_dict, "utf-8"))

    def do_DELETE(self):
        """Handle DELETE requests.

        Delete post with special id from the database.
        """
        path = self.path
        if not path.startswith('/posts'):
            self.show_unknown_request_error()
        else:
            path, params_dict = self.get_query_params(path)

            post_id = self.find_query_parameter("post_id", params_dict)

            if params_dict is not None and post_id is not None:

                necessary_post = user_post_info_coll.find_one({'_id': post_id})

                if necessary_post is not None:
                    user_dict = user_coll.find_one({'_id': necessary_post['user_id']})
                    user_karma_coll.delete_one({'_id': user_dict['user_karma']})
                    user_coll.delete_one({'_id': necessary_post['user_id']})
                    post_coll.delete_one({'_id': necessary_post['post_id']})
                    user_post_info_coll.delete_one({'_id': post_id})
                    self.send_response(200)
                    self.end_headers()
                else:
                    self.show_no_necessary_post()
                    return

            else:
                self.show_no_post_id_error()
                return

    def do_PUT(self):
        """Handle PUT requests.

        Change a post with the special id for a new one.
        """
        path = self.path
        if not path.startswith('/posts'):
            self.show_unknown_request_error()
        else:
            path, params_dict = self.get_query_params(path)

            post_id = self.find_query_parameter("post_id", params_dict)

            if params_dict is not None and post_id is not None:

                necessary_post = user_post_info_coll.find_one({'_id': post_id})

                if necessary_post is not None:
                    pass
                else:
                    self.show_no_necessary_post()
                    return

            else:
                self.show_no_post_id_error()
                return

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
        self.wfile.write(b"Server cannot handle unknown request. Please use only appropriate ones.")

    def show_post_is_already_exists(self):
        """Send error respond when the necessary post is already exists."""
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b'Impossible to store the post which already exists on the source. '
                         b'Please, try to send request with another post.')

    def show_no_post_id_error(self):
        """Send error respond when there is unknown request occurs."""
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b"Sorry but server cannot work with empty post id value. "
                         b"Please use only appropriate ones.")

    def show_no_necessary_attr(self):
        """Send error respond when there is no necessary attribute in the data dict."""
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b"Sorry but there is no such data in the current data set. "
                         b"Please use only appropriate data set structures.")


if __name__ == "__main__":
    client = MongoClient(host=HOST_NAME, port=MONGODB_SERVER_PORT)
    db = client['reddit_parser']
    user_karma_coll = db["user_karma"]
    user_coll = db["user"]
    post_coll = db["post"]
    user_post_info_coll = db["user_post_info"]
    web_server = HTTPServer((HOST_NAME, SERVER_PORT), MyServerRequestHandler)
    print("Server started http://%s:%s" % (HOST_NAME, SERVER_PORT))

    try:
        web_server.serve_forever()
    except KeyboardInterrupt:
        web_server.server_close()
        print("Server stopped.")

# from random import randint
#
# # Step 1: Connect to MongoDB - Note: Change connection string as needed
# client = MongoClient(port=27017)
# db = client.business
# # Step 2: Create sample data
# names = ['Kitchen', 'Animal', 'State', 'Tastey', 'Big', 'City', 'Fish', 'Pizza', 'Goat', 'Salty', 'Sandwich', 'Lazy',
#          'Fun']
# company_type = ['LLC', 'Inc', 'Company', 'Corporation']
# company_cuisine = ['Pizza', 'Bar Food', 'Fast Food', 'Italian', 'Mexican', 'American', 'Sushi Bar', 'Vegetarian']
# for x in range(1, 501):
#     business = {
#         'name': names[randint(0, (len(names) - 1))] + ' ' + names[randint(0, (len(names) - 1))] + ' ' + company_type[
#             randint(0, (len(company_type) - 1))],
#         'rating': randint(1, 5),
#         'cuisine': company_cuisine[randint(0, (len(company_cuisine) - 1))]
#     }
#     # Step 3: Insert business object directly into MongoDB via insert_one
#     result = db.reviews.insert_one(business)
#     # Step 4: Print to the console the ObjectID of the new document
#     print('Created {0} of 500 as {1}'.format(x, result.inserted_id))
# # Step 5: Tell us that you are done
# print('finished creating 500 business reviews')
