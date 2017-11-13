# -*- coding: utf-8 -*-
import logging
import time
from facepy import GraphAPI
import requests
import datetime
import json
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

project_dir = os.path.join(os.getcwd(), os.pardir)


def get_group_info(d_start, d_end, token, query, output_dir):
    graph = GraphAPI(token)

    # Create a pair of since and until days for the user defined range
    days = [(d_end - datetime.timedelta(days=delta)) for delta in
            range((d_end - d_start + datetime.timedelta(days=1)).days)]
    day_pairs = zip(days[:-1], days[1:])

    def gen_fn(date_in: datetime.date):
        """
        Converts datetime object to filename in the format: '{date_in}.json'
        :param date_in: Datetime.date object
        :return:
        """
        date_str = str(date_in).replace('-', '_')
        return os.path.join(project_dir, 'data', date_str+'.json')

    # Calculate some metrics to make sure its working
    beg_time = time.time()
    total_posts = 0

    for pair in day_pairs:
        num_posts = 0
        day_time = time.time()
        posts = graph.get(query, paging=True, until=str(pair[0]), since=str(pair[1]))
        file_name = gen_fn((pair[1]))
        day_list = []
        with open(file_name, 'w', encoding='utf8') as f:
            # Get all posts and calculate metrics
            while 'paging' in posts:
                start_time = time.time()
                num_posts += len(posts['data'])
                total_posts += len(posts['data'])

                day_list.append(posts['data'])
                posts = requests.get(posts['paging']['next']).json()

                end_time = time.time()
                round_time = end_time - start_time
                logger.info(f'{str(pair[1])}: Crawled through {num_posts} posts in {round_time} seconds')
            # Write out to file
            post_json_str = json.dumps(day_list, ensure_ascii=False)
            f.write(post_json_str)

        logger.info(f'{str(pair[1])}: Crawled through a total of {num_posts} posts in {time.time()-day_time} seconds. '
                    f'Total time: {time.time()-beg_time}\tTotal posts: {total_posts}')


if __name__ == '__main__':
    with open(os.path.join(project_dir, 'authentication.json')) as f:
        auth = json.load(f)

    # get dates
    # d_end = datetime.date(2017, 11, 12)
    # d_start = datetime.date(2017, 11, 11)
    d_end = datetime.date(2015, 5, 5)
    d_start = datetime.date(2015, 5, 4)

    token = auth['token']
    query = auth['query']
    output_dir = auth['output_dir']

    get_group_info(d_start, d_end, token, query, output_dir)