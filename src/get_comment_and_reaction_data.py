import datetime
import json
import os
import time

import requests

from user_data import user_data

project_dir = os.path.join(os.getcwd(), os.pardir)
output_dir = os.path.join(project_dir, 'output')
access_token = user_data['token']


def convert_list(l):
    ftype = ['comment', 'like', 'love', 'haha', 'sad', 'wow', 'angry']
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
    # comment_url = f"https://graph.facebook.com/v2.11/{pid}/comments?summary=total_count&limit=0&access_token={access_token}"
    batch_comment_url = f"https://graph.facebook.com/v2.11/comments?ids={list_post_ids}&summary=total_count&filter=stream&limit=0&access_token={access_token}"
    batch_like_url = f"https://graph.facebook.com/v2.11/?ids={list_post_ids}&fields=reactions.type(LIKE).summary(total_count).limit(0)&access_token={access_token}"
    batch_love_url = f"https://graph.facebook.com/v2.11/?ids={list_post_ids}&fields=reactions.type(LOVE).summary(total_count).limit(0)&access_token={access_token}"
    batch_haha_url = f"https://graph.facebook.com/v2.11/?ids={list_post_ids}&fields=reactions.type(HAHA).summary(total_count).limit(0)&access_token={access_token}"
    batch_sad_url = f"https://graph.facebook.com/v2.11/?ids={list_post_ids}&fields=reactions.type(SAD).summary(total_count).limit(0)&access_token={access_token}"
    batch_wow_url = f"https://graph.facebook.com/v2.11/?ids={list_post_ids}&fields=reactions.type(WOW).summary(total_count).limit(0)&access_token={access_token}"
    batch_angry_url = f"https://graph.facebook.com/v2.11/?ids={list_post_ids}&fields=reactions.type(ANGRY).summary(total_count).limit(0)&access_token={access_token}"
    req_list = [requests.get(url) for url in (
    batch_comment_url, batch_like_url, batch_love_url, batch_haha_url, batch_sad_url, batch_wow_url, batch_angry_url)]
    return req_list


for file in os.listdir(os.path.join(output_dir, 'posts')):
    if not file.endswith(".json"):
        continue

    file_date = datetime.date(*[int(x) for x in file.replace('.json', '').split('_')])
    if file_date < datetime.date(2015, 8, 7):
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
                if post_index % 25 == 24:
                    post_jsons = list_to_facebook_data(post_ids_by_group)
                    day_list.append(json.dumps([json.loads(r.text) for r in post_jsons]))
                    post_ids_by_group = []

            post_jsons = list_to_facebook_data(post_ids_by_group)
            day_list.append(json.dumps([json.loads(r.text) for r in post_jsons]))

    with open(os.path.join(output_dir, 'comments', 'com_' + file), "w", encoding='utf-8') as myfile:
        myfile.write(json.dumps(day_list))
    print(f'{file}: {time.time() - start}')

    # 1728661083894539/?fields=comments.summary(total_count).limit(0),reactions.type(LIKE).limit(0).summary(1),reactions.type(LOVE).limit(0).summary(1)
