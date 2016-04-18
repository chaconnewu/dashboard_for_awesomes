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

awesome_url = config['awesome-go']['url']

# Load Markdown content and convert it into HTML
f = open('awesome-go.md', 'wb')
f.write(requests.get("https://raw.githubusercontent.com/avelino/awesome-go/master/README.md").content)
del f

content = open('awesome-go.md', 'r').read()
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

f = open('awesome_go_github_repos.txt', 'w')

f.write('\n'.join([x for x in github_repo_urls]))
del f
