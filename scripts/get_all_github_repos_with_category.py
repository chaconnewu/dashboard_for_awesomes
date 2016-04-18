import mistune
from bs4 import BeautifulSoup, Tag

import requests
import re
import yaml

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

# Get all categories
all_categories = []
for item in soup.find_all('h2'):
    all_categories.append(item)

def subcategories(elem):
    subs = []
    for item in elem.find_next_siblings():
        if item.name == 'h2':
            break
        if item.name == 'p':
            subs.append(item)
    return subs

def get_all_created_items_in_ul(ul):
    lis = [li for li in ul.find_all('li')]
    # Extrac resource Name, URL, and Description
    item_list = []
    for li in lis:
        if li.contents[0].name == 'a':
            item_name = li.contents[0].contents[0]
            item_url = li.contents[0]['href']
            item_desc = ''
            if len(li.contents) > 1:
                item_desc = li.contents[1].replace('-', '', 1).strip()
            item_list.append([item_name, item_url, item_desc])
    return item_list

def find_ul(h):
    cur_item = h.find_next_sibling()
    while cur_item.name != 'ul':
        cur_item = cur_item.find_next_sibling()
    return cur_item

resource_list = []
for category_index in range(len(all_categories)):
    category_dict = {
        'category_name': all_categories[category_index].contents[0]
    }
    subs = subcategories(all_categories[category_index])
    if len(subs) == 0:
        category_dict['subcategory_names'] = ['no_subcategory']
        category_dict['subcategory_list'] = get_all_created_items_in_ul(find_ul(all_categories[category_index]))
    else:
        category_dict['subcategory_names'] = []
        category_dict['subcategory_list'] = []
        for idx, h in enumerate(subs):
            category_dict['subcategory_names'].append(h.contents[0])
            category_dict['subcategory_list'].append(get_all_created_items_in_ul(find_ul(h)))

    resource_list.append(category_dict)

url_set = set()
def find_all_github_repos(curatedList):
    all_count = 0
    github_count = 0
    github_repos = []
    for category in curatedList:
        if category['subcategory_names'][0] == 'no_subcategory':
            for item in category['subcategory_list']:
                if re.search('^https://github.com/[^/]+/[^/]+/?$', item[1]):
                    github_repos.append(item)
                    url_set.add(item[1])
                    github_count += 1
                all_count += 1
        else:
            for subcateogry in category['subcategory_list']:
                for item in subcateogry:
                    if re.search('^https://github.com/[^/]+/[^/]+/?$', item[1]):
                        github_count += 1
                        github_repos.append(item)
                        url_set.add(item[1])
                    all_count += 1

find_all_github_repos(resource_list);

f = open('awesome_go_github_repos.txt', 'w')

f.write('\n'.join([x for x in url_set]))
del f
