from langdetect import detect, DetectorFactory
import re
from elasticsearch import Elasticsearch
import sys

def cleaner(x):
    # x = re.sub(r'\n', ' ', x)  # remove ENTER
    x = re.sub(r'~', '', x)  # remove ~ as sep
    x = re.sub(r'"', '', x)  # remove "

    # x = re.sub(r"(?:\@|https?\://)\S+", "", x)  # remove mentions and links
    # x = re.sub(r'\s*[A-Za-z]+\b', '', x)  # remove english char
    # x = re.sub(r'(\W)(?=\1)', '', x)  # remove repeated punctuation
    x = x.strip()
    return x

sys.path.insert(1, './project_src')

es = Elasticsearch(['https://1400584:WelN&R+N7gH6l&ti@yekta.kavosh.org:9200'], verify_certs=False, timeout=40,
                   max_retries=10, retry_on_timeout=True)

def searching(user_query):
    res = es.search(index="sy-tw-posts*", body=user_query, scroll='2m', size=5000)
    # print(res)
    total = 13000000
    old_scroll_id = res['_scroll_id']

    user_id_checklist = []
    scroll_counter = 0
    hold_scrol = 0
    print("all post: ", total)
    file_name = "./data/syria_corpus2.csv"
    with open(file_name, "a", encoding="utf-8") as file_object:
        # file_object.write("clean_text\n")
        while scroll_counter < total:
            raw_data = res['hits']['hits']
            for doc in raw_data:
                # init variables

                text = doc["_source"]["text"]

                post_id = doc["_source"]["id_str"]

                if (len(text) >= 70):

                    try:
                        if detect(text) == "ar":
                            row = '"' + post_id + '"~"' + cleaner(text) + '"'
                            file_object.write(row)
                            file_object.write('\n')
                            scroll_counter += 1
                    except:
                        print(text)
            try:
                print(scroll_counter)
                res = es.scroll(scroll_id=old_scroll_id, scroll='2m')
                # row_count = sum(1 for row in file_object)
                # print("row file count", row_count)
                if hold_scrol == scroll_counter:
                    break
                hold_scrol = scroll_counter
            except Exception as scroll_err:
                print('Error: ')
                print(scroll_err)
                break


user_query = {
    "query": {
        "bool": {
            "filter": [
                {
                    "range": {
                        "created_at": {
                            "lt": "Sun Dec 01 00:00:00 +0000 2022"
                        }
                    }
                }
            ]
        }
    }
}

searching(user_query)
