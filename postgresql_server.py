import psycopg2
from psycopg2 import Error

USER = "postgres"
PASSWORD = "5432112345"
HOST = "127.0.0.1"
PORT = "5432"
BASE_DB = "postgres"

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

def main():

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

        with conn.cursor() as cursor:
            cursor.execute(create_user_karma_query)

        create_post_query = '''CREATE TABLE IF NOT EXISTS post
                          (ID serial PRIMARY KEY     NOT NULL,
                          post_date           varchar(50)    NOT NULL,
                          number_of_comments         varchar(50)    NOT NULL,
                          number_of_votes           varchar(50)    NOT NULL,
                          post_category           varchar(50)    NOT NULL
                          ); '''

        with conn.cursor() as cursor:
            cursor.execute(create_post_query)

        create_user_query = '''CREATE TABLE IF NOT EXISTS user_data
                                  (ID serial PRIMARY KEY     NOT NULL,
                                  user_name           varchar(50)    NOT NULL,
                                  user_cake_day         varchar(50)    NOT NULL,
                                  user_karma           INTEGER    NOT NULL,
                                  FOREIGN KEY (user_karma) REFERENCES user_karma (ID) ON DELETE CASCADE ON UPDATE CASCADE 
                                  ); '''

        with conn.cursor() as cursor:
            cursor.execute(create_user_query)

        create_user_post_info_query = '''CREATE TABLE IF NOT EXISTS user_post_info
                                          (ID serial PRIMARY KEY     NOT NULL,
                                          user_id           INTEGER    NOT NULL,
                                          post_id         INTEGER    NOT NULL,
                                          time_of_processing           varchar(50)    NOT NULL,
                                          FOREIGN KEY (user_id) REFERENCES user_data (ID) ON DELETE CASCADE ON UPDATE CASCADE,
                                          FOREIGN KEY (post_id) REFERENCES post (ID) ON DELETE CASCADE ON UPDATE CASCADE
                                          ); '''

        with conn.cursor() as cursor:
            cursor.execute(create_user_post_info_query)

    except (Exception, Error) as error:
        print("Exception during working with PostgreSQL", error)
    finally:
        if conn:
            conn.close()
            print("Close main connection with PostgreSQL.")


if __name__ == "__main__":
    main()
