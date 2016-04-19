import requests
import pymysql
import json
import traceback
from urllib.parse import urlparse
from datetime import datetime
import pymysql
import yaml

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
file_path_prefix = '../awesomes/'
repo_table_name = config[project_name]['name'] + '_' + 'github_repos_' + datetime.now().strftime('%Y_%m_%d')

query = '''create table if not exists ''' + repo_table_name + '''
(
     created_at varchar(255),
     description varchar(2048),
     fork boolean,
     forks_count int,
     full_name varchar(255),
     homepage varchar(255),
     id int primary key,
     language varchar(255),
     name varchar(255),
     open_issues_count int,
     owner_login varchar(255),
     owner_url varchar(255),
     pushed_at varchar(255),
     repo_url varchar(255),
     size int,
     stargazers_count int,
     subscribers_count int,
     updated_at varchar(255),
     url varchar(255),
     watchers_count int
) CHARACTER SET = utf8;'''


cur.execute(query)

filename = file_path_prefix + project_name + '_github_repos.txt'

f = open(filename, 'r').read()
# f = open('diffs.txt', 'r').read()

url_list = f.split('\n')[:-1] # get rid of the last empty one

missed = []
for idx, item_url in enumerate(url_list):
    repo_url = 'https://api.github.com/repos' + urlparse(item_url).path
    try:
        r = requests.get(repo_url, auth=(config['github_credential']['username'], config['github_credential']['password']))
        content = r.json()

        created_at = content.get('created_at', 'None')
        description = content.get('description', 'None')
        if description != None:
            description = description.replace("'", "\\'")
        fork = content['fork']
        forks_count = content['forks_count']
        full_name = content['full_name']
        homepage = content.get('homepage', 'None')
        id = content['id']
        language = content['language']
        name = content['name']
        open_issues_count = content['open_issues_count']
        owner_login = content['owner']['login']
        owner_url = content['owner']['url']
        pushed_at = content['pushed_at']
        repo_url = content['html_url']
        size = content['size']
        stargazers_count = content['stargazers_count']
        subscribers_count = content['subscribers_count']
        updated_at = content['updated_at']
        url = content['url']
        watchers_count = content['watchers_count']

        values = "('%s', '%s', '%i', '%d', '%s', '%s', '%d', '%s', '%s', '%d', '%s', '%s', '%s', '%s', '%d', '%d', '%d', '%s', '%s', '%d');" % (created_at, description, fork, forks_count, full_name, homepage, id, language, name, open_issues_count, owner_login, owner_url, pushed_at, repo_url, size, stargazers_count, subscribers_count, updated_at, url, watchers_count)
        insert_query = 'insert into ' + repo_table_name + ' values ' + values
        cur.execute(insert_query)
        print('success at: ', idx)
    except:
        traceback.print_exc()
        print(content)
        missed.append(item_url)
        if content.get('message') == 'Not Found':
            continue
        else:
            print('failed at: %d, %s' % (idx, repo_url))
            # print(content)
            print(insert_query)
            # break

for item in missed:
    print(item)
