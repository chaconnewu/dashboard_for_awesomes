import json
import gzip
import os.path
from collections import defaultdict
from pprint import pprint
from urllib.parse import urlparse

import pymysql
import yaml

with open('config.yml', 'r') as config_file:
    config = yaml.load(config_file)

conn = pymysql.connect(host='127.0.0.1', charset='utf8', use_unicode=True, unix_socket='/tmp/mysql.sock', user=config['database']['user'], passwd=config['database']['password'], db=config['database']['db'], autocommit=True)
cur = conn.cursor()

f = open('awesome_go_github_repos.txt', 'r').read()

url_list = f.split('\n')[:-1] # get rid of the last empty one
url_set = set([urlparse(x.lower()).path for x in url_list])

def insert_into(event, table):
    actor_login = event['actor']['login']
    actor_url = event['actor']['url']
    created_at = event['created_at']
    repo_name = event['repo']['name']
    repo_url = event['repo']['url']
    type = event['type']
    values = "('%s', '%s', '%s', '%s', '%s', '%s');" % (actor_login, actor_url, created_at, repo_name, repo_url, type)
    sql_query = "insert into " + table + " values " + values
    cur.execute(sql_query)

file_base_url = '../data/2016-'
file_postfix = '.json.gz'

event_set = set();
count = 0
for month in range(4, 5):
    month_str = str(month)
    if month < 10:
        month_str = '0' + month_str
    month_str += '-'

    for day in range(1, 14):
        day_str = str(day)
        if day < 10:
            day_str = '0' + day_str
        day_str += '-'

        for n in range(24):
            file_url = file_base_url + month_str + day_str + str(n) + file_postfix
            print(file_url)
            # Check if data file exists
            if not os.path.isfile(file_url):
                continue

            event_dict = defaultdict(int)
            with gzip.GzipFile(file_url, 'r') as f:
                for line in f:
                    try:
                        event = json.loads(line.decode())
                    except:
                        print(event)
                        continue
                    # url = urlparse(event['repo']['url']).path
                    repo_url = urlparse(event['repo']['url']).path[6:].lower()
                    if repo_url.lower() in url_set:
                        insert_into(event, 'awesome_go_activities')
                        count += 1
                        print("awesome_go activity count: ", count)
