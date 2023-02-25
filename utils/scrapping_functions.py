"""Module containing functions to scrape instagram data"""
import logging
import pandas as pd

from instaloader import Instaloader, TopSearchResults, Profile, Hashtag
from utils.instagram_login import get_username_and_session_file

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s %(levelname)s: %(message)s"
)

insta = Instaloader()
username, session_file = get_username_and_session_file()
insta.load_session_from_file(
    username=username,
    filename=session_file,
)


def _get_usernames_from_file(filename: str) -> list:
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

def _get_usernames_from_search(search_words: list) -> list:
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

def _get_usernames_from_hashtags(hashtags: list) -> list:
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

    return search_results

def _get_profile_data(profile: str):
    """
    This is a helper function to get profile data

    Args:
        profile (str): username string to scrape
    """
    return Profile.from_username(context=insta.context, username=profile)

def get_profile_json(
    user_info: str or list, number_of_posts: int
) -> pd.DataFrame:
    """Given an user_info, we return a list of dictionaries
    containing information from usernames

    Args:
        user_info (str or list): If an str is given, we get the user list from a file
            if a list is given, we get from a search
        number_of_posts (int): number of posts to retrieve data,
            otherwise most of the posts will be returned, slowing down performance

    Returns:
        list[dict]: Data retrieved from instaloader
    """
    ## TODO: Add options to get profile data, from hashtag, search and filename
    user_list, post_list, post_dates = [], [], []
    if isinstance(user_info, str):
        user_list = _get_usernames_from_file(filename=user_info)
    elif isinstance(user_info, list):
        user_list = _get_usernames_from_search(search_words=user_info)

    profiles_dict = {
        "user_id": [],
        "username": [],
        "followers": [],
        "followees": [],
        "is_business_account": [],
        "biography": [],
        "profile_pic_url": [],
        "post_list": [],
        "posts_dates": [],
        "similar_accounts": [],
    }

    for i, user in enumerate(user_list):
        logging.info(
            "Getting data for %s. It's the user number %i out of %i\n", user, i+1, len(user_list)
        )
        profile = _get_profile_data(user)
        profiles_dict["user_id"].append(profile.userid)
        profiles_dict["username"].append(profile.username)
        profiles_dict["followers"].append(profile.followers)
        profiles_dict["followees"].append(profile.followees)
        profiles_dict["is_business_account"].append(profile.is_business_account)
        profiles_dict["biography"].append(profile.biography)
        profiles_dict["profile_pic_url"].append(profile.profile_pic_url)
        posts = profile.get_posts()

        for n, post in enumerate(posts):
            if n == number_of_posts:
                break
            post_dates.append(post.date)
            post_list.append(post.caption)


        profiles_dict["post_list"].append(post_list)
        profiles_dict["posts_dates"].append(post_dates)

        similar_accounts = profile.get_similar_accounts()
        similar_accounts_list = []
        for account in similar_accounts:
            similar_accounts_list.append(account.username)

        profiles_dict["similar_accounts"].append(similar_accounts_list)

    return pd.DataFrame(profiles_dict)
