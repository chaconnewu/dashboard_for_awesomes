# -*- coding: utf-8 -*-

# Check the difference of GitHub repos recorded in awesome_*_github_repos.txt and in awesome_*_github_repos_[date] MySQL table

import pymysql
import yaml

from datetime import datetime

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
filename = file_path_prefix + project_name + '_github_repos.txt'

urls_from_file = open(filename, 'r').read().split('\n')

repo_table_name = config[project_name]['name'] + '_' + 'github_repos_' + datetime.now().strftime('%Y_%m_%d')

# retrieve urls from Database table
query = 'select repo_url from ' + repo_table_name;
cur.execute(query)
rows = cur.fetchall()
urls_from_table = [x[0] for x in rows]

diffs = set(urls_from_file) -  set(urls_from_table)

for item in diffs:
    print(item)
