import act
import smtplib
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from textwrap import wrap
import datetime as dt
import glob
import dask
import os
import matplotlib.pyplot as plt
import numpy as np


def send_alert(body):
    if len(body) > 0:
        msg_root = MIMEMultipart('related')
        msg_root['Subject'] = 'CSU Radar Status Update'
        msg_root['From'] = 'dqmgr@arm.gov'
        msg_root['To'] = 'atheisen@anl.gov,zsherman@anl.gov'
        #msg_root['To'] = 'atheisen@anl.gov'
        msg_root.preamble = 'This is a multi-part message in MIME format.'
        msg_text = MIMEText(body, 'html')
        encoders.encode_base64(msg_text)
        msg_root.attach(msg_text)
        server = smtplib.SMTP("localhost")
        server.sendmail('dqmgr@arm.gov', 'atheisen@anl.gov', msg_root.as_string())
        server.quit()


def proc_radar_data(f):
    f_comp = f.split('.')
    scan = f_comp[-2][-3:]
    obj = act.io.armfiles.read_netcdf(f)
    time = obj['time'].values[0]
    dbz_max = float(obj['DBZ'].max())

    return [time, scan, dbz_max]


def email_status():
    status_file = '/home/theisen/www/sail_radar/email.txt'
    status = False
    files = glob.glob(status_file)
    if len(files) > 0:
        status = True

    return status 

if __name__ == '__main__':
    today = dt.date.today().strftime("%Y%m%d")
    yesterday = (dt.date.today() - dt.timedelta(days=1)).strftime("%Y%m%d")
    now = dt.datetime.now()
    ago = now-dt.timedelta(minutes=20)
    fdate = today
    email = False
    e_status = email_status()
    body = ''

    files = glob.glob('/data/datastream/guc/gucxprecipradarS2.00/*csu.sail-' + today + '*')
    yfiles = glob.glob('/data/datastream/guc/gucxprecipradarS2.00/*csu.sail-' + yesterday + '*')
    if len(files) == 0 and now.hour < 3:
        files += yfiles
    files.sort()
    collection_files = glob.glob('/data/collection/guc/gucxprecipradarS2.00/*' + today +'*')
    transfer_files = glob.glob('/data/transfer/incoming_from/collector-amfc2.amf.arm.gov/collection/S2/gucxprecip*' + today + '*')

    if len(files) == 0:
        body += 'Current Time: ' + str(now) + '</br>No Files Found for Today: ' + today + '</br>'
        if len(collection_files) > 0:
            body += '</br>' + str(len(collection_files)) + ' Files are in /data/collections'
        if len(transfer_files) > 0:
            body += '</br>' + str(len(transfer_files)) + ' Files are in /data/transfer'
        body += '</br>'

    if len(files) > 0:
        mtime = (now - dt.datetime.fromtimestamp(os.path.getmtime(files[-1]))).total_seconds()
        if mtime > 3. * 60. * 60.:
            body += 'Current Time: ' + str(now) + '</br>No new files in 3 hours</br> ' + files[-1] + '</br>'
            if len(collection_files) > 0:
                body += '</br>' + str(len(collection_files)) + ' Files are in /data/collection'
            else:
                body += '</br>No files in /data/collection'
            if len(transfer_files) > 0:
                body += '</br>' + str(len(transfer_files)) + ' Files are in /data/transfer'
            else:
                body += '</br>No files in /data/transfer'

    if len(body) > 0:
        if e_status is False:
            send_alert(body)
        email = True

    if len(files) > 0:
        task = []
        for f in files:
            task.append(dask.delayed(proc_radar_data)(f))
        results = dask.compute(*task)

        time = []
        scan = []
        dbz = []
        for r in results:
            time.append(r[0])
            scan.append(r[1])
            dbz.append(r[2])

        dbz = np.array(dbz)
        time = np.array(time)
        print((dt.datetime.now()-now).total_seconds())
        scan_num = np.zeros(len(scan))
        ppi = np.where(np.array(scan) == 'PPI')
        rhi = np.where(np.array(scan) == 'RHI')
        scan_num[ppi] = 1
        scan_num[rhi] = 2

        fig, axs = plt.subplots(2, figsize=(12,8))
        axs[0].plot(time[ppi], dbz[ppi], label='PPI')
        axs[0].plot(time[rhi], dbz[rhi], label='RHI')
        axs[0].legend()
        axs[0].set_title('Maximum Zh in Each File')
        axs[1].plot(time, scan_num, '|')
        axs[1].set_title('Scan Type')
        axs[1].set_yticks((1,2))
        axs[1].set_yticklabels(['PPI', 'RHI'])
        directory = '/home/theisen/www/sail_radar/status_plot/'
        if not os.path.exists(directory):
            os.makedirs(directory)
        plt.savefig(directory + '/gucxprecipradarS2.00.' + str(today) + '.000000.png',bbox_inches='tight')
        plt.close(fig=fig)

        if np.nanmax(dbz) < 0:
            body = 'Reflectivity drops out https://dev.arm.gov/~theisen/sail_radar/status_plot/gucxprecipradarS2.00.' + str(today) + '.000000.png'
            if e_status is False:
                send_alert(body)
            email = True

    email_file = '/home/theisen/www/sail_radar/email.txt'
    if email:
        with open(email_file, 'w') as fp:
            fp.write('Email sent')
            pass
    else:
        try:
            os.remove(email_file)
        except OSError:
            pass
    print('Process completed')
