"""The module for HTTP server which works with parser client and PostgreSQL."""

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import time
import psycopg2
from psycopg2 import Error

USER = "postgres"
PASSWORD = "5432112345"
HOST = "127.0.0.1"
DB_PORT = "5432"
BASE_DB = "postgres"
LOCAL_SERVER_PORT = 8087


class MyServerRequestHandler(BaseHTTPRequestHandler):
    """Handle client's http requests.

    Methods:

    separate_path(self, path: str): Separate current resource path.
    get_current_launch_time(self): Calculate a launch time of the current input query session.
    find_query_parameter(self, param_name: str, params_dict: dict): Find necessary query parameter in the params
                                                                        dict.
    get_query_params(self, path: str): Divide full path for params and simple path.

    save_the_post(self, data: dict) -> bool: Store data to the database.
    send_posts(self, post_id=None): Send posts to the client.
    get_necessary_post(self, table_name: str, post_id) -> tuple: Get the necessary post from the table with the id.
    get_table_rows_count(self, table_name: str) -> int: Get count of the rows from the table.
    do_GET(self): Handle GET requests.
    do_POST(self): Handle POST requests.
    do_DELETE(self): Handle DELETE requests.
    do_PUT(self): Handle PUT requests.
    show_db_is_empty(self): Send error respond when there is no data in the database.
    show_no_necessary_post(self): Send error respond - no necessary post to work with.
    show_unknown_request_error(self): Send error respond - unknown request occurs.
    show_post_is_already_exists(self): Send error respond - the necessary post is already exists.
    show_no_post_id_error(self): Send error respond when there is unknown request occurs.
    show_no_necessary_attr(self): Send error respond when there is no necessary attribute in the data dict.
    create_db(db_name): Create database.
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

    def send_posts(self, post_id=None):
        """Send posts to the client.

        :param post_id: id of the post to send
        :return: None
        """

        get_all_posts_query = \
            "SELECT " \
            "user_post_info.ID, user_post_info.time_of_processing, " \
            "user_data.user_name, user_data.user_cake_day, " \
            "user_karma.post_karma, user_karma.comment_karma, user_karma.general_user_karma, " \
            "post.post_date, post.number_of_comments, post.number_of_votes, post.post_category" \
            " FROM user_post_info INNER JOIN user_data ON user_post_info.user_id = user_data.ID " \
            "INNER JOIN user_karma ON user_data.user_karma = user_karma.ID " \
            "INNER JOIN post ON user_post_info.post_id = post.ID"

        keys = (
            'id', 'time_of_processing', 'user_name', 'user_cake_day', 'post_karma', 'comment_karma',
            'general_user_karma', 'post_date', 'number_of_comments', 'number_of_votes', 'post_category'
        )

        if post_id is not None:
            get_necessary_post_query = get_all_posts_query + f" WHERE user_post_info.ID = '{post_id}';"

            with conn.cursor() as get_necessary_post_cursor:
                get_necessary_post_cursor.execute(get_necessary_post_query)
                necessary_post = get_necessary_post_cursor.fetchone()
                if necessary_post is not None:
                    res_dict = dict(zip(keys, necessary_post))
                else:
                    self.show_no_necessary_post()
                    return
        else:
            get_all_posts_query += ";"

            with conn.cursor() as get_all_posts_cursor:
                get_all_posts_cursor.execute(get_all_posts_query)
                posts = get_all_posts_cursor.fetchall()
                if posts:
                    res_dict = {i: dict(zip(keys, post)) for i, post in enumerate(posts, 1)}
                else:
                    self.show_db_is_empty()
                    return
        self.send_response(200)
        self.end_headers()
        json_posts_dict = json.dumps(res_dict)
        self.wfile.write(bytes(json_posts_dict, "utf-8"))

    def get_necessary_post(self, table_name: str, post_id) -> tuple:
        """Get the necessary post from the table with the id.

        :param table_name: table for getting post
        :param post_id: id of the post to get
        :return: the post
        """
        get_necessary_post_query = f"SELECT * FROM {table_name} WHERE ID = '{post_id}'"

        with conn.cursor() as get_necessary_post_cursor:
            get_necessary_post_cursor.execute(get_necessary_post_query)
            return get_necessary_post_cursor.fetchone()

    def get_table_rows_count(self, table_name: str) -> int:
        """Get count of the rows from the table.

        :param table_name: name of the table
        :param post_id: the id of the post to search for
        :return: a count value
        """

        get_posts_count_query = f"SELECT COUNT(*) as count FROM {table_name}"

        with conn.cursor() as get_posts_count_cursor:
            get_posts_count_cursor.execute(get_posts_count_query)
            count = get_posts_count_cursor.fetchone()
            return count[0]

    def do_GET(self):
        """Handle GET requests.

        Receives all posts' content from the database. Moreover if there is
        a special post with id its data will be received by the client.
        """
        path = self.path
        if not path.startswith('/posts'):
            self.show_unknown_request_error()
        else:
            path, params_dict = self.get_query_params(path)

            post_id = self.find_query_parameter("post_id", params_dict)

            if params_dict is not None and post_id is not None:
                self.send_posts(post_id)
            else:
                self.send_posts()

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

            count = self.get_table_rows_count("user_post_info")

            if count == 0:
                new_post_num = 1

            else:

                necessary_post = self.get_necessary_post('user_post_info', post_id)

                if necessary_post is None:

                    new_post_num = count + 1

                else:
                    self.show_post_is_already_exists()
                    return

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

                necessary_post = self.get_necessary_post('user_post_info', post_id)

                if necessary_post is not None:

                    user_data_post = self.get_necessary_post('user_data', necessary_post[1])

                    if user_data_post is None:
                        self.show_no_necessary_attr()
                        return

                    delete_user_karma_query = f"DELETE FROM user_karma WHERE ID = '{user_data_post[3]}'"
                    delete_user_data_query = f"DELETE FROM user_data WHERE ID = '{necessary_post[1]}'"
                    delete_post_query = f"DELETE FROM post WHERE ID = '{necessary_post[2]}'"
                    delete_user_post_info_query = f"DELETE FROM user_post_info WHERE ID = '{post_id}'"

                    with conn.cursor() as delete_necessary_post_cursor:
                        delete_necessary_post_cursor.execute(delete_user_karma_query)
                        delete_necessary_post_cursor.execute(delete_user_data_query)
                        delete_necessary_post_cursor.execute(delete_post_query)
                        delete_necessary_post_cursor.execute(delete_user_post_info_query)

                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b'Success ! Selected post was deleted.')
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

                necessary_post = self.get_necessary_post('user_post_info', post_id)

                if necessary_post is not None:

                    user_data_post = self.get_necessary_post('user_data', necessary_post[1])

                    try:
                        update_user_karma_query = f"UPDATE user_karma " \
                                                  f"SET post_karma = '{data.get('post_karma')}'," \
                                                  f"    comment_karma = '{data.get('comment_karma')}'," \
                                                  f"    general_user_karma = '{data.get('general_user_karma')}' " \
                                                  f"WHERE ID = '{user_data_post[3]}';"

                        update_user_data_query = f"UPDATE user_data " \
                                                 f"SET user_name = '{data.get('user_name')}'," \
                                                 f"    user_cake_day = '{data.get('user_cake_day')}' " \
                                                 f"WHERE ID = '{necessary_post[1]}';"

                        update_post_query = f"    UPDATE post " \
                                            f"SET post_date = '{data.get('post_date')}', " \
                                            f"    number_of_comments = '{data.get('number_of_comments')}', " \
                                            f"    number_of_votes = '{data.get('number_of_votes')}', " \
                                            f"    post_category = '{data.get('post_category')}' " \
                                            f"WHERE ID = '{necessary_post[2]}';"

                        update_user_post_info_query = f"UPDATE user_post_info " \
                                                      f"SET    " \
                                                      f"time_of_processing = '{data.get('time_of_processing')}' " \
                                                      f"WHERE ID = '{post_id}';"

                        with conn.cursor() as update_necessary_post_cursor:
                            update_necessary_post_cursor.execute(update_user_karma_query)
                            update_necessary_post_cursor.execute(update_user_data_query)
                            update_necessary_post_cursor.execute(update_post_query)
                            update_necessary_post_cursor.execute(update_user_post_info_query)

                        self.send_response(200)
                        self.end_headers()
                        self.wfile.write(b'Success !\n\nNote:\n\n- Impossible to change post id value so it is just '
                                         b'skipped automatically.')

                    except KeyError as e:
                        self.show_no_necessary_attr()
                        return

                else:
                    self.show_no_necessary_post()
                    return

            else:
                self.show_no_post_id_error()
                return

    def show_db_is_empty(self):
        """Send error respond when there is no data in the database."""
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'There is no data for show in the database.')

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
                                      port=DB_PORT,
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
                                port=DB_PORT,
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
