from langdetect import detect, DetectorFactory
import re
from elasticsearch import Elasticsearch
import sys
from normalizer.TextNormalizer import Normalizer

norm_ar = Normalizer(language='ar', remove_extra_spaces=True,
                     rtl_style=True,
                     rtl_numbers_refinement=True,
                     remove_diacritics=False,
                     affix_spacing=True,
                     remove_repeated_chars=False,
                     punctuation_spacing=True,
                     hashtags_refinement=True,
                     entity_cleaning=False,
                     remove_punctuation=False,
                     remove_email=True,
                     remove_url=True,
                     remove_mobile_number=False,
                     remove_home_number=False,
                     remove_emoji=False,
                     remove_mention=True,
                     remove_html=True,
                     remove_numbers=True,
                     remove_english=True,
                     remove_newline=True)


def cleaner(x):
    x = re.sub(r'[^\w\s]', '', x)
    x = re.sub(r'\n', '', x)
    x = x.strip()
    return x


sys.path.insert(1, './project_src')

es = Elasticsearch(['https://1400584:WelN&R+N7gH6l&ti@yekta.kavosh.org:9200'], verify_certs=False, timeout=40,
                   max_retries=10, retry_on_timeout=True)

def searching(user_query):
    res = es.search(index="sy-tw-posts*", body=user_query, scroll='2m', size=5000)
    # print(res)
    total = 1300000
    old_scroll_id = res['_scroll_id']

    user_id_checklist = []
    scroll_counter = 0
    hold_scrol = 0
    print("all post: ", total)
    file_name = "./data/syria_corpus.csv"
    with open(file_name, "a", encoding="utf-8") as file_object:
        # file_object.write("clean_text\n")
        while scroll_counter < total:
            raw_data = res['hits']['hits']
            for doc in raw_data:
                # init variables

                text = doc["_source"]["text"]

                clean_text = cleaner(norm_ar.normalize(text))

                if (len(clean_text) >= 70):

                    try:
                        if detect(clean_text) == "ar":
                            file_object.write(clean_text)
                            file_object.write('\n')
                            scroll_counter += 1
                    except:
                        print(clean_text)
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
                            "lt": "Sun Nov 05 00:00:00 +0000 2022"
                        }
                    }
                }
            ]
        }
    },
    "sort": {
        "_script": {
            "script": "Math.random()",
            "type": "number",
            "order": "asc"
        }
    }
}

searching(user_query)
