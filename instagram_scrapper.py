"""Does Stuff"""

import ast

import pandas as pd
from utils.scrapping_functions import ScrappingFunctions

scrapping = ScrappingFunctions()

users_data, similar_accounts = scrapping.get_profile_json(["candy"], number_of_posts=50)
users_data.to_csv("InstagramData.csv", index=False, mode="a")
similar_accounts.to_csv("SimilarAccounts.csv", index=False)


to_convert = pd.read_csv(
    "InstagramData.csv"
)  # .to_excel("InstagramData.xlsx", index=False)
similar_profiles = []
for line in to_convert["similar_accounts"]:
    similar_profiles.append(ast.literal_eval(line))
    print(similar_profiles)
pd.DataFrame({"SimilarProfiles":similar_profiles}).to_csv("SimilarProfiles.csv", index=False)
to_convert.explode(["post_list", "posts_dates"])
to_convert.to_excel("InstagramAccounts.xlsx", index=False)
