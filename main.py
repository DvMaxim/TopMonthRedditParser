"""The module for most general functions of the project.

:func get_current_filename: create a filename for a result file
:func main: run main application's functions.
"""

import time
import os
import argparse
import logging
from parse_main_functions import parser


URL = 'https://www.reddit.com/top/?t=month'

def get_args_from_the_cmd():
    """Get optional arguments from the command line.

    :return: a tuple of the arguments
    """
    parser = argparse.ArgumentParser(description='Posts number')

    parser.add_argument('-p_n', '--posts_number'
                        , metavar='posts_number'
                        , type=int
                        , help='Get a number of the posts which we need to parse.'
                        , default=1
                        , dest='posts_num'
                        , required=False)

    args = parser.parse_args()
    return args.posts_num


def get_current_launch_time() -> str:
    """Calculate a launch time of the program.

    Calculate a launch time of the program based on the current date using
    the next time template: year/month/day/hours/minutes.

    :return: a launch time of the program
    :rtype: str
    """
    time_tuple = time.localtime(time.time())
    time_list = list(time_tuple)[:5]
    time_list = ['0' + str(time_list[i]) if time_list[i] < 10 else str(time_list[i]) for i in range(len(time_list))]
    return ''.join(time_list)


def main() -> None:
    """Run main application's functions."""

    launch_time = get_current_launch_time()

    num_posts = get_args_from_the_cmd()

    logger = logging.getLogger("parserApp")
    logger.setLevel(logging.DEBUG)

    # create the logging file handler
    fh = logging.FileHandler(f"logging_data\\logger - {launch_time.replace('txt', '')}.log")

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)

    # add handler to logger object
    logger.addHandler(fh)

    if not os.path.isdir("logging_data"):
        os.mkdir("logging_data")

    logger.info("Program started.")

    parser(URL, num_posts)
    logger.info("Program finished.")


if __name__ == '__main__':
    main()
