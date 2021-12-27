"""The module for most general functions of the project.

:func get_current_filename: create a filename for a result file
:func main: run main application's functions.
"""

import time
import os
import argparse
import logging
import requests
from parse_main_functions import parser


URL = 'https://www.reddit.com/top/?t=month'

FILENAME_RESOURCE_URL = 'http://localhost:8087/filename'


def get_args_from_the_cmd():
    """Get optional arguments from the command line.

    :return: a tuple of the arguments
    """
    parser = argparse.ArgumentParser(description='Posts number / result file name')

    parser.add_argument('-p_n', '--posts_number'
                        , metavar='posts_number'
                        , type=int
                        , help='Get a number of the posts which we need to parse.'
                        , default=100
                        , dest='posts_num'
                        , required=False)

    parser.add_argument('-f_n', '--file_name'
                        , metavar='result_file_name'
                        , type=str
                        , help='A name of the result file of the program.'
                        , default=get_current_filename()
                        , dest='res_file_name'
                        , required=False
                        )

    args = parser.parse_args()
    return args.posts_num, args.res_file_name


def get_current_filename() -> str:
    """Create a filename for a result file.

    Create a filename based on the current date using
    the next time template: year/month/day/hours/minutes.
    Also it adds 'reddit-' string to the beginning of the received
    formatted date string and file's extension to the end of it.

    :return: filename of the result file
    :rtype: str
    """
    time_tuple = time.localtime(time.time())
    time_list = list(time_tuple)[:5]
    time_list = ['0' + str(time_list[i]) if time_list[i] < 10 else str(time_list[i]) for i in range(len(time_list))]
    return 'reddit-' + ''.join(time_list) + '.txt'


def main() -> None:
    """Run main application's functions."""

    num_posts, file_name = get_args_from_the_cmd()

    logger = logging.getLogger("parserApp")
    logger.setLevel(logging.DEBUG)

    # create the logging file handler
    fh = logging.FileHandler(f"logging_data\\logger - {file_name.replace('txt', '')}.log")

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)

    # add handler to logger object
    logger.addHandler(fh)

    response = requests.post(FILENAME_RESOURCE_URL, json={
        'file_name': file_name
    })

    if not os.path.isdir("logging_data"):
        os.mkdir("logging_data")

    logger.info("Program started.")

    if response.status_code == 200:
        logger.debug(f"Result file {file_name} has been created successfully.")
    elif response.status_code == 404:
        logger.debug(f"Error during creation result file {file_name}.")

    parser(URL, file_name, num_posts)
    logger.info("Program finished.")


if __name__ == '__main__':
    main()
