import subprocess


items = ['awesome_go', 'awesome_ruby', 'awesome_python', 'awesome_tensorflow']

for item in items:
    filename = './awesomes/' + item + '_with_repo_info.md'
    subprocess.check_call(['cp', filename, '../' + item.replace('_', '-') + '/'])
