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


def convert_dict(indict):
    outlist = {}
    for post_id_l, post_data in indict.items():
        num_c = post_data['comments']['summary']['total_count']
        num_r = post_data['reactions']['summary']['total_count']
        outlist[post_id_l] = {'num_comments': num_c, 'num_reactions': num_r}
    return outlist


def list_to_facebook_data(list_post_ids):
    c2rmv = str.maketrans("", "", "'[] ")
    fixed_post_ids = str(list_post_ids).translate(c2rmv)
    batch_url = f"https://graph.facebook.com/v2.11/?ids={fixed_post_ids}" + \
                '&fields=comments.summary(1)%7Bid%7D%2Creactions.summary(1)%7Bid%7D&' + \
                f'access_token={access_token}'
    return requests.get(batch_url)


for file in os.listdir(os.path.join(output_dir, 'posts')):
    if not file.endswith(".json"):
        continue

    file_date = datetime.date(*[int(x) for x in file.replace('.json', '').split('_')])
    if file_date < datetime.date(2016, 12, 31):
        continue

    file_path = os.path.join(output_dir, 'posts', file)

    day_dict = {}
    with open(file_path, encoding='utf-8') as json_data:
        d = json.load(json_data)
        start = time.time()
        for post_group in d:
            post_ids_by_group = []
            for post_index, post in enumerate(post_group):
                post_id = post['id']
                post_ids_by_group.append(post_id)

            for id_chunk in chunked(post_ids_by_group, 50):
                post_jsons = list_to_facebook_data(id_chunk)
                post_json_dict = post_jsons.json()
                day_dict.update(convert_dict(post_json_dict))

    with open(os.path.join(output_dir, 'summary', 'summary_' + file), "w", encoding='utf-8') as myfile:
        myfile.write(json.dumps(day_dict))
    print(f'{file}: {time.time() - start}')
