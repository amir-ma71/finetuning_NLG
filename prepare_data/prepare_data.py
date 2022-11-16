import pandas as pd
from normalizer.TextNormalizer import Normalizer
import re

norm_ar = Normalizer(language='ar', remove_extra_spaces=True,
                     rtl_style=True,
                     rtl_numbers_refinement=True,
                     remove_diacritics=True,
                     affix_spacing=True,
                     remove_repeated_chars=True,
                     punctuation_spacing=True,
                     hashtags_refinement=True,
                     entity_cleaning=True,
                     remove_punctuation=False,
                     remove_email=True,
                     remove_url=True,
                     remove_mobile_number=True,
                     remove_home_number=True,
                     remove_emoji=True,
                     remove_mention=True,
                     remove_html=True,
                     remove_numbers=True,
                     remove_english=True,
                     remove_newline=True)

c = 1


def cleaner(x):
    global c
    x = re.sub(r'[^\w\s]', '', x)
    print(c)
    c += 1
    return x


df = pd.read_csv("TweetsArabic2.csv", encoding="utf-8")

# df = df[0:100]

df["cleaned"] = df["tweet"].apply(lambda x: norm_ar.normalize(x))
df["cleaned"] = df["cleaned"].apply(lambda x: cleaner(x))

clean_tw_list = []
for tw in df.iterrows():
    tweet = tw[1]["cleaned"]
    if len(tweet.split()) >= 5:
        clean_tw_list.append(tw[1]["cleaned"])

print("*******",len( clean_tw_list))

out = pd.DataFrame()
out["tweet"] = clean_tw_list
out.to_csv("cleand_tweet.csv", encoding="utf-8", index=False, quoting=1)
