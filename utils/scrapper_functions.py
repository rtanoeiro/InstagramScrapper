"""Does Stuff"""
# TODO: Get login from login_instagram class and move functions to here
import logging

from instaloader import Instaloader, TopSearchResults
from utils.login_instagram import get_cookie_location

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')

# Get instance
l = Instaloader()

def login():
    cookie_location, username = get_cookie_location()
    l.load_session_from_file(
        username=username,
        filename=cookie_location,
    )

def load_usernames_from_file(filename: str) -> list:
    """This will return an iterable list of usernames that came from a file

    Args:
        filename (str): filename to be used

    Returns:
        list: list of usernames containing that word
    """
    user_list = []
    with open(filename, "r") as f:
        lines = f.readlines()

    user_list.append(lines)

    return user_list


def get_usernames_by_search(search_words: list, iterations: int) -> list:
    """This function will return a list of usernames that appear from the search

    Args:
        search_word (str): Word to use as a search on instagram
        iterations: each run will get around 15 results, so the number of results will be around iterations *15 results

    Returns:
        list: list of usernames containing that word
    """
    user_list = []
    for search_word in search_words:
        for _ in range(iterations):
            search_results = TopSearchResults(
                context=l.context, searchstring=search_word
            ).get_prefixed_usernames()

            for result in search_results:
                user_list.append(result)

    return user_list