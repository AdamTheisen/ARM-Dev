import act
import requests
import json 
import glob
import pandas as pd
import datetime as dt
import numpy as np
import xarray as xr
import dask
import matplotlib.pyplot as plt
import textwrap
from matplotlib.dates import DateFormatter
from matplotlib.dates import HourLocator


def get_doi(site, dsname, c_start, c_end):
    # Get DOI Information
    doi_url = 'https://adc.arm.gov/citationservice/citation/inst-class?id=' + inst[ii] + '&citationType=apa'
    doi_url += '&site=' + site
    doi_url += '&dataLevel=' + dsname.split('.')[-1]
    doi_url += '&startDate=' + c_start
    doi_url += '&endDate=' + c_end
    doi = requests.get(url=doi_url).json()['citation']

    return doi


def get_metadata(ds):
    metadata_url = 'https://adc.arm.gov/solr8/metadata/select?q=datastream%3A' + ds
    r = requests.get(url=metadata_url)
    response = r.json()['response']
    response = response['docs'][0]
    description = response['instrument_name_text']

    return description

if __name__ == '__main__':
    now = pd.Timestamp.now()
    # Import Configuration File
    from anx_conf import conf
    site = conf['site']
    inst = list(conf['instruments'].keys())
    c_start = conf['start_date']
    c_end = conf['end_date']

    nrows = len(inst)
    ncols = 3
    fig = plt.figure(figsize=(10, 1.5 * nrows), constrained_layout=True)
    gs = fig.add_gridspec(nrows, ncols)

    for ii in range(len(inst)):
        dsname = conf['instruments'][inst[ii]]['dsname']
        ds = site + dsname

        files = glob.glob('/data/archive/' + site + '/' + ds + '/' + ds + '*nc')
        if len(files) == 0:
            files = glob.glob('/data/archive/' + site + '/' + ds + '/' + ds + '*cdf')
        files = sorted(files)

        obj = act.io.armfiles.read_netcdf(files, parallel=True)

        if 'dsname2' in conf['instruments'][inst[ii]]:
            dsname2 = conf['instruments'][inst[ii]]['dsname2']
            ds2 = site + dsname2
            files2 = glob.glob('/data/archive/' + site + '/' + ds2 + '/' + ds2 + '*nc')
            if len(files2) == 0:
                files2 = glob.glob('/data/archive/' + site + '/' + ds2 + '/' + ds2 + '*cdf')
            files2 = sorted(files2)
            obj2 = act.io.armfiles.read_netcdf(files2, parallel=True, concat_dim=['time'], combine='nested')
            obj = xr.merge([obj, obj2])
            obj2.close()
        else:
            dsname2 = None

        if 'override_delta' in conf['instruments'][inst[ii]]:
            t_delta = conf['instruments'][inst[ii]]['override_delta']
        else:
            t_delta = act.utils.determine_time_delta(obj['time'].values, default=60.)/60

        print(ds, t_delta, int(1440/t_delta), 1440/t_delta)

        start = pd.to_datetime(obj['time'].values[0]).floor('D')
        end = pd.to_datetime(obj['time'].values[-1]).floor('D')
        dates = pd.date_range(start, end + dt.timedelta(days=1), freq='d')

        obj['date'] = xr.DataArray(obj.time.dt.floor('D'), coords=obj.time.coords)

        groups = obj.groupby('date').groups
        group_names = list(groups.keys())

        img = np.zeros([int(np.ceil(1440/t_delta)), len(dates)])
        date_list = []
        for i, d in enumerate(group_names):
            d_obj = obj['time'].isel(time=groups[d])
            d0 = pd.to_datetime(d_obj['time'].values[0]).floor("D")
            date_list.append(d0)
            d1 = d0 + dt.timedelta(days=1)
            print(t_delta)
            d_range = pd.date_range(d0, d1, freq=str(t_delta) + 'T', closed='left')

            df1 = pd.DataFrame({'counts': np.zeros(len(d_range))}, index=d_range)
            counts = d_obj.resample(time=str(t_delta) + 'min').count().to_dataframe()
            data = df1.join(counts)
            data.loc[data['time'] > 0, 'time'] = 100

            idx = np.where(dates == d0)[0]
            img[:, idx[0]] = data['time'].tolist()
            d_obj.close()

        img = np.nan_to_num(img)

        # Get DOI Information
        doi = get_doi(site, dsname, c_start, c_end)
        description = get_metadata(ds)

        ax0 = fig.add_subplot(gs[ii, 0])
        ax0.set_frame_on(False)
        ax0.get_xaxis().set_visible(False)
        ax0.get_yaxis().set_visible(False)
        fs = 8
        ax0.text(0, 0.9, '\n'.join(textwrap.wrap(description, width=45)), size=fs)
        ax0.text(0, 0.8, 'ARM Name: ' + inst[ii].upper(), size=fs)
        ds_str = ds
        if dsname2 is not None:
            ds_str += ', ' + ds2
        ax0.text(0, 0.7, 'Datastream: ' + ds_str, size=fs)
        ax0.text(0, 0.6, '\n'.join(textwrap.wrap(doi, width=45)), va='top', size=fs)

        ax1 = fig.add_subplot(gs[ii, 1:])
        ax1.pcolormesh(dates, d_range, img, vmin=1, cmap='Blues', shading='flat')
        ax1.yaxis.set_major_locator(HourLocator(interval=6))
        ax1.yaxis.set_major_formatter(DateFormatter('%H:%M'))
        ax1.set_xlim([pd.to_datetime(c_start), pd.to_datetime(c_end) + pd.Timedelta('1 days')])

        obj.close()

    plt.savefig('/home/theisen/www/test.png')
    print(pd.Timestamp.now() - now)
