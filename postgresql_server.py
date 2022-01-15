"""The module for HTTP server which works with parser client and PostgreSQL."""

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import time
import psycopg2
from psycopg2 import Error

USER = "postgres"
PASSWORD = "5432112345"
HOST = "127.0.0.1"
PORT = "5432"
BASE_DB = "postgres"
LOCAL_SERVER_PORT = 8087


class MyServerRequestHandler(BaseHTTPRequestHandler):
    """Handle client's http requests.

    Methods:

    separate_path(self, path: str): Separate current resource path.
    def get_current_launch_time(self): Calculate a launch time of the current input query session.
    def find_query_parameter(self, param_name: str, params_dict: dict): Find necessary query parameter in the params
                                                                        dict.
    def get_query_params(self, path: str): Divide full path for params and simple path.
    def parse_data(self, data): Parse incoming data according to the collection in the database.
    def save_the_post(self, data): Store data to the database.
    def send_posts(self, necessary_posts): Send posts to the client.
    def join_collections(self, necessary_post): Join data from the different collections of the post to a one dict.
    do_GET(self): Handle GET requests.
    do_POST(self): Handle POST requests.
    do_DELETE(self): Handle DELETE requests.
    do_PUT(self): Handle PUT requests.
    show_no_file_source_error(self): Send error respond - no file source.
    show_no_necessary_post(self): Send error respond - no necessary post to work with.
    show_unknown_request_error(self): Send error respond - unknown request occurs.
    show_post_is_already_exists(self): Send error respond - the necessary post is already exists.
    def show_no_post_id_error(self): Send error respond when there is unknown request occurs.
    def show_no_necessary_attr(self): Send error respond when there is no necessary attribute in the data dict.
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
        """Find necessary query parameter in the params dict.

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

    def save_the_post(self, data: dict) -> bool:
        """Store data to the database.

        :param data: data to store
        :return: boolean flag which show if the storing process was successful or not
        """

        is_post_saved = False

        try:

            save_data_user_karma_query = \
                "INSERT INTO user_karma (post_karma, comment_karma, general_user_karma) VALUES " \
                "(%s, %s, %s) RETURNING ID;"

            records_to_insert = (data.get('post_karma'), data.get('comment_karma'), data.get('general_user_karma'))

            with conn.cursor() as save_data_user_karma_cursor:
                save_data_user_karma_cursor.execute(save_data_user_karma_query, records_to_insert)
                id_user_karma = save_data_user_karma_cursor.fetchone()[0]

            save_data_user_query = " INSERT INTO user_data (user_name, user_cake_day, user_karma) VALUES (%s, %s, %s)" \
                                   "RETURNING ID;"

            records_to_insert = (data.get('user_name'), data.get('user_cake_day'), str(id_user_karma))

            with conn.cursor() as save_data_user_cursor:
                save_data_user_cursor.execute(save_data_user_query, records_to_insert)
                id_user = save_data_user_cursor.fetchone()[0]

            save_data_post_query = """
                                    INSERT INTO post (post_date, number_of_comments, number_of_votes, post_category) 
                                    VALUES (%s, %s, %s, %s) RETURNING ID;
                                    """
            records_to_insert = (data.get('post_date'), data.get('number_of_comments'),
                                 data.get('number_of_votes'), data.get('post_category'))

            with conn.cursor() as save_data_post_cursor:
                save_data_post_cursor.execute(save_data_post_query, records_to_insert)
                id_post = save_data_post_cursor.fetchone()[0]

            save_data_user_post_info_query = "INSERT INTO user_post_info VALUES (%s, %s, %s, %s);"

            records_to_insert = (data.get('unique_id', data.get('id')), str(id_user),
                                 str(id_post), self.get_current_launch_time())

            with conn.cursor() as save_data_user_post_info_cursor:
                save_data_user_post_info_cursor.execute(save_data_user_post_info_query, records_to_insert)

            is_post_saved = True

        except KeyError as e:
            self.show_no_necessary_attr()
        finally:
            return is_post_saved

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

    def join_collections(self, necessary_post: dict) -> dict:
        """Join data from the different collections of the post to a one dict

        :param necessary_post: post to join
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

            get_posts_count_query = "SELECT COUNT(*) as count FROM user_post_info"

            with conn.cursor() as get_posts_count_cursor:
                get_posts_count_cursor.execute(get_posts_count_query)
                count = get_posts_count_cursor.fetchone()
                count = count[0]

            if count == 0:
                new_post_num = 1

            else:

                get_necessary_post_query = "SELECT * FROM user_post_info WHERE ID = " + post_id

                with conn.cursor() as get_necessary_post_cursor:
                    get_necessary_post_cursor.execute(get_necessary_post_query)
                    necessary_post = get_necessary_post_cursor.fetchone()

                if necessary_post is None:

                    # get db elements count
                    new_post_num = count + 1

                else:
                    self.show_post_is_already_exists()
                    return

            # add data in db

            is_data_stored = self.save_the_post(data)

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
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        data = json.loads(body)
        path = self.path
        if not path.startswith('/posts'):
            self.show_unknown_request_error()
        else:
            path, params_dict = self.get_query_params(path)

            post_id = self.find_query_parameter("post_id", params_dict)

            if post_id is not None:

                necessary_post = user_post_info_coll.find_one({'_id': post_id})

                if necessary_post is not None:

                    collection_data = self.parse_data(data)

                    user_dict = user_coll.find_one({'_id': necessary_post['user_id']})

                    user_karma_coll.update_one({'_id': user_dict['user_karma']},
                                               {'$set': collection_data['user_karma']},
                                               upsert=False)
                    user_coll.update_one({'_id': necessary_post['user_id']}, {'$set': collection_data['user']},
                                         upsert=False)
                    post_coll.update_one({'_id': necessary_post['post_id']}, {'$set': collection_data['post']},
                                         upsert=False)
                    send_message = False
                    id = collection_data['user_post_info'].pop("_id", None)
                    if id is not None:
                        send_message = True

                    user_post_info_coll.update_one({'_id': post_id}, {'$set': collection_data['user_post_info']},
                                                   upsert=False)

                    self.send_response(200)
                    self.end_headers()
                    if send_message:
                        self.wfile.write(b'Success !\n\nNotes:\n\n- Impossible to change post id value so it was just '
                                         b'skipped.\n'
                                         b'- Other attributes were updated successfully.')

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


def create_db(db_name):
    """Create database.

    :param db_name: name for a new database
    :return: boolean flag
    """
    try:

        start_conn = psycopg2.connect(user=USER,
                                      password=PASSWORD,
                                      host=HOST,
                                      port=PORT,
                                      database=BASE_DB)

        start_conn.autocommit = True

        create_db_query = f"CREATE DATABASE {db_name}"

        with start_conn.cursor() as cursor:
            cursor.execute(create_db_query)

    except (Exception, Error) as error:
        print("Database is already exists. There is no need to create it again.")
    finally:
        if start_conn:
            start_conn.close()
            print("Close start connection with PostgreSQL.")


if __name__ == "__main__":
    db_name = "reddit_parser"
    create_db(db_name)

    try:

        conn = psycopg2.connect(user=USER,
                                password=PASSWORD,
                                host=HOST,
                                port=PORT,
                                database=db_name)

        conn.autocommit = True

        create_user_karma_query = '''CREATE TABLE IF NOT EXISTS user_karma
                          (ID serial PRIMARY KEY     NOT NULL,
                          post_karma           varchar(50)    NOT NULL,
                          comment_karma         varchar(50)    NOT NULL,
                          general_user_karma           varchar(50)    NOT NULL
                          ); '''

        with conn.cursor() as create_user_karma_cursor:
            create_user_karma_cursor.execute(create_user_karma_query)

        create_post_query = '''CREATE TABLE IF NOT EXISTS post
                              (ID serial PRIMARY KEY     NOT NULL,
                              post_date           varchar(50)    NOT NULL,
                              number_of_comments         varchar(50)    NOT NULL,
                              number_of_votes           varchar(50)    NOT NULL,
                              post_category           varchar(50)    NOT NULL
                              ); '''

        with conn.cursor() as create_post_cursor:
            create_post_cursor.execute(create_post_query)

        create_user_query = '''CREATE TABLE IF NOT EXISTS user_data
                                      (ID serial PRIMARY KEY     NOT NULL,
                                      user_name           varchar(50)    NOT NULL,
                                      user_cake_day         varchar(50)    NOT NULL,
                                      user_karma           INTEGER    NOT NULL,
                                      FOREIGN KEY (user_karma) REFERENCES user_karma (ID) ON DELETE CASCADE ON UPDATE CASCADE 
                                      ); '''

        with conn.cursor() as create_user_cursor:
            create_user_cursor.execute(create_user_query)

        create_user_post_info_query = '''CREATE TABLE IF NOT EXISTS user_post_info
                                              (ID varchar(50) PRIMARY KEY     NOT NULL,
                                              user_id           INTEGER    NOT NULL,
                                              post_id         INTEGER    NOT NULL,
                                              time_of_processing           varchar(50)    NOT NULL,
                                              FOREIGN KEY (user_id) REFERENCES user_data (ID) ON DELETE CASCADE ON UPDATE CASCADE,
                                              FOREIGN KEY (post_id) REFERENCES post (ID) ON DELETE CASCADE ON UPDATE CASCADE
                                              ); '''

        with conn.cursor() as create_user_post_info_cursor:
            create_user_post_info_cursor.execute(create_user_post_info_query)

        web_server = HTTPServer((HOST, LOCAL_SERVER_PORT), MyServerRequestHandler)
        print("Server started http://%s:%s" % (HOST, LOCAL_SERVER_PORT))

        try:
            web_server.serve_forever()
        except KeyboardInterrupt:
            web_server.server_close()
            print("Server stopped.")

    except (Exception, Error) as error:
        print("Exception during working with PostgreSQL", error)
    finally:
        if conn:
            conn.close()
            print("Close main connection with PostgreSQL.")
