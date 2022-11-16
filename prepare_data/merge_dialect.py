import pandas as pd

df_21_dialect = pd.read_csv(r"D:\project\NLG\fine-tunning\prepare_data/data/V2 ( 3M)/full_3M.csv", encoding="utf-8", quoting=1)

maghreb = ["Libya","Tunisia","Morocco","Algeria","Mauritania"]
levant = ["Syria","Jordan","Lebanon","Palestine"]
gulf = ["Iraq","Qatar","Oman","Saudi_Arabia","United_Arab_Emirates","Kuwait","Bahrain"]
aden = ["Yemen","Djibouti","Somalia"]
nile = ["Egypt","Sudan"]



c = 1
def merged_dialect(dialect):
    global c
    if dialect in maghreb:
        return "Maghreb"
    elif dialect in levant:
        return "Levant"
    elif dialect in gulf:
        return "Gulf"
    elif dialect in aden:
        return "Gulf of Aden"
    elif dialect in nile:
        return "Nile Basin"
    print(c)
    c += 1


df_21_dialect["dialect_1"] = df_21_dialect["dialect"].apply(lambda x: merged_dialect(x))
df_21_dialect = df_21_dialect.drop("dialect",axis=1)


df_21_dialect.to_csv(r"D:\project\NLG\fine-tunning\prepare_data/data/V2 ( 3M)/full_3M_dialect6.csv", encoding="utf-8", quoting=1,index=False)
