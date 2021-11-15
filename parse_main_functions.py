"""The module for the functions which have the main functional.

:func filter_post_list: produce filter process over the list of posts
:func beta_parser: test parsing process on some single post
:func parser: launch parser
"""

import logging
from selenium import webdriver
from selenium.webdriver.common.by import By


module_logger = logging.getLogger("parserApp.parse_main_functions")


def filter_post_list(post_list: list, file_name: str,
                     driver, corr_len: str, max_posts_count: int,
                     start_index: int = 0) -> (int, list):
    pass


def beta_parser(url: str, file_name: str) -> None:
    pass


def parser(url: str, file_name: str, num_posts: int) -> None:
    """Launch parser.

    Create a browser, load first 100 elements and try
    to parse them. If some post will be corrupted load more
    new one's and reproduce this cycle until you get 100 relevant posts.

    :param url: web-source to parse
    :type: str
    :param file_name: name of the result text file with all data about all parsed posts
    :type: str
    :param num_posts: number of posts that we need to parse
    :type: int
    :return: None
    :rtype: None
    """

    logger = logging.getLogger("parserApp.parse_main_functions.parser")
    logger.debug("Start session with a browser.")

    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    binary_yandex_driver_file = r'D:\Python Projects\RedditParser\yandexdriver.exe'  # path to YandexDriver
    driver = webdriver.Chrome(binary_yandex_driver_file, options=options)
    driver.maximize_window()

    try:
        driver.get(url)
        logger.debug("Checking page for parsing availability.")
        initial_posts = driver.find_elements(By.CLASS_NAME, 'Post')
        if not initial_posts:
            message = 'Impossible to parse because number of post on the page is 0.'
            logger.error("%s" % message)
            with open(file_name, "w") as file:
                file.write(message)
                file.write('\n')
            return
        logger.debug("Page is available. Start parsing process.")
        is_first_filter = True
        correct_posts_list = []
        corr_len = 0
        new_filter_start = 0
        while True:
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
            initial_posts = driver.find_elements(By.CLASS_NAME, 'Post')
            len_list = len(initial_posts)
            if len_list >= num_posts:
                if is_first_filter:
                    logger.debug("Produce first time parsing process from the beginning of the current post list.")
                    corr_len, filtered_posts = filter_post_list(initial_posts, file_name, driver, corr_len, num_posts)
                    is_first_filter = False
                else:
                    logger.debug(f"Produce parsing process from the {new_filter_start} position from the current "
                                 f"posts list.")
                    corr_len, filtered_posts = filter_post_list(initial_posts, file_name, driver, corr_len, num_posts,
                                                                new_filter_start)
                logger.debug("Correct posts list length after filtering %d" % corr_len)
                correct_posts_list.extend(filtered_posts)
                if corr_len < num_posts:
                    new_filter_start = len_list
                    continue
                else:
                    logger.debug("Finish parsing process.")
                    break

    except Exception as ex:
        logger.error("Error during the parsing process: %s" % ex)
    finally:
        logger.debug("End session with a browser.")
        driver.close()
        driver.quit()


