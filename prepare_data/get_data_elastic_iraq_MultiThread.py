from langdetect import detect, DetectorFactory
import re
from elasticsearch import Elasticsearch
import sys
from queue import Queue
from threading import Thread
import datetime
import calendar

sys.path.insert(1, './project_src')

es = Elasticsearch(['https://1400584:WelN&R+N7gH6l&ti@yekta.kavosh.org:9200'], verify_certs=False, timeout=40,
                   max_retries=10, retry_on_timeout=True)
NUM_THREADS = 5
q = Queue()

def cleaner(x):
    # x = re.sub(r'\n', ' ', x)  # remove ENTER
    x = re.sub(r'~', '', x)  # remove ~ as sep
    x = re.sub(r'"', '', x)  # remove "

    # x = re.sub(r"(?:\@|https?\://)\S+", "", x)  # remove mentions and links
    # x = re.sub(r'\s*[A-Za-z]+\b', '', x)  # remove english char
    # x = re.sub(r'(\W)(?=\1)', '', x)  # remove repeated punctuation
    x = x.strip()
    return x

def searching():
    global q
    while True:
        user_query = q.get()
        res = es.search(index="iq-tw-posts*", body=user_query, scroll='2m', size=5000)
        print("lt: ", user_query["query"]["bool"]["filter"][0]["range"]["created_at"]["lt"])
        print("gt: ", user_query["query"]["bool"]["filter"][0]["range"]["created_at"]["gt"])

        # print(res)
        total = 13000000
        old_scroll_id = res['_scroll_id']

        user_id_checklist = []
        scroll_counter = 0
        hold_scrol = 0
        print("all post: ", total)
        file_name = "./data/iraq_corpus_MT.csv"
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
                            print("not Arabic")
                try:

                    print(scroll_counter, " of ", user_query["query"]["bool"]["filter"][0]["range"]["created_at"]["lt"] )
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
        q.task_done()


end = "Sun Dec 01 00:00:00 +0000 2020"
begin = "Sun Dec 01 00:00:00 +0000 2010"
time_format = "%a %b %d %H:%M:%S +0000 %Y"

dt_start = datetime.datetime.strptime(begin, time_format)
dt_end = datetime.datetime.strptime(end, time_format)
one_day = datetime.timedelta(1)
start_dates = [dt_start]
end_dates = []
today = dt_start
while today <= dt_end:
    #print(today)
    tomorrow = today + one_day
    if tomorrow.month != today.month:
        start_dates.append(tomorrow)
        end_dates.append(today)
    today = tomorrow

end_dates.append(dt_end)
date_list = []
for t in end_dates:
    time = str(calendar.day_name[t.weekday()][:3]) + " " + str(t.strftime("%B")[:3]) + " " + str(t.strftime('%d')) + " 00:00:00 +0000 " + str(t.year)
    date_list.append(time)



for h in range(len(date_list)-1,0,-1):
    user_query = {
        "query": {
            "bool": {
                "filter": [
                    {
                        "range": {
                            "created_at": {
                                "lt": date_list[h],
                                "gt": date_list[h-1]
                            }
                        }
                    }
                ]
            }
        }
    }

    q.put(user_query)

for t in range(NUM_THREADS):

    worker = Thread(target=searching)
    worker.daemon = True
    worker.start()

q.join()
