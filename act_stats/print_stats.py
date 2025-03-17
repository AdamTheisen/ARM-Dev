import os
from github import Github


token = os.getenv('GITHUB_TOKEN')

g = Github(token)
repo = g.get_repo('ARM-DOE/ACT')
clones = repo.get_clones_traffic(per='day')
views = repo.get_views_traffic(per='day')

print(dir(views['views'][0]))

for i in range(len(views['views'])):
    ts = views['views'][i].timestamp
    for j in range(len(clones['clones'])):
        if clones['clones'][j].timestamp == ts:
            clone_ct = str(clones['clones'][j].count)
            clone_uni = str(clones['clones'][j].uniques)
            break
        else:
            clone_ct = str(0)
            clone_uni = str(0)
    print(','.join([str(views['views'][i].timestamp.date()), clone_ct, clone_uni, str(views['views'][i].count), str(views['views'][i].uniques)]))

