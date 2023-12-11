import json
from urllib.error import HTTPError, URLError
import datetime
import pandas as pd
import numpy as np

try:
    from urllib.request import urlopen
except ImportError:
    from urllib import urlopen

mentors = {
    'Rob Newsom': 6914,
    'Raghavendra Krishnamurthy': 20548,
    'Jenni Kyrouac': 7820
}

instrument = ['dl']
mentor_id = [6914, 20548]
#instrument = ['met', 'stamp']
#mentor_id = [7820]

dq_id = [20149]
dqpr_start = datetime.datetime(2020, 1, 1, 0, 0, 0)
dqpr_end = datetime.datetime(2023, 12, 31, 23, 59, 59)

"""
status : int, list of int, None
        Status numbers to use in query as of May 2020.
        1 = Open - Requries Action
        2 = In Progress - Assignments
        3 = Closed - All Assignments Completed
        4 = Open - Escalated to PRB Attention
        6 = Closed = No DQR or PRB Requested Solution Assignments Requried
        8 = Waiting - For Spares
        9 = Waiting - For Site Visit
        9999 = DQPR Rejected
"""
status = [3, 6]

for inst in instrument:
    query_url = ['http://armui-prod:8081/dqprapi/dq/dqpr/search']
    query_url += [f"instrument={inst}"]
    query_url[0] = query_url[0] + '?'
    query_url = '&'.join(query_url)

    # Perform HTML query
    response_body = urlopen(query_url).read().decode("utf-8")

    # parse into json object
    response_body_json = json.loads(response_body)

    dqpr_number = []
    dqpr_sd = []
    dqpr_ed = []
    dqpr_status = []
    dqpr_submitter = []
    for dqpr in response_body_json:
        if dqpr['dqprStatus'] not in status:
            continue

        sd = datetime.datetime.strptime(dqpr['dqprEntrydateStr'], '%Y-%m-%d %H:%M:%S')
        if dqpr['dqprStatus'] not in [3, 6]:
            continue
        for dqprStatusDict in dqpr['dqprStatusObj']:
            ed = int(int(dqprStatusDict['dateset'])/1000)
            ed = datetime.datetime.utcfromtimestamp(ed)

        if (ed < dqpr_start) or (sd > dqpr_end):
            continue

        dqpr_number.append(dqpr['dqprNo'])
        dqpr_sd.append(sd)
        dqpr_ed.append(ed)
        dqpr_status.append(dqpr['dqprStatus'])
        dqpr_submitter.append(dqpr['personId'])

    # Get Comment History
    #dqpr_number = [12366]
    data = []
    for i, d in enumerate(dqpr_number):
        mentor_submitted = False
        if dqpr_submitter[i] in mentor_id:
            mentor_submitted = True

        time_to_close = dqpr_ed[i] - dqpr_sd[i]
        query_url = 'http://armui-prod:8081/dqprapi/dq/comment/user/'
        query_url += str(d)

        response_body = urlopen(query_url).read().decode("utf-8")
        response_body_json = json.loads(response_body)

        ct = 0
        for c in response_body_json:
            if c['personId'] in mentor_id:
                time_to_first_comment = (datetime.datetime.fromtimestamp(c['commentDate'] / 1000.) - dqpr_sd[i]).days
                break
            else:
                time_to_first_comment = -9999
            ct += 1

        # DQPR No, Time to Close Out, Time to first mentor comment, comments between mentor comments, mentor submitted
        data.append([d, time_to_close.days, time_to_first_comment, ct, mentor_submitted])

    col = ['DQPR', 'Time-to-Close', 'First-Comment', 'Comments-to-Mentor', 'MentorSubmitted']
    df = pd.DataFrame(data, columns=col)

    df = df.replace(-9999, np.nan)
    print('Statistics for: ', inst)
    print('Dates: ', '-'.join([str(dqpr_start), str(dqpr_end)]))
    print('Number of DQPRs: ', len(dqpr_number))
    print('Days to Close (Avg/Min/Max): ', int(df.loc[:, 'Time-to-Close'].mean()),
        '/', df.loc[:, 'Time-to-Close'].min(), '/', df.loc[:, 'Time-to-Close'].max())

    df2 = df[~df.MentorSubmitted]
    print('\nExcluding Mentor Submitted DQPRs')
    print('-------------------------------')
    print('Number of DQPRs: ', len(df2.index))
    print('Days to First Comment (Avg/Min/Max): ', int(df2.loc[:, 'First-Comment'].mean()),
        '/', df2.loc[:, 'First-Comment'].min(), '/', df2.loc[:, 'First-Comment'].max())
    print('Comments before First Mentor Comment(Avg/Min/Max): ', int(df2.loc[:, 'Comments-to-Mentor'].mean()),
        '/', df2.loc[:, 'Comments-to-Mentor'].min(), '/', df2.loc[:, 'Comments-to-Mentor'].max())

    print(','.join([inst, str(dqpr_start), str(dqpr_end), str(len(dqpr_number)), str(int(df.loc[:, 'Time-to-Close'].mean())),
        str(df.loc[:, 'Time-to-Close'].min()), str(df.loc[:, 'Time-to-Close'].max()),
        str(len(df2.index)), str(int(df2.loc[:, 'First-Comment'].mean())),
        str(df2.loc[:, 'First-Comment'].min()), str(df2.loc[:, 'First-Comment'].max()),
        str(int(df2.loc[:, 'Comments-to-Mentor'].mean())),
        str(df2.loc[:, 'Comments-to-Mentor'].min()), str(df2.loc[:, 'Comments-to-Mentor'].max())]))
