from collections import defaultdict
from urllib.parse import urlparse
from datetime import datetime, timedelta

import pymysql
import html2text
import subprocess
import yaml

h = html2text.HTML2Text()
full_html_str = ''
num_for_each_category = 10

with open('config.yml', 'r') as config_file:
    config = yaml.load(config_file)

conn = pymysql.connect(host='127.0.0.1', charset='utf8', use_unicode=True, unix_socket='/tmp/mysql.sock', user=config['database']['user'], passwd=None, db=config['database']['db'], autocommit=True)
cur = conn.cursor()
cur = conn.cursor()
repo_table_name = 'github_repos_' + datetime.now().strftime('%Y_%m_%d')
# repo_table_name = 'github_repos_2016_04_17'

time_format = '%Y-%m-%d'
current_time = datetime.now()
current_day = current_time.strftime(time_format)
previous_seven_days = (current_time - timedelta(days=7)).strftime(time_format)
previous_month = (current_time - timedelta(days=30)).strftime(time_format)

def determine_stats(stats_type):
    if stats_type == 'star':
        return ['WatchEvent', 'starred', ':star:']
    elif stats_type == 'active':
        return ['PushEvent',  'active', 'Pushes']
    elif stats_type == 'pull request':
        return ['PullRequestEvent',  'pull requests', 'PRs']

def determin_time_period(time_period):
    if time_period == 'week':
        return previous_seven_days
    elif time_period == 'month':
        return previous_month

def generating_stats(stats_type, time_type, current, num=None):
    event_type, header_text, table_header_text = determine_stats(stats_type)
    time_period = determin_time_period(time_type)


    query = "select repo_name, a.repo_url, count(*) as cnt, stargazers_count, description from awesome_go_activities as a, %s as b where a.repo_url=b.url and type='%s' and (a.created_at >= '%s' and a.created_at < '%s') group by repo_url order by cnt desc" % (repo_table_name, event_type, time_period, current)

    if num:
        query += ' limit ' + str(num)

    cur.execute(query)

    table_list = []
    for row in cur:
        repo_name, repo_api_url, increased_star_count, stars_count, description = row
        simplified_name = repo_name.split('/')[-1]
        repo_url = 'https://github.com/' + '/'.join(urlparse(repo_api_url).path.split('/')[-2:])
        table_list.append([simplified_name, repo_url, str(increased_star_count), str(stars_count), description])

    html_str = '<h2>Most %s repos in the past %s (from %s to %s)</h2>' % (header_text, time_type, time_period, current)
    table_html_str = '<table><tr><th>Repo name</th><th>:arrow_up:%s </th><th>:star:</th><th>Description</th></tr>' % (table_header_text)

    for row in table_list:
        table_html_str += '<tr>'
        table_html_str += "<td><a href=%s target='_blank'>%s</a></td><td>%s</td><td>%s</td><td>%s</td>" % (row[1], row[0], row[2], row[3], row[4])

        table_html_str += '</tr>'

    table_html_str += '</table>'
    html_str += table_html_str

    return html_str

def generating_inactive_repos(query_repo, query_activity, header):
    cur.execute(query_repo)

    all_repos = []
    for row in cur:
        all_repos.append(row)

    cur.execute(query_activity)

    active_repos = []
    for row in cur:
        active_repos.append(row[0])

    inactive_repos = []
    for row in all_repos:
        if row[0] not in active_repos:
            inactive_repos.append(row)

    header += ' (%d repos)' % (len(inactive_repos))
    html_str = '<h2>%s</h2>' % (header)
    table_html_str = '<table><tr><th>Repo name</th><th>:star:</th><th>Description</th></tr>'
    for row in inactive_repos:
        url, stars_count, description = row
        repo_name = urlparse(url).path.split('/')[-1]
        repo_url = "https://github.com/" + '/'.join(urlparse(url).path.split('/')[-2:])
        table_html_str += "<tr><td><a href=%s target='_blank'>%s</a></td><td>%s</td><td>%s</td></tr>" % (repo_url, repo_name, str(stars_count), description)
    table_html_str += '</table>'
    html_str += table_html_str
    return html_str

inactive_2016_query_repo = "select url, stargazers_count, description from " + repo_table_name + " where updated_at < '2016' order by stargazers_count asc"
inactive_2016_query_activity = 'select distinct repo_url from awesome_go_activities'
inactive_2016_header = 'Inactive repos in 2016 (no recorded events and last updated was before 2016)'

inactive_no_push_repo = "select url, stargazers_count, description from " + repo_table_name + " where pushed_at < '2016' order by stargazers_count asc"
inactive_no_push_activity = 'select distinct repo_url from awesome_go_activities where type="PushEvent"'
inactive_no_push_header = 'Inactive repos that has no push event in 2016'

full_html_str = generating_stats('star', 'week', current_day, num_for_each_category) + generating_stats('active', 'week', current_day, num_for_each_category) + generating_stats('star', 'month', current_day, num_for_each_category) + generating_stats('active', 'month', current_day, num_for_each_category) + generating_inactive_repos(inactive_2016_query_repo, inactive_2016_query_activity, inactive_2016_header) + generating_inactive_repos(inactive_no_push_repo, inactive_no_push_activity, inactive_no_push_header)

f = open('awesome_go_dashboard.html', 'w')
f.write(full_html_str)
del f

# Generating GithuB Flavored Markdown file with pandoc
subprocess.check_call(['pandoc', 'awesome_go_dashboard.html', '-f', 'html', '-t', 'markdown_github', '-s', '--toc', '-o', 'awesome_go_dashboard.md'])
