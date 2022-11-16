import pandas as pd

df = pd.read_csv(r"D:\project\NLG\fine-tunning\prepare_data/data/V2 ( 3M)/TwitterResults.csv", encoding="utf-8",
                 quoting=1)


def select_dialect(row):
    if row["dialect_1"] == row["dialect_2"]:
        return row["dialect_2"]
    elif row["dialect_2"] == "Modern Standard Arabic":
        return "Modern Standard Arabic"
    else:
        return "None"


df["dialect"] = df.apply(lambda x: select_dialect(x), axis=1)
df = df.drop(["dialect_2","dialect_1"], axis=1)
df = df[df['dialect'] != "None"]
df.to_csv(r"D:\project\NLG\fine-tunning\prepare_data/data/V2 ( 3M)/final_tweet.csv", encoding="utf-8", quoting=1,index=False)
