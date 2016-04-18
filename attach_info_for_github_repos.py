import mistune
import re
import pymysql
import yaml
import iso8601
import pytz
import subprocess

from bs4 import BeautifulSoup, Tag
from datetime import datetime, timedelta
from dateutil.parser import parse


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
# repo_table_name = 'github_repos_' + datetime.now().strftime('%Y_%m_%d')
repo_table_name = 'github_repos_2016_04_17'

# Load awesome-* with BeautifulSoup
content = open('awesome-go.md', 'r').read()
content = content.replace('] (http', '](http')
markdown = mistune.Markdown()
soup = BeautifulSoup(markdown(content), 'html.parser')

lis = soup.find_all('li');

for li in lis:
    a = li.find_all('a')
    repo_url = a[0]['href']
    if len(a) > 0 and re.search('^https://github.com/[^/]+/[^/]+/?$', repo_url):
        # count += 1
        query = "select stargazers_count, updated_at from %s where repo_url='%s'" %(repo_table_name, repo_url)
        cur.execute(query)
        rows = cur.fetchall()
        if len(rows) == 1:
            stars_count, updated_at = rows[0]
            updated_at_datetime = parse(updated_at)

            updated_days_ago = (datetime.now(pytz.utc)- updated_at_datetime).days
            tag = soup.new_tag('span')
            tag.string = ' &#9733 %d, updated %d days ago ' % (stars_count, updated_days_ago)

            a[0].insert_after(tag)

f = open('awesome_go_with_repo_info.html', 'w')

f.write(soup.prettify())
del f

subprocess.check_call(
['pandoc', 'awesome_go_with_repo_info.html', '-f', 'html', '-t', 'markdown_github', '-s', '-o', 'awesome_go_with_repo_info.md'])
