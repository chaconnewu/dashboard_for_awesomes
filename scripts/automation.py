import subprocess
import yaml

from datetime import datetime

with open('config.yml', 'r') as config_file:
    config = yaml.load(config_file)

project_name = config['current']
today = datetime.now().strftime('%Y-%m-%d')

# Parse original .md to extract all GitHub repos
subprocess.check_call(['python3', 'get_all_github_repos.py'])

# Retrieve all repo info and store in database
subprocess.check_call(['python3', 'get_repo_info.py'])

# Attach stars count and last pushed date
subprocess.check_call(['python3', 'attach_info_for_github_repos.py'])

# Update dashboard_for_awesomes
# subprocess.check_call(['cd', '..'])
# subprocess.check_call(['git', 'add', '.'])
# subprocess.check_call(['git', 'commit', '-m', 'Update ' + project_name + ' (' + today + ')'])
# subprocess.check_call(['git', 'push'])
#
# # Update awesome-* project
# filename = project_name + '_with_repo_info.md'
# project_name = project_name.replace('_', '-')
# subprocess.check_call(['cp', 'awesomes/' + filename, '../' + project_name + '/'])
# subprocess.check_call(['cd', '../' + project_name])
# subprocess.check_call(['git', 'add', '.'])
# subprocess.check_call(['git', 'commit', '-m', 'Update ' + project_name + ' (' + today + ')'])
# subprocess.check_call(['git', 'push'])
