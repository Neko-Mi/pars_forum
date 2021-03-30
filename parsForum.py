import requests
import pandas as pd
from threading import Thread
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
    msg = list()
    for o in ops:
        msg.append(o['insert'])
    return msg


def pars(messages, dis_id, page, user):
    url = 'https://mangalib.me/api/forum/posts?page=' + str(page) + \
          '&discussion_id=' + str(dis_id)

    try:
        data = requests.get(url).json()['data']
        if data:
            for d in data:
                if d['user_id'] == user:
                    message = {"updated_at": d["updated_at"],
                               "message":
                                   all_message(d["body"]["ops"]),
                               "reply_user_id":
                                   d["reply_user_id"],
                               "discussion_id":
                                   d["chatter_discussion_id"]}
                    print(message)
                    messages = messages.append(message, ignore_index=True)
            page += 1
        else:
            dis_id += 1
            page = 1

    except:
        dis_id += 1
        page = 1

    return messages, dis_id, page


def large_pars(length, user, messages, dis_id):
    page1 = 1
    while page1 <= 51:
        with concurrent.futures.ThreadPoolExecutor(
                max_workers=100) as e:
            future_list = []

            start = page1
            for i in range(100):
                print(start)
                future = e.submit(pars, messages=messages, dis_id=dis_id,
                                   page=start, user=user)
                future_list.append(future)
                start += length


            for f in future_list:
                msgs, dis_id, page = f.result()
                messages = messages.append(msgs, ignore_index=True)

        print('page: ', page1)
        page1 += 1

    return messages


def parsForum(dis_id, max_id, user):
    page = 1
    messages = pd.DataFrame(columns=["updated_at",
                                     "message",
                                     "reply_user_id",
                                     "discussion_id"])

    while dis_id < max_id:

        print(dis_id)

        if dis_id == 23396 or dis_id == 4706:
            if dis_id == 23396:
                message = large_pars(51, user, messages, 23396)
                messages.append(message, ignore_index=True)
                dis_id += 1
                page = 1
            else:
                message = large_pars(23, user, messages, 4706)
                messages.append(message, ignore_index=True)
                dis_id += 1
                page = 1
        else:
            messages, dis_id, page = pars(messages, dis_id, page, user)
            # messages.append(message, ignore_index=True)

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
    user = 224741
    min_id = 62000
    max_id = 62020
    threads = 10
    start_time = datetime.now()
    multi(min_id, max_id, threads, user)
    print(datetime.now() - start_time)

