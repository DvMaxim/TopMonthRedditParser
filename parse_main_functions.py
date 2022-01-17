"""The module for the functions which have the main functional.

:func filter_post_list: produce filter process over the list of posts
:func beta_parser: test parsing process on some single post
:func parser: launch parser
"""

import os
import logging
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from parse_sub_functions import parse_el


BROWSER_NAME = 'yandexdriver.exe'
module_logger = logging.getLogger("parserApp.parse_main_functions")


def filter_post_list(post_list: list,
                     driver, corr_len: str, max_posts_count: int,
                     start_index: int = 0) -> (int, list):
    """Filter the list of posts.

        Receive the list of posts and filter it from the start_index position.
        This position will appear only if didn't reached necessary number of relevant posts
        (in our case it is always 100) by the first filter process. Moreover current filter process
        is pretty simple: we just run through the list and parse a single element. If some troubles
        appear during the parsing process of the post we will just delete it from the posts list.
        If element is relevant it will remain in our list and the number of correct elements will be increased by one.

        :param post_list: the list of posts that we need to filter
        :type: list of selenium web-elements
        :param driver: the browser object
        :type: selenium.webdriver.chrome.webdriver.WebDriver
        :param corr_len: number of corrects posts
        :type: int
        :param max_posts_count: number of posts that we need to parse
        :type: int
        :param start_index: index of the first element in the post_list which we begin iterate from
        :type: int
        :return: updated number of the correct posts / the filtered list of posts with only relevant one's
        :rtype: int / list of selenium web-elements
        """
    logger = logging.getLogger("parserApp.parse_main_functions.filter_post_list")
    logger.debug("Start filtering process with current correct posts = %d" % corr_len)

    if start_index:
        post_list = post_list[start_index:]

    for el in list(post_list):
        el_index = post_list.index(el)
        if corr_len < max_posts_count:
            logger.debug("Try to parse current post element with the %d index in the posts list.\n" % el_index)
            if not parse_el(post_list[el_index], driver):
                post_list.remove(el)
                logger.debug(
                    "Element with %d index was removed from the posts list because it was not correct." % el_index)
            else:
                corr_len += 1
                logger.debug(
                    "Element with %d index in the posts list was parsed successfully." % el_index)
        else:
            return corr_len, post_list[:el_index]

    return corr_len, post_list


def beta_parser(url: str) -> None:
    """Test parsing process.

        This is a small version of the parser function where
        we process a one post. It is useful for developers because
        they can easily test and debug our parsing process, but, it is
        significant to say that this function will be never used in the final version of project
        cause it aims only for testing and improving our parsing algorithms.

        :param url: web-source to parse
        :type: str
        :return: None
        :rtype: None
        """

    logger = logging.getLogger("parserApp.parse_main_functions.beta_parser")
    logger.debug("Start session with a browser.")
    options = webdriver.ChromeOptions()
    # options.headless = True  # this is hide your browser
    project_location = os.path.split(__file__)[0]
    binary_yandex_driver_file = project_location + r'\\' + BROWSER_NAME  # path to YandexDriver
    driver = webdriver.Chrome(binary_yandex_driver_file, options=options)
    driver.maximize_window()

    try:
        driver.get(url)
        initial_posts = driver.find_elements(By.CLASS_NAME, 'Post')
        logger.debug("Testing a parsing process on the single post element.")
        if parse_el(initial_posts[0], driver):
            logger.debug("Parser has successfully finished.")
        else:
            logger.error("Error during the parsing process.")

    except Exception as ex:
        logger.error("Error during the parsing process: %s" % ex)
    finally:
        logger.debug("End session with a browser.")
        driver.close()
        driver.quit()


def parser(url: str, num_posts: int) -> None:
    """Launch parser.

    Create a browser, load first 100 elements and try
    to parse them. If some post will be corrupted load more
    new one's and reproduce this cycle until you get 100 relevant posts.

    :param url: web-source to parse
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
    project_location = os.path.split(__file__)[0]
    binary_yandex_driver_file = project_location + r'\\' + BROWSER_NAME  # path to YandexDriver
    driver = webdriver.Chrome(binary_yandex_driver_file, options=options)
    driver.maximize_window()

    try:
        driver.get(url)
        logger.debug("Checking page for parsing availability.")
        initial_posts = driver.find_elements(By.CLASS_NAME, 'Post')
        if not initial_posts:
            message = 'Impossible to parse because number of post on the page is 0.'
            logger.error("%s" % message)
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
                    corr_len, filtered_posts = filter_post_list(initial_posts, driver, corr_len, num_posts)
                    is_first_filter = False
                else:
                    logger.debug(f"Produce parsing process from the {new_filter_start} position from the current "
                                 f"posts list.")
                    corr_len, filtered_posts = filter_post_list(initial_posts, driver, corr_len, num_posts,
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