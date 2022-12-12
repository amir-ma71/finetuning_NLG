import pandas as pd
import re


def cleaner(x):
    try:
        x = re.sub(r'\n', ' ', x)  # remove ENTER
        x = re.sub(r'\r', ' ', x)  # remove \r
        x = re.sub(r"(?:\@|https?\://)\S+", "", x)  # remove mentions and links
        x = re.sub(r'\s*[A-Za-z]+\b', '', x)  # remove english char
        x = re.sub(r'(\W)(?=\1)', '', x)  # remove repeated punctuation
        x = x.strip()
        if len(x) > 75:
            return x
        else:
            return None
    except:
        return None


iraq = pd.read_csv(r"D:\project\NLG\fine-tunning\prepare_data\data\V3\iraq_corpus2.csv",quoting=1, sep="~", encoding="utf-8",engine="python", error_bad_lines=False,encoding_errors='ignore')
iraq.columns = ["user_id",'text']
print(" iraq dataset loaded ....")

iraq_clean = pd.DataFrame()
iraq_clean["user_id"] = iraq["user_id"]
iraq_clean["clean_text"] = iraq["text"].apply(lambda x: cleaner(x))
print(" iraq dataset cleaned .... len: ", len(iraq_clean.clean_text))

del iraq
print(" iraq dataset deleted ....")

iraq_clean = iraq_clean.drop_duplicates(subset=['clean_text'])
print(" iraq dataset remove duplicated ...." )
print(" iraq dataset len: ", len(iraq_clean.clean_text) )

iraq_clean = iraq_clean.dropna(subset=['clean_text'])
print(" iraq dataset remove Null ...." )
print(" iraq dataset len: ", len(iraq_clean.clean_text) )


syria = pd.read_csv(r"D:\project\NLG\fine-tunning\prepare_data\data\V3\syria_corpus2.csv",quoting=1, sep="~", encoding="utf-8",engine="python", error_bad_lines=False,encoding_errors='ignore')
syria.columns = ["user_id",'text']
print(" syria dataset loaded ....")

syria_clean = pd.DataFrame()
syria_clean["user_id"] = syria["user_id"]
syria_clean["clean_text"] = syria["text"].apply(lambda x: cleaner(x))
print(" syria dataset cleaned .... len: ", len(syria_clean.clean_text))

del syria
print(" syria dataset deleted ....")

syria_clean = syria_clean.drop_duplicates(subset=['clean_text'])
print(" syria dataset remove duplicated ...." )
print(" syria dataset len: ", len(syria_clean.clean_text) )

syria_clean = syria_clean.dropna(subset=['clean_text'])
print(" syria dataset remove Null ...." )
print(" syria dataset len: ", len(syria_clean.clean_text) )

print(" appending datasets ....")
df = iraq_clean.append([syria_clean]).reset_index(drop=True)

print(" full dataset len: ", len(df.clean_text) )

del iraq_clean
del syria_clean

df = df.drop_duplicates(subset=['clean_text'])
print(" full dataset remove duplicated ...." )
print(" full dataset len: ", len(df.clean_text) )
df.to_csv("full_3M.csv",encoding= "utf-8",index=False, quoting=1)




