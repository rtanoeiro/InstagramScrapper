"""Module containing functions to scrape instagram data"""
import logging

from instaloader import Instaloader, TopSearchResults
from utils.instagram_login import InstagramLogin

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')

# Get instance
insta = Instaloader()
insta_login = InstagramLogin()

class ScrappingFunctions:
    """
    This Class will contain several functions used for scrapping data on Instagram
    based on the purpose for theses scripts, which is scrapping data from the website
    """

    def __init__(self) -> None:
        self.cookie_location, self.username = insta_login.get_cookie_file_and_username()
        insta.load_session_from_file(
            username=self.username,
            filename=self.cookie_location,
        )

    def load_usernames_from_file(self, filename: str) -> list:
        """This will return an iterable list of usernames that came from a file

        Args:
            filename (str): filename to be used

        Returns:
            list: list of usernames containing that word
        """
        user_list = []
        with open(filename, "r", encoding="UTF-8") as file:
            lines = file.readlines()

        user_list.append(lines)

        return user_list


    def get_usernames_by_search(self, search_words: list, iterations: int) -> list:
        """This function will return a list of usernames that appear from the search

        Args:
            search_word (str): Word to use as a search on instagram
            iterations: each run will get around 15 results,
            so the number of results will be around iterations *15 results

        Returns:
            list: list of usernames containing that word
        """
        user_list = []
        for search_word in search_words:
            for _ in range(iterations):
                search_results = TopSearchResults(
                    context=insta.context, searchstring=search_word
                ).get_prefixed_usernames()

                for result in search_results:
                    user_list.append(result)

        return user_list