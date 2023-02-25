"""Does Stuff"""

from utils.scrapping_functions import get_profile_json

get_profile_json(
    user_info_source="hashtag",
    user_info=["cat", "dog", "bike"],
    number_of_posts=5,
    number_of_users=10,
    columns_with_lists=["post_list", "post_date"],
)
