"""Module containing functions to scrape instagram data"""
import logging

from instaloader import Instaloader, TopSearchResults, Profile, Hashtag
from utils.instagram_login import InstagramLogin

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')

insta = Instaloader()
insta_login = InstagramLogin()

class ScrappingFunctions:
    """
    This Class will contain several functions used for scrapping data on Instagram
    based on the purpose for theses scripts, which is scrapping data from the website

    The main purpose is based on a list of usernames scrape data from whatever is available
    from that username.
    """

    def __init__(self) -> None:
        self.cookie_location, self.username = insta_login.get_cookie_file_and_username()
        insta.load_session_from_file(
            username=self.username,
            filename=self.cookie_location,
        )

    def _get_usernames_from_file(self, filename: str) -> list:
        """This will return an iterable list of usernames that came from a file
        The file should contain one username per line

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


    def _get_usernames_from_search(self, search_words: list) -> list:
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
            search_results = TopSearchResults(
                context=insta.context, searchstring=search_word
            ).get_prefixed_usernames()

            for result in search_results:
                user_list.append(result)

        return user_list

    def _get_usernames_from_hashtags(self, hashtags: list) -> list:
        """This function will return a list of usernames that appear from the search

        Args:
            search_word (str): Word to use as a search on instagram
            iterations: each run will get around 15 results,
            so the number of results will be around iterations *15 results

        Returns:
            list: list of usernames containing that word
        """
        ## TODO: Adjust to return profiles associated to hashtag
        user_list = []
        for hashtag in hashtags:
            search_results = Hashtag.from_name(context=insta.context, name=hashtag)

            for result in search_results:
                user_list.append(result)

        return user_list

    def _get_profile_data(self, profile: str):
        """
        This is a helper function to get profile data

        Args:
            profile (str): username string to scrape
        """
        return Profile.from_username(context=insta.context, username=profile)

    def get_profile_json(self, user_info: str or list) -> list[dict]:
        """Given an user_info, we return a list of dictionaries
        containing information from usernames

        Args:
            user_info (str or list): If an str is given, we get the user list from a file
            if a list is given, we get from a search

        Returns:
            list[dict]: Data retrieved from instaloader
        """
        ## TODO: Add options to get profile data, from hashtag, search and filename
        user_list, post_list, post_dates = [], [], []
        if user_info is str:
            user_list = self._get_usernames_from_file(filename=user_info)
        elif user_info is list:
            user_list = self._get_usernames_from_search(search_words=user_info)

        profiles_dict = {
            "followers": [],
            "username": [],
            "external_url": [],
            "is_business_account": [],
            "biography": [],
            "profile_pic_url": [],
            "post_list": [],
            "posts_dates": [],
            "similar_accounts": [],
        }
        for i, user in enumerate(user_list):
            print(
                f"Getting data for {user}. It's the user number {i+1} out of {len(user_list)}\n"
            )
            profile =self._get_profile_data(user)
            profiles_dict["username"].append(profile.username)
            profiles_dict["followers"].append(profile.followers)
            profiles_dict["external_url"].append(profile.external_url)
            profiles_dict["is_business_account"].append(profile.is_business_account)
            profiles_dict["biography"].append(profile.biography)
            profiles_dict["profile_pic_url"].append(profile.profile_pic_url)
            posts = profile.get_posts()

            for post in posts:
                post_dates.append(post.date)
                post_list.append(post.caption)

            profiles_dict["post_list"].append(post_list)
            profiles_dict["posts_dates"].append(post_dates)

            similar_accounts = profile.get_similar_accounts()
            similar_accounts_list = []
            for account in similar_accounts:
                similar_accounts_list.append(account.username)

            profiles_dict["similar_accounts"].append(similar_accounts_list)

        return profiles_dict
