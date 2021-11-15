"""The module for most general functions of the project.

:func get_current_filename: create a filename for a result file
:func main: run main application's functions.
"""


import time
import os
import logging
from parse_main_functions import parser


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


URL = 'https://www.reddit.com/top/?t=month'
NUM_POSTS = 100


def main() -> None:
    """Run main application's functions."""
    file_name = get_current_filename()

    if not os.path.isdir("logging_data"):
        os.mkdir("logging_data")

    logger = logging.getLogger("parserApp")
    logger.setLevel(logging.DEBUG)

    # create the logging file handler
    fh = logging.FileHandler(f"logging_data\\logger - {file_name.replace('txt', '')}.log")

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)

    # add handler to logger object
    logger.addHandler(fh)

    logger.info("Program started.")
    file = open(file_name, 'w')
    file.close()
    parser(URL, file_name, NUM_POSTS)
    logger.info("Program finished.")


if __name__ == '__main__':
    main()
