from api.dqpr_api import DQPR_API
from config.settings import SETTINGS
import datetime as dt
import pandas as pd
import numpy as np
import time
import json
import os
from collections import OrderedDict
import urllib
from scipy import stats
import csv


def convert_datetime_time_from_epoch(d):
    epoch = dt.datetime.utcfromtimestamp(0)
    return ('%f' % ((d - epoch).total_seconds() * 1000)).split(".")[0]


def get_url(search_url):
    print(search_url)
    with urllib.request.urlopen(search_url) as url:
        results = json.loads(url.read().decode())
    return results

non_rejected_status = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
all_status = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,9999]
open_waiting_status = [1,2,4,8,9,10,11,12,13,14,15]
closed_status = [3,6,12]

codeDesc=['Incorrect','Questionable','Missing','-9999','Data Unaffected']
statusDesc=['Open - Requires Action','In Progress - Assignments',
'Closed - All Assignments Complete', 'Open - Escalated to PRB Attention',
'Closed - No DQR or PRB Requested Solution','Waiting - For Spares',
'Waiting - For Site Visit','DQPR Rejected']
statusVal=[1,2,3,4,6,8,9,9999]

dqpr_api = DQPR_API(SETTINGS)

test = {}
test['submitter'] = {}
test['dqpr_total'] = {}
test['instruments'] = {}
test['site_totals'] = {}
test['site_totals_open_waiting'] = {}
test['status_totals'] = {}

test['open_close_stats']={}
test['open_close_stats']['days_30'] = 0
test['open_close_stats']['days_30_90'] = 0
test['open_close_stats']['days_90'] = 0
test['open_close_stats']['closed_last_month'] = 0

test['mean_days_open']={}
test['instruments_days_open']={}
year_mean = {}
year_median = {}

test['metadata'] = {}
cyear = dt.datetime.now().strftime('%Y')

today = dt.date.today()
first = today.replace(day=1)
prev_month = (first - dt.timedelta(days=1)).strftime('%m%Y')

sdate = dt.datetime.now().strftime('%m/%d/%Y')
test['metadata']['current_year'] = cyear
test['metadata']['start_date'] = sdate
test['metadata']['year_mean_days_open']={}
test['metadata']['year_median_days_open']={}

sdate = dt.datetime(dt.datetime.now().year-10,1,1,0,0,0)
sdate = convert_datetime_time_from_epoch(sdate)
result_set = dqpr_api.search_dqprs({"start_date": sdate,
    "status": ",".join(["{}".format(status) for status in closed_status])})
#result_set = dqpr_api.get_last_year()
for dqpr in result_set:
    entry = dqpr['entryDate']
    entry = dt.datetime.fromtimestamp(entry/1000.)
    mean_days = (dt.datetime.now()-entry).total_seconds()/(24.*60.*60.)
    
    entry_date = entry.strftime('%Y%m%d')
    entry_year = entry.strftime('%Y')
    if entry_date not in test['dqpr_total']:
        test['dqpr_total'][entry_date] = 1
    else:
        test['dqpr_total'][entry_date] += 1
    loc = dqpr['dqprLocObj']
    #Get Status
    status = dqpr['dqprStatus']
    if status in closed_status:
        closed = dqpr['dqprStatusObj'][-1]['dateset']
        closed = dt.datetime.fromtimestamp(closed/1000.)
        if closed.strftime('%m%Y') == prev_month:
            test['open_close_stats']['closed_last_month'] += 1
        mean_days = (closed-entry).total_seconds()/(24.*60.*60.)

    if loc[0]['site'] not in test['site_totals_open_waiting']:
        if status in open_waiting_status: 
            test['site_totals_open_waiting'][loc[0]['site']] = 1
    else:
        if status in open_waiting_status: 
            test['site_totals_open_waiting'][loc[0]['site']] += 1

    if status in open_waiting_status:
        if status not in test['status_totals']:
            test['status_totals'][status] = 1
        else:
            test['status_totals'][status] += 1

    if mean_days != 0:
        if entry_year in year_mean:
            year_mean[entry_year].append(mean_days)
        else:
            year_mean[entry_year] = [mean_days]

###Only for this year
    if  entry.strftime('%Y') != cyear:
        continue
    if status in open_waiting_status:
        if mean_days <= 30:
            test['open_close_stats']['days_30'] += 1
        elif mean_days <= 90:
            test['open_close_stats']['days_30_90'] += 1
        elif mean_days > 90:
            test['open_close_stats']['days_90'] += 1
 

    #Site Totals
    if loc[0]['site'] not in test['site_totals']:
        test['site_totals'][loc[0]['site']] = 1
    else:
        test['site_totals'][loc[0]['site']] += 1
    #Instrument totals
    if loc[0]['instrument'] not in test['instruments']:
        test['instruments'][loc[0]['instrument']] = 1
    else:
        test['instruments'][loc[0]['instrument']] += 1

    if status not in open_waiting_status or status not in ['9999']:
        if loc[0]['instrument'] not in test['instruments_days_open']:
            test['instruments_days_open'][loc[0]['instrument']] = [mean_days]
        else:
            test['instruments_days_open'][loc[0]['instrument']].\
                append(mean_days)

    #Submitter
    submitter = dqpr['personId']
    print(submitter)
    url = 'https://adc.arm.gov/arm-armint-api/instrument/contact?personId='+str(submitter)
    #r = get_url(url)
    #submitter = r['nameLast']
    #if submitter not in test['submitter']:
    #    test['submitter'][submitter] = 1
    #else:
    #    test['submitter'][submitter] += 1

for i in test['instruments_days_open']:
    test['mean_days_open'][i] = np.mean(test['instruments_days_open'][i])

hist = []
bins = np.linspace(0,200,41)
year = []
f = open('./dqpr_stats.txt', 'w+')
f.write(','.join(bins.astype(str)))
f.write('\n')
for y in year_mean:
    test['metadata']['year_mean_days_open'][y] = np.mean(year_mean[y])
    test['metadata']['year_median_days_open'][y] = np.median(year_mean[y])
    print(y,np.mean(year_mean[y]),np.median(year_mean[y]))
    hist = np.histogram(year_mean[y], bins)[0]
    f.write(','.join(hist.astype(str)))
    f.write('\n')

f.close()

cdate = dt.datetime.now().strftime('%Y%m%d')
dqpr_file = os.path.join(os.environ['DQ_DATA'],'dqpr_stats',cdate+'.json')
with open(dqpr_file,'w') as fp:
    json.dump(test,fp)

