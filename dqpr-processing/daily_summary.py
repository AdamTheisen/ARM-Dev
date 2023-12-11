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

def convert_datetime_time_from_epoch(d):
    epoch = dt.datetime.utcfromtimestamp(0)
    return ('%f' % ((d - epoch).total_seconds() * 1000)).split(".")[0]

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

#Initialize DQPR API
dqpr_api = DQPR_API(SETTINGS)

sdate = dt.datetime(dt.datetime.now().year,dt.datetime.now().month,
    dt.datetime.now().day-1,0,0,0)
sdate = convert_datetime_time_from_epoch(sdate)

#Query DQPR DB
result_set = dqpr_api.search_dqprs({"comment_date": sdate,
    "status": ",".join(["{}".format(status) for status in non_rejected_status])})

print(sdate)
for dqpr in result_set:
    dqpr_no = dqpr['dqprNo']
    comments = dqpr_api.get_comment_history(dqpr_no)
    print(comments[-1])
    sys.exit()
