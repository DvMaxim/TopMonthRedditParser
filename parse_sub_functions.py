"""The module for functions that are used in functions from the parse_main_functions.py module.

:func parse_el: parse post and get all necessary data from it
:func parse_karma: look through the user page and get post karma and comment karma
:func parse_post_date: look through the post page and get post date
:func is_user_html_a_warning: check the correctness of the page where we need to come
"""


import logging
import uuid
import requests
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains


HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 YaBrowser/21.9.2.169 Yowser/2.5 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'}
# Special data about browser which is used when we require to some web-source to get necessary web page

HOST = 'https://www.reddit.com'
# General web address of the source that we need to work with

module_logger = logging.getLogger("parserApp.parse_sub_functions")


def parse_el(el, file_name: str, driver) -> bool:
    """Get necessary data about the current user.

    :param el: post element that we need to parse
    :type: selenium.webdriver.remote.webelement.WebElement
    :param file_name: name of the result text file with all data about all parsed posts
    :type: str
    :param driver: the browser object
    :type: selenium.webdriver.chrome.webdriver.WebDriver
    :return: True signal if post element parsed well and False signal if it wasn't
    :rtype: boolean
    """
    logger = logging.getLogger("parserApp.parse_sub_functions.parse_el")

    logger.info("Begin parsing process over the post element.\n\n")

    elem_source = el.get_attribute('innerHTML')
    parse_list = []
    el_soup = BeautifulSoup(elem_source, 'html.parser')

    unique_id = uuid.uuid1().hex
    logger.debug("Unique_id: %s." % unique_id)
    parse_list.append(unique_id)

    post_link = el_soup.find('a', class_='_3jOxDPIQ0KaOWpzvSQo-1s')
    if not post_link:
        logger.error("No post link, impossible to continue parsing process.")
        return False
    post_link = post_link.get('href')
    logger.debug("Post link: %s." % post_link)
    parse_list.append(post_link)

    user = el_soup.find('a', {"class": ["_2tbHP6ZydRpjI44J3syuqC", "_23wugcdiaj44hdfugIAlnX", "oQctV4n0yUb0uiHDdGnmE"]})
    if not user:
        logger.error("No user block on the page, impossible to continue parsing process.")
        return False

    username = user.text.strip().replace('u/', '')
    logger.debug("Username: %s." % username)
    parse_list.append(username)

    link_second_part = user.get('href')
    user_link = HOST + link_second_part
    user_html = requests.get(user_link, headers=HEADERS)
    if not user_html.status_code == 200:
        logger.error("Impossible to refer to the user page.")
        return False

    user_soup = BeautifulSoup(user_html.text, 'html.parser')
    if is_user_html_a_warning(user_soup):
        logger.error("User page is not available for parsing process.")
        return False

    user_karma = user_soup.find('span', {"id": "profile--id-card--highlight-tooltip--karma"})
    if not user_karma:
        logger.error("No user karma on the page, impossible to continue parsing process.")
        return False
    user_karma = user_karma.text
    logger.debug("User karma: %s." % user_karma)
    parse_list.append(user_karma)

    user_cake_day = user_soup.find('span', {"id": "profile--id-card--highlight-tooltip--cakeday"})
    if not user_cake_day:
        logger.error("No user cake day on the page, impossible to continue parsing process.")
        return False
    user_cake_day = user_cake_day.text
    logger.debug("User cake day: %s." % user_cake_day)
    parse_list.append(user_cake_day)

    post_karma, comment_karma = parse_karma(driver, user_link)

    logger.debug("Post karma: %s." % post_karma)
    logger.debug("Comment karma: %s." % comment_karma)

    parse_list.append(post_karma)
    parse_list.append(comment_karma)

    post_date = parse_post_date(driver, post_link)
    logger.debug("Post date: %s." % post_date)
    parse_list.append(post_date)

    number_of_comments = el_soup.find('span', class_='FHCV02u6Cp2zYL0fhQPsO')
    if not number_of_comments:
        logger.error("No number of comments info on the page, impossible to continue parsing process.")
        return False
    number_of_comments = number_of_comments.text.split()[0]
    logger.debug("Number of comments: %s." % number_of_comments)
    parse_list.append(number_of_comments)

    number_of_votes = el_soup.find('div', {"class": ["_1rZYMD_4xY3gRcSS3p8ODO", "_3a2ZHWaih05DgAOtvu6cIo"]})
    if not number_of_votes:
        logger.error("No number of votes info on the page, impossible to continue parsing process.")
        return False
    number_of_votes = number_of_votes.text
    logger.debug("Number of votes: %s." % number_of_votes)
    parse_list.append(number_of_votes)

    post_category = el_soup.find('a', class_='_3ryJoIoycVkA88fy40qNJc')
    if not post_category:
        logger.error("No post category on the page, impossible to continue parsing process.")
        return False
    post_category = post_category.get('href').replace('/r', '')
    post_category = post_category.replace('/', '')
    logger.debug("Post category: %s.\n" % post_category)
    parse_list.append(post_category)

    parse_str = ' | '.join(parse_list)

    with open(file_name, "a") as file:
        file.write(parse_str)
        file.write('\n')

    logger.info("Parsing process over the post element finish successfully.\n\n")

    return True


def parse_karma(driver, user_link: str) -> (str, str):
    pass


def parse_post_date(driver, post_link) -> str:
    pass


def is_user_html_a_warning(user_soup) -> bool:
    pass
