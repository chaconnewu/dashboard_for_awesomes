import mistune
import re
import pymysql
import yaml
import iso8601
import pytz
import subprocess
import html.parser

from bs4 import BeautifulSoup, Tag
from datetime import datetime, timedelta

from dateutil.parser import parse

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

# repo_table_name = 'github_repos_2016_04_17'

# Load awesome-* with BeautifulSoup
content = open(file_path_prefix + project_name + '.md', 'r').read()
content = content.replace('] (http', '](http')
markdown = mistune.Markdown()
soup = BeautifulSoup(markdown(content), 'html.parser')

lis = soup.find_all('li');

visited = set()

html_str = '<ul>'
for li in lis:
    a = li.find_all('a')
    repo_url = a[0]['href']

    if len(a) > 0 and re.search('^https://github.com/[^/]+/[^/]+/?$', repo_url):
        query = "select stargazers_count, pushed_at from %s where repo_url='%s'" %(repo_table_name, repo_url)
        cur.execute(query)
        rows = cur.fetchall()
        if len(rows) == 1:
            stars_count, updated_at = rows[0]
            updated_at_datetime = parse(updated_at)

            updated_days_ago = (datetime.now(pytz.utc)- updated_at_datetime).days
            if updated_days_ago >= 90:
                html_str += str(li)

filename = file_path_prefix + 'least_updated_items_in_' + project_name
f = open(filename + '.html', 'w')
f.write(html_str)
del f

subprocess.check_call(
['pandoc', filename + '.html', '-f', 'html', '-t', 'markdown_github', '-s', '-o', filename + '.md'])
