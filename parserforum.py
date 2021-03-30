import requests
import pandas as pd
import concurrent.futures
from datetime import datetime


def infile(arr, user):
    messages = pd.DataFrame(columns=["updated_at",
                                     "message",
                                     "reply_user_id",
                                     "discussion_id"])

    for a in arr:
        messages = messages.append(a, ignore_index=True)

    messages = messages.sort_values("updated_at", kind='mergesort')
    filename = str(user) + '.xlsx'
    messages.to_excel(filename)


def all_message(ops):
    msg = [""] * len(ops)
    i = 0
    for o in ops:
        msg[i] = o['insert']
        i += 1
    return msg


def parsForum(dis_id, max_id, user):
    page = 1
    messages = pd.DataFrame(columns=["updated_at",
                                     "message",
                                     "reply_user_id",
                                     "discussion_id"])

    while dis_id < max_id:
        url = 'https://mangalib.me/api/forum/posts?page=' + str(page) + \
              '&discussion_id=' + str(dis_id)

        print(dis_id)

        try:
            data = requests.get(url).json()['data']
            if data:
                for d in data:
                    if d['user_id'] == user:
                        message = {
                            "updated_at": d["updated_at"],
                                    "message":
                                        all_message(d["body"]["ops"]),
                                    "reply_user_id":
                                        d["reply_user_id"],
                            "discussion_id":
                                d["chatter_discussion_id"]
                                    }
                        messages = messages.append(message, ignore_index=True)
                page += 1
            else:
                dis_id += 1
                page = 1

        except:
            dis_id += 1
            page = 1

    return messages


def multi(min_id, max_id, threads_num, user):
    length = max_id - min_id
    length = round(length / threads_num)

    start = min_id
    arr_msg = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads_num) as e:
        future_list = []
        for i in range(threads_num):
            end = start + length
            future = e.submit(parsForum, dis_id=start, max_id=end, user=user)
            future_list.append(future)
            print('created thread :', i)
            start += length

        for f in future_list:
            arr_msg.append(f.result())

    infile(arr_msg, user)


if __name__ == '__main__':
    user = 476662
    min_id = 1
    max_id = 66533
    threads = 10
    start_time = datetime.now()
    multi(min_id, max_id, threads, user)
    print(datetime.now() - start_time)