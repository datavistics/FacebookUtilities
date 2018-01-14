import datetime
import json
import os
import time

import requests
from more_itertools import chunked

from user_data import user_data

project_dir = os.path.join(os.getcwd(), os.pardir)
output_dir = os.path.join(project_dir, 'output')
access_token = user_data['token']
ftype = ['comment', 'reaction']


def convert_list(l):
    out = {}
    for ckey in l[0]:
        out[ckey] = {ftype[0]: l[0][ckey]['summary']['total_count']}
        break
    for ind, d in enumerate(l[1:]):
        if not d:
            continue
        for k in d:
            out[k][ftype[ind]] = d[k]['reactions']['summary']['total_count']
    return d


def list_to_facebook_data(list_post_ids):
    c2rmv = str.maketrans("", "", "'[] ")
    fixed_post_ids = str(list_post_ids).translate(c2rmv)
    batch_url = f"https://graph.facebook.com/v2.11/comments?ids={fixed_post_ids}" + \
                '&fields=comments.summary(1)%7Bid%7D%2Creactions.summary(1)%7Bid%7D&' + \
                f'access_token={access_token}'
    print(batch_url)
    return requests.get(batch_url)


for file in os.listdir(os.path.join(output_dir, 'posts')):
    if not file.endswith(".json"):
        continue

    file_date = datetime.date(*[int(x) for x in file.replace('.json', '').split('_')])
    if file_date < datetime.date(2017, 10, 1):
        continue

    file_path = os.path.join(output_dir, 'posts', file)

    day_list = []
    with open(file_path, encoding='utf-8') as json_data:
        d = json.load(json_data)
        start = time.time()
        for post_group in d:
            post_ids_by_group = []
            for post_index, post in enumerate(post_group):
                post_id = post['id']
                post_ids_by_group.append(post_id)

            for id_chunk in chunked(post_ids_by_group, 25):
                post_jsons = list_to_facebook_data(id_chunk)
                # day_list.append([{ft: json.loads(r.text)} for ft, r in zip(ftype, post_jsons)])

    with open(os.path.join(output_dir, 'comments', 'com_' + file), "w", encoding='utf-8') as myfile:
        myfile.write(json.dumps(day_list))
    print(f'{file}: {time.time() - start}')

    # 1728661083894539/?fields=comments.summary(total_count).limit(0),reactions.type(LIKE).limit(0).summary(1),reactions.type(LOVE).limit(0).summary(1)
