import pandas as pd
import functools as ft

iraq1_dialect = pd.read_csv(r"D:\project\NLG\fine-tunning\prepare_data/data/V2 ( 3M)/result_Dialect_iraq1.csv", encoding="utf-8", quoting=1).drop_duplicates()
print(1)
iraq1_senti = pd.read_csv(r"D:\project\NLG\fine-tunning\prepare_data/data/V2 ( 3M)/result_sentiment_iraq1.csv", encoding="utf-8", quoting=1).drop_duplicates()
print(2)
iraq1_topic = pd.read_csv(r"D:\project\NLG\fine-tunning\prepare_data/data/V2 ( 3M)/result_topic_iraq1.csv", encoding="utf-8", quoting=1).drop_duplicates()
print(3)
iraq1_merged = iraq1_topic.merge(iraq1_dialect, on="text")
print(4)
iraq1_merged = iraq1_merged.merge(iraq1_senti, on="text")
print("irag 1 merged Done")

iraq2_dialect = pd.read_csv(r"D:\project\NLG\fine-tunning\prepare_data/data/V2 ( 3M)/result_Dialect_iraq2.csv", encoding="utf-8", quoting=1).drop_duplicates()
iraq2_senti = pd.read_csv(r"D:\project\NLG\fine-tunning\prepare_data/data/V2 ( 3M)/result_sentiment_iraq2.csv", encoding="utf-8", quoting=1).drop_duplicates()
iraq2_topic = pd.read_csv(r"D:\project\NLG\fine-tunning\prepare_data/data/V2 ( 3M)/result_topic_iraq2.csv", encoding="utf-8", quoting=1).drop_duplicates()
iraq2_merged = iraq2_topic.merge(iraq2_senti, on="text").merge(iraq2_dialect, on="text")

print("irag 2 merged Done")

syria1_dialect = pd.read_csv(r"D:\project\NLG\fine-tunning\prepare_data/data/V2 ( 3M)/result_Dialect_syria1.csv", encoding="utf-8", quoting=1).drop_duplicates()
syria1_senti = pd.read_csv(r"D:\project\NLG\fine-tunning\prepare_data/data/V2 ( 3M)/result_sentiment_syria1.csv", encoding="utf-8", quoting=1).drop_duplicates()
syria1_topic = pd.read_csv(r"D:\project\NLG\fine-tunning\prepare_data/data/V2 ( 3M)/result_topic_syria1.csv", encoding="utf-8", quoting=1).drop_duplicates()
syria1_merged = syria1_topic.merge(syria1_senti, on="text").merge(syria1_dialect, on="text")

print("syria 1 merged Done")

syria2_dialect = pd.read_csv(r"D:\project\NLG\fine-tunning\prepare_data/data/V2 ( 3M)/result_Dialect_syria2.csv", encoding="utf-8", quoting=1).drop_duplicates()
syria2_senti = pd.read_csv(r"D:\project\NLG\fine-tunning\prepare_data/data/V2 ( 3M)/result_sentiment_syria2.csv", encoding="utf-8", quoting=1).drop_duplicates()
syria2_topic = pd.read_csv(r"D:\project\NLG\fine-tunning\prepare_data/data/V2 ( 3M)/result_topic_syria2.csv", encoding="utf-8", quoting=1).drop_duplicates()
syria2_merged = syria2_topic.merge(syria2_senti, on="text").merge(syria2_dialect, on="text")

print("syria 2 merged Done")

df = iraq1_merged.append([iraq2_merged, syria1_merged,syria2_merged]).reset_index(drop=True)

df.to_csv("full_3M.csv",encoding= "utf-8",index=False, quoting=1)
