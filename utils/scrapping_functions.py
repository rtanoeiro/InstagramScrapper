"""Module containing functions to scrape instagram data"""
import ast
import logging
from typing import Optional

import pandas as pd
from instaloader import Hashtag, Instaloader, Profile, TopSearchResults

from utils.instagram_login import get_username_and_session_file

## TODO: Instead of querying Instagram several times, play around with insta.context.load_json and then filter the desired columns
## This will likely decrease the munging of data on the get_profile_json function
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

    Returns:
        list: list of usernames to scrape data
    """
    user_list = []
    for search_word in search_words:
        logging.info("Now getting users for the keywork search: #%s \n", search_word)
        search_results = TopSearchResults(
            context=insta.context, searchstring=search_word
        ).get_prefixed_usernames()

        for result in search_results:
            user_list.append(result)

    return user_list


def _get_usernames_from_hashtags(hashtags: list, number_of_desired_users: int) -> list:
    """This function will return a list of usernames that appear from the search

    Args:
        search_word (str): Word to use as a search on instagram
        number_of_desired_users (int): maximum number of users to grab

    Returns:
        list: list of usernames to scrape data
    """
    users_per_hashtag = number_of_desired_users // len(hashtags)
    user_list = []
    for hashtag in hashtags:
        logging.info("Now getting users for the Hashtag: #%s \n", hashtag)
        search_results = Hashtag.from_name(context=insta.context, name=hashtag)
        post_list = search_results.get_posts()

        for n_users, post in enumerate(post_list):
            if n_users == users_per_hashtag:
                break
            user_list.append(post.owner_username)

    return user_list


def _get_profile_data(profile: str):
    """
    This is a helper function to get profile data

    Args:
        profile (str): username string to scrape
    """
    return Profile.from_username(context=insta.context, username=profile)


def get_profile_json(
    user_info_source: str,
    user_info: str or list,
    number_of_posts: Optional[int],
    number_of_users: Optional[int],
    columns_with_lists: Optional[list],
):
    """Given an user_info, we return a list of dictionaries
    containing information from usernames

    Args:
        user_info_source (str): Source of data to be retrieved, can be 'hashtag', 'search' or 'file
        user_info (str or list): Based on what was selected on user_info_source,
            user_info will be routed to the respective function.
        number_of_posts (int): number of posts to retrieve data,
            otherwise most of the posts will be returned, slowing down performance
        number_of_users (int): number of users to catch, this will help select a fixed number
            of users when searching by hashtag

    Returns:
        list[dict]: Data retrieved from instaloader
    """

    if not isinstance(number_of_posts, int):
        raise TypeError("The number of posts variable has to be an integer")
    if not isinstance(number_of_users, int):
        raise TypeError("The number of posts variable has to be an integer")

    user_list = []
    if user_info_source.lower() == "hashtag":
        user_list = _get_usernames_from_hashtags(
            hashtags=user_info, number_of_desired_users=number_of_users
        )
    elif user_info_source.lower() == "search":
        user_list = _get_usernames_from_file(filename=user_info)
    elif user_info_source.lower() == "file":
        user_list = _get_usernames_from_search(search_words=user_info)
    else:
        raise ValueError(
            "The value of the variable user_info_source has to be either \
            'hashtag', 'search' or 'file"
        )

    profiles_dict = {
        "user_id": [],
        "username": [],
        "followers": [],
        "followees": [],
        "is_business_account": [],
        "biography": [],
        "profile_pic_url": [],
        "post_list": [],
        "post_date": [],
    }
    similar_accounts_dict = {"similar_accounts": []}
    for n_user, user in enumerate(user_list):
        post_list, post_dates = [], []
        logging.info(
            "Getting data for %s. It's the user number %i out of %i\n",
            user,
            n_user + 1,
            len(user_list),
        )
        profile = _get_profile_data(user)
        profiles_dict["user_id"].append(profile.userid)
        profiles_dict["username"].append(profile.username)
        profiles_dict["followers"].append(profile.followers)
        profiles_dict["followees"].append(profile.followees)
        profiles_dict["is_business_account"].append(profile.is_business_account)
        profiles_dict["biography"].append(profile.biography.replace("\n", " | "))
        profiles_dict["profile_pic_url"].append(profile.profile_pic_url)
        posts = profile.get_posts()

        for n_post, post in enumerate(posts):
            if n_post == number_of_posts:
                break
            post_dates.append(post.date)
            post_list.append(post.caption.replace("\n", " | "))

        profiles_dict["post_list"].append(post_list)
        profiles_dict["post_date"].append(post_dates)

        similar_accounts = profile.get_similar_accounts()
        for account in similar_accounts:
            similar_accounts_dict["similar_accounts"].append(account.username)

    _list_to_rows(columns_to_convert=columns_with_lists, dataframe=profiles_dict)

    exploded_dataframe = _expand_lists_into_rows(
        dataframe=pd.DataFrame(profiles_dict), columns_to_explode=columns_with_lists
    )
    exploded_dataframe.to_csv("InstagramProfileData.csv", index=False, mode="a")
    pd.DataFrame(similar_accounts_dict).to_csv(
        "SimilarProfilesData.csv", index=False, mode="a", header=False
    )


def _list_to_rows(columns_to_convert: list, dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Helper function to convert a column of the DataFrame into
    several rows via the .explode() method

    Args:
        columns_to_convert (list): columns to be exploded
        dataframe (pd.DataFrame): Full dataframe containing columns

    Returns:
        pd.DataFrame: Dataframe with converted columns
    """
    for column in columns_to_convert:
        if isinstance(dataframe[column][0], list):
            logging.info("%s is already a list, no need to convert", column)
        else:
            dataframe[column] = dataframe[column].apply(_convert_to_list)


def _convert_to_list(column):
    logging.info("%s is not a list, convert string into list", column)
    return ast.literal_eval(column)


def _expand_lists_into_rows(
    dataframe: pd.DataFrame, columns_to_explode: list
) -> pd.DataFrame:
    """
    This is a helper function to expand the DataFrame to contain
    one line for each item of the list in the column.
    Args:
        dataframe (pd.DataFrame): Dataframe to expand
        columns_to_explode (list): columns to use

    Returns:
        pd.DataFrame: Exploded DataFrame
    """
    logging.info("Expanding all columns containing a list...")
    dataframe_exploded = dataframe.explode(column=columns_to_explode)
    logging.info("DataFrame Successfully expanded")

    return dataframe_exploded
