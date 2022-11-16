import pandas as pd
# import pandas_ml as pdml


ub_df = pd.read_csv(r"D:\project\NLG\fine-tunning\prepare_data/data/V2 ( 3M)/final_tweet.csv", encoding="utf-8",
                    quoting=1)
# blance dialect

other_dialect = ["Gulf of Aden", "Levant", "Maghreb", "Nile Basin"]
df_otherDialect = ub_df[
    (ub_df['dialect'] == "Levant") | (ub_df['dialect'] == "Maghreb") | (ub_df['dialect'] == "Gulf of Aden") | (
                ub_df['dialect'] == "Nile Basin")]
df_Gulf_MSA = ub_df[(ub_df['dialect'] == "Gulf") | (ub_df['dialect'] == "Modern Standard Arabic")]


# # reduse gulf to MSA
# gulf_reducer = df_Gulf_MSA.imbalance.under_sampling.ClusterCentroids()
# df_Gulf_MSA_BL = df_Gulf_MSA.fit_sample(gulf_reducer)
#
# df_msaBL_with_other = df_Gulf_MSA_BL.append([df_otherDialect]).reset_index(drop=True)
# # then boost other to MSA
# booster_other = df_msaBL_with_other.imbalance.over_sampling.SMOTE()
# df_blanced = df_msaBL_with_other.fit_sample(booster_other)
#
df_otherDialect.to_csv(r"D:\project\NLG\fine-tunning\prepare_data/data/V2 ( 3M)/df_otherDialect.csv", encoding="utf-8",
                  quoting=1, index=False)
df_Gulf_MSA.to_csv(r"D:\project\NLG\fine-tunning\prepare_data/data/V2 ( 3M)/df_Gulf_MSA.csv", encoding="utf-8",
                  quoting=1, index=False)