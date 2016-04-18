import mistune
import re
import pymysql
import yaml
import html.parser
import requests

from bs4 import BeautifulSoup, Tag
from datetime import datetime


with open('config.yml', 'r') as config_file:
    config = yaml.load(config_file)

project_name = config['current']
project_readme_raw_url = config[project_name]['url']
awesome_url = config[project_name]['url']

# Load Markdown content and convert it into HTML
f = open(project_name + '.md', 'wb')
f.write(requests.get(project_readme_raw_url).content)
del f

content = open(project_name + '.md', 'r').read()
content = content.replace('] (http', '](http')
markdown = mistune.Markdown()
soup = BeautifulSoup(markdown(content), 'html.parser')

lis = soup.find_all('li');
github_repo_urls = set()
for li in lis:
    a = li.find_all('a')
    repo_url = a[0]['href']
    if len(a) > 0 and re.search('^https://github.com/[^/]+/[^/]+/?$', repo_url):
        github_repo_urls.add(repo_url)

f = open(project_name + '_github_repos.txt', 'w')

f.write('\n'.join([x for x in github_repo_urls]))
del f
