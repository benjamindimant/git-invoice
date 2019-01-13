from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import requests

# Load in template
env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('index.html')

date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
base_url = 'https://api.github.com'

username = input("Username: ")
password = input("Password: ")
repository = input("Repository: ")

auth=(username, password)

print(base_url + '/users/{0}'.format(username))

user = requests.get(base_url + '/users/{0}'.format(username), auth=auth)

commits = requests.get(base_url + '/repos/{0}/{1}/commits'.format(username, repository), auth=auth)

print(commits.json())

output = template.render(
    date=date
)

# to save the results
with open("my_new_file.html", "w") as fh:
    fh.write(output)
