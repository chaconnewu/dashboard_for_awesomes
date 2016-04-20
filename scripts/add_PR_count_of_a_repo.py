import requests
import mistune
import re
import pymysql
import yaml
import iso8601
import pytz
import subprocess
import html.parser
import traceback

from bs4 import BeautifulSoup, Tag
from datetime import datetime, timedelta
from dateutil.parser import parse
from pprint import pprint

h = html.parser.HTMLParser()

file_path_prefix = '../awesomes/'

with open('config.yml', 'r') as config_file:
    config = yaml.load(config_file)

conn = pymysql.connect(
    host='127.0.0.1',
    charset='utf8',
    use_unicode=True,
    unix_socket='/tmp/mysql.sock',
    user=config['database']['user'],
    passwd=None,
    db=config['database']['db'],
    autocommit=True
    )

cur = conn.cursor()
project_name = config['current']
repo_table_name = config[project_name]['name'] + '_' + 'github_repos_' + datetime.now().strftime('%Y_%m_%d')

query = 'select url from %s' % (repo_table_name)
cur.execute(query)
rows = cur.fetchall()

count = 0
for row in rows:
    api_url = row[0]
    pulls_url = api_url + '/pulls?page=1&per_page=100'
    try:
        r = requests.get(pulls_url, auth=(config['github_credential']['username'], config['github_credential']['password']))
        prs = r.json()
        open_pr_count = len([x for x in prs if x['state'] == 'open'])
        query = "update %s set open_pr_count='%d' where url='%s'" % (repo_table_name, open_pr_count, api_url)
        cur.execute(query)
    except:
        traceback.print_exc()
