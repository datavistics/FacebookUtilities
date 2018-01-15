# -*- coding: utf-8 -*-
import datetime
import json
import logging
import os
import time

import requests
from facepy import GraphAPI
from gooey import Gooey, GooeyParser

logging.basicConfig(filename='download_query.log', level=logging.INFO)
logger = logging.getLogger(__name__)

project_dir = os.path.join(os.getcwd(), os.pardir)


def get_group_info(d_start, d_end, token, query, output_dir):
    """
    Will execute a query for the duration given and save the results to json in the directory given.
    :param d_start:
    :param d_end:
    :param token:
    :param query:
    :param output_dir:
    :return:
    """
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
        return os.path.join(output_dir, date_str + '.json')

    # Calculate some metrics to make sure its working
    beg_time = time.time()
    total_posts = 0

    # Clean up query

    for pair in day_pairs:
        num_posts = 0
        day_time = time.time()
        posts = graph.get(query, paging=True, until=str(pair[0]), since=str(pair[1]))
        file_name = gen_fn((pair[1]))
        day_list = []
        if len(posts['data']) == 0:
            continue
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
                logger.info(f'\tCrawled through {num_posts} posts in {round_time} seconds')
            # Write out to file
            post_json_str = json.dumps(day_list, ensure_ascii=False)
            f.write(post_json_str)

        logger.info(f'{str(pair[1])}: Crawled through a total of {num_posts} posts in {time.time()-day_time} seconds.\n'
                    f'Total time: {time.time()-beg_time}\tTotal posts: {total_posts}')


@Gooey(program_name='Facebook Query to json',
       image_dir=os.path.dirname(os.path.realpath(__file__)),
       required_cols=1,
       optional_cols=1)
def parse_args():
    stored_args = {}

    # Get filename info
    script_name = os.path.splitext(os.path.basename(__file__))[0]
    args_file = "{}-args.json".format(script_name)

    # Uses previous args as defaults
    if os.path.isfile(args_file):
        with open(args_file) as data_file:
            stored_args = json.load(data_file)

    parser = GooeyParser(
        description='This program will store facebook data in json format in the output directory.\nThe data will '
                    'automatically be paged (beyond the 25 post limit), and downloaded/sorted by date.\n'
                    'Posts have been tested, but feel free to try any data')
    parser.add_argument('-s', '--d_start', action='store',
                        widget='DateChooser', default=stored_args.get('d_start'), help='YYYY-MM-DD')
    parser.add_argument('-e', '--d_end', action='store',
                        widget='DateChooser',
                        default=stored_args.get('d_end'),
                        help='YYYY-MM-DD')
    parser.add_argument('-o', '--output_dir', action='store',
                        widget='DirChooser',
                        default=stored_args.get('output_dir'),
                        help='Leave blank for default')
    parser.add_argument('-q', '--query', action='store', default=stored_args.get('query'),
                        help="Full query for facebook, eg:\n'me?fields=id,name,picture'")
    args = parser.parse_args()
    with open(args_file, 'w') as data_file:
        # Using vars(args) returns the data as a dictionary
        json.dump(vars(args), data_file)
    return args


if __name__ == '__main__':
    args = parse_args()
    d_start = datetime.datetime.strptime(args.d_start, '%Y-%m-%d').date()
    d_end = datetime.datetime.strptime(args.d_end, '%Y-%m-%d').date()
    query = args.query
    output_dir = args.output_dir

    with open('user_data.json') as json_file:
        token_dict = json.load(json_file)

    token = token_dict['token']
    get_group_info(d_start, d_end, token, query, output_dir)
