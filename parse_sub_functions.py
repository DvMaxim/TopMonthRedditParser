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

HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 YaBrowser/21.9.2.169 Yowser/2.5 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'}
# Special data about browser which is used when we require to some web-source to get necessary web page

HOST = 'https://www.reddit.com'
# General web address of the source that we need to work with

module_logger = logging.getLogger("parserApp.parse_sub_functions")


def parse_el(el, file_name: str, driver) -> bool:
    """Get necessary data about the current user."""
    pass


def parse_karma():
    pass


def parse_post_date():
    pass


def is_user_html_a_warning():
    pass
