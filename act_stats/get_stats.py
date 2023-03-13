import os
from github import Github
import datetime as dt

token = os.getenv('GITHUB_TOKEN')

g = Github(token)
repo = g.get_repo('ARM-DOE/ACT')
clones = repo.get_clones_traffic(per='day')
views = repo.get_views_traffic(per='day')

now = dt.date.today()
if now == views['views'][-1].timestamp.date():
   idx = -2
else:
   idx = -1

for i in range(len(views['views'])):
    ts = views['views'][idx].timestamp
    for j in range(len(clones['clones'])):
        if clones['clones'][j].timestamp == ts:
            clone_ct = str(clones['clones'][j].count)
            clone_uni = str(clones['clones'][j].uniques)
            break
        else:
            clone_ct = str(0)
            clone_uni = str(0)
    a = ','.join([str(ts), clone_ct, clone_uni, str(views['views'][idx].count), str(views['views'][idx].uniques)])

#a = ','.join([str(clones['clones'][idx].timestamp), str(clones['clones'][idx].count), str(clones['clones'][idx].uniques),
#              str(views['views'][idx].count),  str(views['views'][idx].uniques)])

f = open('/home/theisen/Code/ARM-Dev/act_stats/act_stats.csv', 'a')
f.write(a + '\n')
f.close()
