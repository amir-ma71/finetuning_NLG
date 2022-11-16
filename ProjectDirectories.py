
from pathlib import Path
import os

Root_Path = Path(__file__).resolve().parent
Data_Path = os.path.join(Root_Path, 'modules/data')
Models_Path = os.path.join(Root_Path, 'modules/models')

Pretrained_Model_Path = os.path.join(Models_Path, 'aragpt2-base')
FineTune_Model_Path_02 = os.path.join(Models_Path, 'GPT2_Finetune_Models/_GPT2-Model_train.tf')
#FineTune_Model_Path_01 = os.path.join(Models_Path, 'GPT2_Finetune_Models/_GPT2-Model_01_4.253.tf')

Raw_Data_Path = os.path.join(Data_Path, 'gpt_dataset_sample10.csv')
Tokenized_Data_Path = os.path.join(Data_Path, 'reviews_tokenized_128_ratings')

