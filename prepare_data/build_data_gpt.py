import pandas as pd

df = pd.read_csv(r"D:\project\NLG\fine-tunning\prepare_data\data\V2 ( 3M)\final_blance_2M.csv", encoding="utf-8")

c = 1
def build_data(row):
    global c
    text = row["text"]
    dialect = row["dialect"]
    sentiment = row["sentiment"]
    topic = row["topic"]

    gpt_txt = "<|" + dialect + "|><|" + topic + "|><|" + sentiment + "|>" + " " + text
    print(c)
    c += 1
    return gpt_txt


text_list = []
for tw in df.iterrows():
    text_list.append(build_data(tw[1]))

gpt_df = pd.DataFrame()

gpt_df["text"] = text_list

gpt_df.to_csv(r"D:\project\NLG\fine-tunning\prepare_data\data\V2 ( 3M)\gpt_dataset.csv", encoding="utf-8", index=False, quoting=1)