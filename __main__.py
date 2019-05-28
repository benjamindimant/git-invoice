import math
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
from dateutil import parser, relativedelta
import requests
import getpass

# Load in template
env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('index.html')

date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
base_url = 'https://api.github.com'

username = input("Username: ")
password = getpass.getpass("Password: ")
repository = input("Repository: ")

auth=(username, password)

user = requests.get(base_url + '/users/{0}'.format(username), auth=auth)

repo = requests.get(base_url + '/repos/{0}/{1}/stats/contributors'.format(username, repository), auth=auth)

total_commits = 0
data = []
contributors = []
start_date = None
end_date = None
for contributor in repo.json():
    total_commits += contributor['total']
    weeks = contributor['weeks']
    contributors.append(contributor['author']['login'])
    end_reached = False
    for i in range(len(weeks) - 1, -1, -1):
        week = weeks[i]
        if week['c'] == 0 and not end_reached:
            continue
        else:
            end_reached = True
            if end_date is None:
                end_date = week['w']
        data.append(week['c'])
        if i == 0:
            start_date = week['w']
data.reverse()

total_commits *= 2 # Account for merges

commits = []
for i in range(int(math.ceil(total_commits / 100))):
    r = requests.get(base_url + '/repos/{0}/{1}/commits?per_page=100&page={2}'.format(username, repository, i), auth=auth)
    commits += r.json()

parsed_commits = []
for commit in commits:
    c = commit.get('commit')
    c['author']['date'] = parser.isoparse(c['author']['date']).strftime('%H:%M:%S %d/%m/%Y')
    parsed_commits.append(commit.get('commit'))
parsed_commits.reverse()

months = []

current = datetime.fromtimestamp(start_date)
end_date = datetime.fromtimestamp(end_date)

while current <= end_date:
    months.append(current.strftime("%B"))
    current += relativedelta.relativedelta(months=1)

contributors_string = ''
for i in range(len(contributors)):
    contributors_string += contributors[i]
    if i != len(contributors) - 1:
        contributors_string += ', '

summary = {
    'title': repository,
    'total': len(commits),
    'data': data,
    'months': months,
    'contributors': contributors_string
}

output = template.render(
    summary=summary,
    date=date,
    months=months,
    commits=parsed_commits
)

# to save the results
with open(repository + ".html", "w") as fh:
    fh.write(output)
