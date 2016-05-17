import subprocess
import yaml

awesome_project_list = ['awesome_tensorflow', 'awesome_go', 'awesome_python', 'awesome_ruby']

def process(project_name):
    with open('config.yml', 'r') as config_file:
        config = yaml.load(config_file)
    config['current'] = project_name
    f = open('config.yml', 'w')
    f.write(yaml.dump(config, default_flow_style=False, indent=2))
    del f

    subprocess.check_call(['python3', 'automation.py'])

def main():
    for item in awesome_project_list:
        process(item)

if __name__ == '__main__':
    main()
