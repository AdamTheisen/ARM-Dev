import json
from urllib.error import HTTPError, URLError
import datetime
import pandas as pd
import numpy as np

try:
    from urllib.request import urlopen
except ImportError:
    from urllib import urlopen

verbose = False
instrument_dict = {
    'acsm': [19076, 7124, 3676, 14927, 24081],
    'aeth': [7455, 3676, 14927, 24081],
    'aps': [7941, 3676, 21408, 22737, 14927, 24081],
    'caps-pmex': [7455, 3676, 14927, 24081],
    'cpc': [7941, 3676, 21408, 22737, 14927, 24081],
    'ccn': [16585, 3676, 21242, 14927, 24081],
    'co-analyzer': [22152, 5636, 3676, 14927, 24081],
    'nephelometer': [16585, 3676, 14927, 24081],
    'htdma': [16585, 3676, 14927, 24081],
    'ozone': [22152, 5636, 3676, 14927, 24081],
    'psap': [22152, 5636, 3676, 14927, 24081],
    'smps': [7941, 3676, 21408, 22737, 14927, 24081],
    'so2': [22152, 5636, 3676, 14927, 24081],
    'sp2': [7455, 3676, 14927, 24081],
    'uhsas': [16585, 3676, 14927, 24081],
    'ldis': [18499, 5536, 11, 22984],
    'disdrometer': [18499, 5536],
    'wb': [18499, 5536, 11, 22984],
    'met': [7820, 22594, 20087],
    'stamp': [7820, 22594, 20087, 18980, 20012],
    'sebs': [7820, 22594, 20087, 18980, 20012],
    'ecor': [7820, 22594, 20087, 18980, 20012],
    'ebbr': [7820, 22594, 20087, 18980, 20012],
    'maws': [20087, 7820],
    'sonde': [20087, 7820],
    'rwp': [16799],
    'mpl': [16799],
    'mwr': [6155],
    'mwr3c': [6155],
    'mwrhf': [6155],
    'mwrp': [6155],
    'gvr': [6155],
    'gvrp': [6155],
    'mfr': [5327, 18453],
    'mfrsr': [5327, 18453],
    'dl': [6914, 20548],
    'sirs': [12187, 8298, 5386, 23583],
    'skyrad': [12187, 8298, 5386, 23583],
    'gndrad': [12187, 8298, 5386, 23583],
    'brs': [12187, 8298, 5386, 23583],
}


dq_id = [20149, 5880, 20071]
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

"""
    QA Reason Codes
    5000 - Instrument
    5001 - Collection
    5002 - Transfer
    5003 - Environmental
    5004 - Processing
"""
qa_reason = [5004]

stat_line = []
#instrument = ['aps']
#for inst in instrument:
for inst in instrument_dict:
    mentor_id = instrument_dict[inst]
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
        if dqpr['dqprLocObj'][0]['site'] == 'nsa' and dqpr['dqprLocObj'][0]['instrument'] == 'ldis':
            continue
        if dqpr['dqprLocObj'][0]['site'] == 'mos':
            continue
        if dqpr['dqprStatus'] not in status:
            continue
        if dqpr['dqprQaReasonObj'][0]['qareason'] in qa_reason:
            continue
        sd = datetime.datetime.strptime(dqpr['dqprEntrydateStr'], '%Y-%m-%d %H:%M:%S')
        if dqpr['dqprStatus'] not in [3, 6]:
            continue

        ed = None
        for dqprStatusDict in dqpr['dqprStatusObj'][::-1]:
            if dqprStatusDict['status'] in [2, 3, 6]:
                ed = int(int(dqprStatusDict['dateset'])/1000)
                ed = datetime.datetime.utcfromtimestamp(ed)

        # If not end date, assume error in DB data (Ex: 12154)
        if ed is None:
            continue

        if (ed < dqpr_start) or (sd > dqpr_end):
            continue

        dqpr_number.append(dqpr['dqprNo'])
        dqpr_sd.append(sd)
        dqpr_ed.append(ed)
        dqpr_status.append(dqpr['dqprStatus'])
        dqpr_submitter.append(dqpr['personId'])

    # Get Comment History
    #dqpr_number = [11610]
    data = []
    no_mentor_comment = 0
    for i, d in enumerate(dqpr_number):
        mentor_submitted = False
        if dqpr_submitter[i] in mentor_id:
            mentor_submitted = True

        time_to_close = dqpr_ed[i] - dqpr_sd[i]
        query_url = 'http://armui-prod:8081/dqprapi/dq/comment/user/'
        query_url += str(d)

        response_body = urlopen(query_url).read().decode("utf-8")
        response_body_json = json.loads(response_body)

        # Find the first comment from the mentor team and record time to first comment
        ct = 0
        ping_ct = 0
        first_mentor = False
        time_to_first_comment = -9999
        for c in response_body_json:
            if first_mentor is False:
                if c['personId'] in mentor_id:
                    time_to_first_comment = (datetime.datetime.fromtimestamp(c['commentDate'] / 1000.) - dqpr_sd[i]).days
                    first_mentor = True
                else:
                    time_to_first_comment = -9999
                ct += 1
            if c['personId'] in dq_id:
                if 'ping' in c['comment'] or 'Ping' in c['comment']:
                    if 'mentor' in c['comment'] or 'Mentor' in c['comment']:
                        ping_ct += 1
        if (time_to_first_comment == -9999) and (int(time_to_close.days) > 14):
            no_mentor_comment += 1
        # DQPR No, Time to Close Out, Time to first mentor comment, comments between mentor comments, mentor submitted
        data.append([d, time_to_close.days, time_to_first_comment, ct, mentor_submitted, ping_ct])

    col = ['DQPR', 'Time-to-Close', 'First-Comment', 'Comments-to-Mentor', 'MentorSubmitted', 'PingCount']
    df = pd.DataFrame(data, columns=col)

    df = df.replace(-9999, np.nan)
    df2 = df[~df.MentorSubmitted]
    if verbose:
        print('\nStatistics for: ', inst)
        print('Dates: ', '-'.join([str(dqpr_start), str(dqpr_end)]))
        print('Number of DQPRs: ', len(dqpr_number))
        print('Number of DQPRs without Mentor Comment: ', no_mentor_comment)
        if len(dqpr_number) == 0:
            continue
        print('Days to Close (Avg/Min/Max): ', int(df.loc[:, 'Time-to-Close'].mean()),
            '/', df.loc[:, 'Time-to-Close'].min(), '/', df.loc[:, 'Time-to-Close'].max())
        print('DQ Pings (Avg/Max)', df.loc[:, 'PingCount'].mean(), int(df.loc[:, 'PingCount'].max()))

        print('\nExcluding Mentor Submitted DQPRs')
        print('-------------------------------')
        print('Number of DQPRs: ', len(df2.index))
        print('Days to First Comment (Avg/Min/Max): ', int(df2.loc[:, 'First-Comment'].mean()),
            '/', df2.loc[:, 'First-Comment'].min(), '/', df2.loc[:, 'First-Comment'].max())
        print('Comments before First Mentor Comment(Avg/Min/Max): ', int(df2.loc[:, 'Comments-to-Mentor'].mean()),
            '/', df2.loc[:, 'Comments-to-Mentor'].min(), '/', df2.loc[:, 'Comments-to-Mentor'].max())
    if len(dqpr_number) == 0:
        continue

    stat_line.append([inst, str(dqpr_start.date()), str(dqpr_end.date()), str(len(dqpr_number)),
        str(int(df.loc[:, 'Time-to-Close'].mean())),  str(int(df.loc[:, 'Time-to-Close'].median())),
        str(df.loc[:, 'Time-to-Close'].min()), str(df.loc[:, 'Time-to-Close'].max()),
        str(len(df2.index)), str(int(df2.loc[:, 'First-Comment'].mean())), str(int(df2.loc[:, 'First-Comment'].median())),
        str(df2.loc[:, 'First-Comment'].min()), str(df2.loc[:, 'First-Comment'].max()),
        str(int(df2.loc[:, 'Comments-to-Mentor'].mean())),
        str(df2.loc[:, 'Comments-to-Mentor'].min()), str(df2.loc[:, 'Comments-to-Mentor'].max()),
        str(df.loc[:, 'PingCount'].mean()), str(int(df.loc[:, 'PingCount'].max())), str(no_mentor_comment)])

for l in stat_line:
    print(','.join(l))
