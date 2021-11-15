import time


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
    file_name = get_current_filename()


if __name__ == '__main__':
    main()
