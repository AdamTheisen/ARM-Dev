from api.dqpr_api import DQPR_API
from config.settings import SETTINGS
import datetime as dt
import requests
import pandas as pd
import numpy as np
import time
import json
import os
from collections import OrderedDict
import sys

import urllib.request

def convert_datetime_time_from_epoch(d):
    epoch = dt.datetime.utcfromtimestamp(0)
    return ('%f' % ((d - epoch).total_seconds() * 1000)).split(".")[0]


def get_url(search_url):
    with urllib.request.urlopen(search_url) as url:
        results = json.loads(url.read().decode())
    return results

#1    Open - Requires Action
#2    In Progress - Assignments
#3    Closed - All Assignments Completed
#4    Open - Escalated to PRB Attention
#6    Closed - No DQR or PRB Requested Solution Assignments Required
#8    Waiting - For Spares
#9    Waiting - For Site Visit
#9999    DQPR Rejected

non_rejected_status = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
all_status = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,9999]
open_waiting_status = [1,2,4,8,9,10,11,12,13,14,15]
closed_status = [3,5,6,7]

codeDesc=['Incorrect','Questionable','Missing','-9999','Data Unaffected']
statusDesc=['Open - Requires Action','In Progress - Assignments',
'Closed - All Assignments Complete', 'Open - Escalated to PRB Attention',
'Closed - No DQR or PRB Requested Solution','Waiting - For Spares',
'Waiting - For Site Visit','DQPR Rejected']
statusVal=[1,2,3,4,6,8,9,9999]


comment_url = 'https://adc.arm.gov/dq/api/dq/comment/user/'
search_url = 'https://adc.arm.gov/DQPRSearch/dq/dqpr/search?'
pid_url = 'https://adc.arm.gov/arm-people-api/person/search?personIds='
lname_url = 'https://adc.arm.gov/arm-people-api/person/search?nameLast='

mentor = 'Newsom'
mentor_id = 6914
instruments = ['dl', 'rl']
#mentor_results = get_url(lname_url+mentor)[0]
#mentor_id = mentor_results['personId']


for instrument in instruments:
    print(instrument)
    criteria = {
                'instrument': instrument,
                'start_date': '1609480800000'
               }

    search = search_url
    for c in criteria:
        search += c + '=' + criteria[c] + '&'

    print(search)
    results = get_url(search)
    print(results)
    days = []
    no_comment = []
    for dqpr in results:
        if dqpr['personId'] == mentor_id:
            continue
        entry_date = pd.to_datetime(dqpr['dqprEntrydateStr'])
        dqpr_no = dqpr['dqprNo']
        comments = get_url(comment_url+str(dqpr_no))
        mentor_comment_date = None
        for c in comments:
            c_id = c['personId']
            if mentor_id == c_id:
                mentor_comment_date = dt.datetime.fromtimestamp(c['commentDate']/1000.)
                break
        if mentor_comment_date is None:
            no_comment.append(dqpr_no)
        else:
            days.append(mentor_comment_date - entry_date)

        status = dqpr['dqprStatusObj']

    if len(days) > 0:
        avg_days_to_comment = sum(days, dt.timedelta())/len(days)
        print('  Number DQPRs: ',len(days),'\n  Avg: ',avg_days_to_comment.days,
            '\n  Min: ',min(days).days, '\n  Max: ',max(days).days, '\n  No Comment: ',len(no_comment))
    else:
        print(' Number DQPRs: 0')

