import glob
from collections import Counter
import sys
import numpy as np
import subprocess
import pandas as pd


site = 'sgp'
dirs = glob.glob('/data/archive/' + site + '/*ecorsfE41*')
dirs.sort()
exclude_dirs = ['sacr', 'kazr', 'dl', 'camseastate', 'mwacr', 'image',
                'mask', 'sonde', 'mwrtip', 'rwpspec']

#df = {'ds': [], 'date_per': [], 'file_per': []}
df = {'ds': [], 'score': []}
what_to_print = []
data = {}
for d in dirs:
    if any(ed in d for ed in exclude_dirs):
        continue
    print(d)
    files = glob.glob(d + '/*')
    if len(files) == 0:
        continue
    dates = [f.split('.')[-3] for f in files]
    counts = Counter(dates)
    idx = np.where(np.array(list(counts.values())) > 1)
    dates = list(np.array(list(counts.keys()))[idx])
    split_files = [f for f in files if any(d in f for d in dates)]
    data[d] = {'n_split_files': len(idx[0]), 'n_days': len(counts.keys()), 'split_files': split_files}

    arg = '/home/ermold/apps/el7/ermold/bin/nc_find_overlaps ' + d + '/*'
    results = subprocess.Popen(arg, shell=True, stdout=subprocess.PIPE)
    data[d].update({'reproc_files': []})
    data[d].update({'delete_files': []})
    data[d].update({'unknown_files': []})
    for line in results.stdout:
        if 'R' in str(line).split('\\t')[0].split(' ')[0]:
            data[d]['reproc_files'].append(str(line).split('\\t')[0].split(' ')[1])
            dates.append(str(line).split('\\t')[0].split(' ')[1].split('.')[-3])
        if 'D' in str(line).split('\\t')[0].split(' ')[0]:
            data[d]['delete_files'].append(str(line).split('\\t')[0].split(' ')[1])
            dates.append(str(line).split('\\t')[0].split(' ')[1].split('.')[-3])
        if '?' in str(line).split('\\t')[0].split(' ')[0]:
            data[d]['unknown_files'].append(str(line).split('\\t')[0].split(' ')[1])
            dates.append(str(line).split('\\t')[0].split(' ')[1].split('.')[-3])
            #print(str(line).split('\\t')[0])

    data[d]['n_unknown_files'] = len(data[d]['unknown_files'])
    data[d]['n_reproc_files'] = len(data[d]['reproc_files'])
    data[d]['n_delete_files'] = len(data[d]['delete_files'])
    data[d]['n_files'] = len(files)

    df['ds'].append(d)
    #if len(counts.keys()) > 0:
    #    df['date_per'].append(100 - 100. * len(np.unique(dates))/len(counts.keys()))
    #else:
    #    df['date_per'].append(0)
    #if data[d]['n_files'] > 0:
    #    df['file_per'].append(100 - 100. * (data[d]['n_split_files'] / data[d]['n_days'] +(data[d]['n_unknown_files'] + data[d]['n_reproc_files'] + data[d]['n_delete_files']) / data[d]['n_files']))
    #else:
    #    df['file_per'].append(0)

    all_files = data[d]['split_files'] + data[d]['unknown_files'] + data[d]['reproc_files'] + data[d]['delete_files']
    df['score'].append(100 - 100. * len(np.unique(all_files)) / len(files))

df = pd.DataFrame(data=df)
print(df.sort_values(by=['score']).to_string())
