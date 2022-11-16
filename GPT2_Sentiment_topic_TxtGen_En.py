import datasets
import datetime
import pickle
import tensorflow as tf
import pandas as pd
from transformers import AutoTokenizer, TFGPT2LMHeadModel, pipeline
from ProjectDirectories import *


class GPT2_Sentiment():

    def __init__(self, max_tok=128,
                 pos_tok="<|positive|>", neg_tok="<|negative|>", neu_tok="<|neutral|>",  # Sentiment
                 end_tok="<|endoftext|>", pad_tok="<|pad|>",
                 culture_tok="<|Culture|>", finance_tok="<|Finance|>", medical_tok="<|Medical|>",  # Topic
                 politics_tok="<|Politics|>", tech_tok="<|Tech|>", religion_tok="<|Religion|>",  # Topic
                 maghreb_tok="<|Maghreb|>", levant_tok="<|Levant|>", gulf_tok="<|Gulf|>",  # dialect
                 aden_tok="<|Gulf of Aden|>", nile_tok="<|Nile Basin|>", msa_tok="<|Modern Standard Arabic|>"
                 ):

        self.__MAX_TOKENS = max_tok
        self.__POS_TOKEN = pos_tok
        self.__NEG_TOKEN = neg_tok
        self.__NEU_TOKEN = neu_tok
        self.__EOS_TOKEN = end_tok
        self.__PAD_TOKEN = pad_tok
        self.__CULTURE_TOKEN = culture_tok
        self.__FINANCE_TOKEN = finance_tok
        self.__MEDICAL_TOKEN = medical_tok
        self.__POLITICS_TOKEN = politics_tok
        self.__TECH_TOKEN = tech_tok
        self.__RELIGION_TOKEN = religion_tok
        self.__MAGHREB_TOKEN = maghreb_tok
        self.__LEVANT_TOKEN = levant_tok
        self.__GULF_TOKEN = gulf_tok
        self.__ADEN_TOKEN = aden_tok
        self.__NILE_TOKEN = nile_tok
        self.__MSA_TOKEN = msa_tok

        self.__BOS_TOKENS = [self.__POS_TOKEN, self.__NEG_TOKEN, self.__NEU_TOKEN, self.__CULTURE_TOKEN,
                             self.__FINANCE_TOKEN, self.__MEDICAL_TOKEN, self.__POLITICS_TOKEN, self.__TECH_TOKEN,
                             self.__RELIGION_TOKEN, self.__MAGHREB_TOKEN, self.__LEVANT_TOKEN, self.__GULF_TOKEN,
                             self.__ADEN_TOKEN, self.__NILE_TOKEN, self.__MSA_TOKEN]
        try:
            self.tpu = tf.distribute.cluster_resolver.TPUClusterResolver()  # TPU detection
            print("Running on TPU ", self.tpu.cluster_spec().as_dict()["worker"])
        except ValueError:
            self.tpu = None
        if self.tpu:
            tf.config.experimental_connect_to_cluster(self.tpu)
            tf.tpu.experimental.initialize_tpu_system(self.tpu)
            self.__strategy = tf.distribute.TPUStrategy(self.tpu)
        else:
            self.__strategy = tf.distribute.get_strategy()
        print("REPLICAS: ", self.__strategy.num_replicas_in_sync)
        self.__Tokenizer = self.__load_tokenizer()
        self.__BATCH_SIZE_PER_REPLICA = 8
        self.__EPOCHS = 2
        try:
            self.__BATCH_SIZE = self.__BATCH_SIZE_PER_REPLICA * self.__strategy.num_replicas_in_sync
        except NameError as e:
            self.__BATCH_SIZE = self.__BATCH_SIZE_PER_REPLICA

    def __load_tokenizer(self):
        tokenizer = AutoTokenizer.from_pretrained(
            Pretrained_Model_Path,
            eos_token=self.__EOS_TOKEN,
            pad_token=self.__PAD_TOKEN,
            max_length=self.__MAX_TOKENS,
            is_split_into_words=True,
            local_files_only=True,
        )
        tokenizer.add_tokens(self.__BOS_TOKENS, special_tokens=True)
        return tokenizer

    def read_pureDataset(self):
        data = pd.read_csv(Raw_Data_Path)
        data = datasets.Dataset.from_pandas(data)
        data = data.map(self.TextTokenizer, batched=True, num_proc=self.__strategy.num_replicas_in_sync,
                        remove_columns=["text"], load_from_cache_file=True, )
        data.save_to_disk(Tokenized_Data_Path)
        return data

    def load_tokenizedData(self):
        data = datasets.load_from_disk(Tokenized_Data_Path)
        data.set_format(type="python", columns=["input_ids", "attention_mask", "labels"])
        data = data.train_test_split(
            test_size=0.20, shuffle=True, seed=1, load_from_cache_file=True
        )
        return data

    def TextTokenizer(self, examples):
        # Add start and end token to each comment
        examples = [ex + self.__EOS_TOKEN for ex in examples["text"]]
        # tokenizer created input_ids and attention_mask as output
        output = self.__Tokenizer(examples, add_special_tokens=True, max_length=self.__MAX_TOKENS, truncation=True,
                                  pad_to_max_length=True, )
        # shift labels for next token prediction
        # set padding token labels to -100 which is ignored in loss computation
        output["labels"] = [x[1:] for x in output["input_ids"]]
        output["labels"] = [[-100 if x == self.__Tokenizer.pad_token_id else x for x in y] for y in output["labels"]]
        # truncate input ids and attention mask to account for label shift
        output["input_ids"] = [x[:-1] for x in output["input_ids"]]
        output["attention_mask"] = [x[:-1] for x in output["attention_mask"]]
        return output

    def prepare_dataTensors(self, data_tokenized, type='train'):
        tensor_inputs = tf.convert_to_tensor(data_tokenized[type]["input_ids"])
        with open(os.path.join(Data_Path, '%s_tensor_inputs.pkl' % type), 'wb') as f:
            pickle.dump(tensor_inputs, f)
        tensor_labels = tf.convert_to_tensor(data_tokenized[type]["labels"])
        with open(os.path.join(Data_Path, '%s_tensor_labels.pkl' % type), 'wb') as f:
            pickle.dump(tensor_labels, f)
        tensor_mask = tf.convert_to_tensor(data_tokenized[type]["attention_mask"])
        with open(os.path.join(Data_Path, '%s_tensor_mask.pkl' % type), 'wb') as f:
            pickle.dump(tensor_mask, f)

    def load_dataTensor(self, type='train'):
        with open(os.path.join(Data_Path, '%s_tensor_inputs.pkl' % type), 'rb') as f:
            tensor_inputs = pickle.load(f)
        with open(os.path.join(Data_Path, '%s_tensor_labels.pkl' % type), 'rb') as f:
            tensor_labels = pickle.load(f)
        with open(os.path.join(Data_Path, '%s_tensor_mask.pkl' % type), 'rb') as f:
            tensor_mask = pickle.load(f)
        dataset = tf.data.Dataset.from_tensor_slices(
            ({"input_ids": tensor_inputs, "attention_mask": tensor_mask}, tensor_labels,))
        return dataset

    def recreate_trainTest(self, train, test):
        self.__BUFFER_SIZE = len(train)
        train_ds = (train.shuffle(self.__BUFFER_SIZE).batch(self.__BATCH_SIZE, drop_remainder=True))
        test_ds = test.batch(self.__BATCH_SIZE, drop_remainder=True)
        return train_ds, test_ds

    def model_finetuneInitialization(self, learn_rate=0.001):
        self.__INITAL_LEARNING_RATE = learn_rate
        lr_schedule = tf.keras.optimizers.schedules.ExponentialDecay(
            self.__INITAL_LEARNING_RATE,
            decay_steps=300,
            decay_rate=0.7,
            staircase=True)
        with self.__strategy.scope():
            model = TFGPT2LMHeadModel.from_pretrained(
                Pretrained_Model_Path,
                use_cache=False,
                pad_token_id=self.__Tokenizer.pad_token_id,
                eos_token_id=self.__Tokenizer.eos_token_id,
            )
            model.resize_token_embeddings(len(self.__Tokenizer))
            optimizer = tf.keras.optimizers.Adam(learning_rate=lr_schedule)
            model.compile(optimizer=optimizer, loss=model.hf_compute_loss)
            model.summary()
        return model

    def finetune_dataset(self, model_init, train_ds, test_ds):
        callbacks = [
            tf.keras.callbacks.EarlyStopping(
                monitor="val_loss", verbose=1, patience=1, restore_best_weights=True
            ),
            tf.keras.callbacks.ModelCheckpoint(
                "modules/models/GPT2_Finetune_Models/_GPT2-Model_{epoch:02d}_{val_loss:.3f}.tf",
                monitor="val_loss",
                save_best_only=True,
                verbose=1,
                save_format="tf",
            ),
        ]
        steps_per_epoch = int(self.__BUFFER_SIZE // self.__BATCH_SIZE)
        print(f"Model Params:\nbatch_size: {self.__BATCH_SIZE}\nEpochs: {self.__EPOCHS}\n"
              f"Step p. Epoch: {steps_per_epoch}\n"
              f"Initial Learning rate: {self.__INITAL_LEARNING_RATE}")
        hist = model_init.fit(train_ds, validation_data=test_ds, batch_size=self.__BATCH_SIZE,
                              epochs=self.__EPOCHS, callbacks=callbacks, verbose=1, )
        return hist

    def run_trainSteps(self, is_first_run=False):
        if is_first_run:
            gpt2.read_pureDataset()
        data = gpt2.load_tokenizedData()
        if is_first_run:
            gpt2.prepare_dataTensors(data, type='train')
        train = gpt2.load_dataTensor(type='train')
        if is_first_run:
            gpt2.prepare_dataTensors(data, type='test')
        test = gpt2.load_dataTensor(type='test')
        train_ds, test_ds = gpt2.recreate_trainTest(train, test)
        model_init = gpt2.model_finetuneInitialization()
        finetune_model = gpt2.finetune_dataset(model_init, train_ds, test_ds)
        return finetune_model

    def load_finetuneModel(self):
        model = TFGPT2LMHeadModel.from_pretrained(
            Pretrained_Model_Path,
            use_cache=False,
            pad_token_id=self.__Tokenizer.pad_token_id,
            eos_token_id=self.__Tokenizer.eos_token_id,
        )

        model.resize_token_embeddings(len(self.__Tokenizer))
        optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)
        model.compile(optimizer=optimizer, loss=model.compute_loss)
        model.summary()

        model.load_weights(filepath=FineTune_Model_Path_02)
        review = pipeline(
            "text-generation",
            model=model,
            tokenizer=self.__Tokenizer,
        )
        return review

    def __tagged_Text(self, model, **kwargs):
        if kwargs['dialect'].title() == "Gulf Of Aden":
            sent = "<|" + "Gulf of Aden" + "|>" + "<|" + kwargs['topic'].title() + "|>" + "<|" + kwargs[
                'sentiment'] + "|>" + ' ' + kwargs['text']
        else:
            sent = "<|" + kwargs['dialect'].title() + "|>" + "<|" + kwargs['topic'].title() + "|>" + "<|" + kwargs[
                'sentiment'] + "|>" + ' ' + kwargs['text']
        st = datetime.datetime.now()
        gen_txt = model(sent, max_length=150, num_return_sequences=kwargs['texts_num'])
        end = datetime.datetime.now()
        print(end - st)
        return gen_txt

    def generate_newTexts(self, model, texts=[], sent_label='positive', topic_label='political',
                          dialect_label='Modern Standard Arabic',
                          texts_num=10):
        result = []
        for txt in texts:
            gen_txt = self.__tagged_Text(model, text=txt, sentiment=sent_label, topic=topic_label,
                                         dialect=dialect_label,
                                         texts_num=texts_num)
            print('Begin Text: ', txt)
            tmp_list = []
            for t in gen_txt:
                text = t['generated_text'].split(">")[-1].strip()
                tmp_list.append(text)
                print(text)
            print('---------------------------------------------------------------------------------------------\n')
            result.append({'begin_text': txt, 'generated_text': tmp_list})
        return result


import cProfile, sys

# from mpi4py.MPI import COMM_WORLD

if __name__ == '__main__':
    pr = cProfile.Profile()
    pr.enable()

    gpt2 = GPT2_Sentiment()
    model = gpt2.run_trainSteps(is_first_run=True)
    # model = gpt2.load_finetuneModel()
    begin_texts = ['روسيا']
    # begin_texts = ['today', 'Zahra and her husband', 'Iran', 'Trump', 'Joe Biden tells']
    gpt2.generate_newTexts(model, texts=begin_texts, sent_label='positive', topic_label='politics',
                           dialect_label='gulf of aden', texts_num=1)

    pr.disable()

    pr.dump_stats('profiling.prof')
