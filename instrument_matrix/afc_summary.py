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
import argparse
import importlib
from scipy import stats
from matplotlib.dates import DateFormatter
from matplotlib.dates import HourLocator


def get_doi(site, dsname, c_start, c_end):
    # Get DOI Information from ARM's API
    doi_url = 'https://adc.arm.gov/citationservice/citation/inst-class?id=' + inst[ii] + '&citationType=apa'
    doi_url += '&site=' + site
    doi_url += '&dataLevel=' + dsname.split('.')[-1]
    doi_url += '&startDate=' + c_start
    doi_url += '&endDate=' + c_end
    doi = requests.get(url=doi_url).json()['citation']

    return doi


def get_metadata(ds):
    # Get Metadata Information, particularly the description
    metadata_url = 'https://adc.arm.gov/solr8/metadata/select?q=datastream%3A' + ds
    r = requests.get(url=metadata_url)
    response = r.json()['response']
    response = response['docs'][0]
    description = response['instrument_name_text']

    return description


def get_da(site, dsname, dsname2, t_delta, d):
    """
    Function to calculate data availability for a particular instrument

    Parameters
    ----------
    site : str
        ARM Site ID
    dsname : str
        Datastream name to use, minus site
    dsname2 : str
        Secondary datastream name to use, minus site
        For instance if dsname = dlfptM1.b1, dsname2 = dlppiM1.b1
    t_delta : float
        Pre-defined time delta to use, otherwise resample to 1 minute
    d : str
        Date to process DA for

    Returns
    -------
    dict
        returns a dictionary of data and time deltas to use for plotting

    """

    # Get files for particular day, defaults to archive area for now
    ds = site + dsname
    files = glob.glob('/data/archive/' + site + '/' + ds + '/' + ds + '*' + d + '*nc')
    if len(files) == 0:
        files = glob.glob('/data/archive/' + site + '/' + ds + '/' + ds + '*' + d + '*cdf')
    files = sorted(files)

    # Set time delta to 1 minute if not specified
    if t_delta is None:
        t_delta = 1

    # Read data for primary datastream
    if len(files) > 0:
        try:
            obj = act.io.armfiles.read_netcdf(files)
        except ValueError: 
            obj = act.io.armfiles.read_netcdf(files[0])
        obj = obj.sortby('time')
    else:
        obj = None

    # Read data for primary datastream
    if dsname2 is not None:
        ds2 = site + dsname2
        files2 = glob.glob('/data/archive/' + site + '/' + ds2 + '/' + ds2 + '*' + d + '*nc')
        if len(files2) == 0:
            files2 = glob.glob('/data/archive/' + site + '/' + ds2 + '/' + ds2 + '*' + d + '*cdf')
        files2 = sorted(files2)
        if len(files2) > 0:
            obj2 = act.io.armfiles.read_netcdf(files2, combine='nested', coords=['time'])
            obj2 = obj2.sortby('time')
            if obj is not None:
                obj = obj['time'].combine_first(obj2['time'])
                obj2.close()
            else:
                obj = obj2
    else:
        dsname2 = None

    # Set up dataframe with all expected times for day
    d0 = pd.to_datetime(d)
    d1 = d0 + dt.timedelta(days=1)
    d_range = pd.date_range(d0, d1, freq=str(t_delta) + 'T', closed='left')
    df1 = pd.DataFrame({'counts': np.zeros(len(d_range))}, index=d_range)

    # Join datasets with dataframe and where counts > 0 set to 100 for color
    if len(files) > 0:
        counts = obj['time'].resample(time=str(t_delta) + 'min').count().to_dataframe()
        data = df1.join(counts)
        data.loc[data['time'] > 0, 'time'] = 100
        r_data = np.nan_to_num(data['time'].tolist())
        obj.close()
    else:
        data = df1
        r_data = np.nan_to_num(data['counts'].tolist())

    return {'data': r_data, 't_delta': t_delta}


if __name__ == '__main__':
    """
    Main function to get information from configuration file and create DA plots

    Author : Adam Theisen
    """

    parser = argparse.ArgumentParser(description='Create campaign summary plots.')
    parser.add_argument('-c', '--conf', type=str, required=True,
                       help='Conf file to get information from')
    args = parser.parse_args()

    exec(open(args.conf).read())

    # Time trials
    now = pd.Timestamp.now()

    # Import Configuration File
    #rom conf.conf import conf
    site = conf['site']
    inst = list(conf['instruments'].keys())
    c_start = conf['start_date']
    c_end = conf['end_date']

    # Set date range for plots
    start = pd.to_datetime(c_start)
    end = pd.to_datetime(c_end)
    c_dates = pd.date_range(start, end + dt.timedelta(days=1), freq='d')
    c_dates = c_dates

    # Set up Plot
    nrows = len(inst)
    ncols = 3
    fig = plt.figure(figsize=(10, 1.5 * nrows), constrained_layout=True)
    gs = fig.add_gridspec(nrows, ncols)

    # Process each instrument
    for ii in range(len(inst)):
        dsname = conf['instruments'][inst[ii]]['dsname']
        ds = conf['site'] + dsname
        print(ds)
        dsname2 = None
        ds2 = None
        if 'dsname2' in conf['instruments'][inst[ii]]:
            dsname2 = conf['instruments'][inst[ii]]['dsname2']
            ds2 = site + dsname2

        t_delta = None
        if 't_delta' in conf['instruments'][inst[ii]]:
            t_delta = conf['instruments'][inst[ii]]['t_delta']

        workers = None
        if 'workers' in conf['instruments'][inst[ii]]:
            workers = conf['instruments'][inst[ii]]['workers']
       
        # Dask loop for multiprocessing
        # workers should be set to 1 in the conf file for radars 
        task = []
        for jj, d in enumerate(c_dates):
            #task.append(get_da(site, dsname, dsname2, t_delta, d.strftime('%Y%m%d')))
            task.append(dask.delayed(get_da)(site, dsname, dsname2, t_delta, d.strftime('%Y%m%d')))
        results = dask.compute(*task, num_workers=workers)

        img = [list(r['data']) for r in results]
        t_delta = int(stats.mode([r['t_delta'] for r in results])[0][0])

        # Get DOI Information
        doi = get_doi(site, dsname, c_start, c_end)
        description = get_metadata(ds)

        # Add Subplot and start adding text
        # Just text on this plot
        ax0 = fig.add_subplot(gs[ii, 0])
        ax0.set_frame_on(False)
        ax0.get_xaxis().set_visible(False)
        ax0.get_yaxis().set_visible(False)
        fs = 8
        ax0.text(0, 0.9, '\n'.join(textwrap.wrap(description, width=45)), size=fs)
        ax0.text(0, 0.8, 'ARM Name: ' + inst[ii].upper(), size=fs)
        ds_str = ds
        doi_y = 0.6
        if dsname2 is not None:
            ds_str += ', ' + ds2
            if len(ds_str) > 45:
               doi_y -= 0.05 * np.floor(len(ds_str)/45)
            ds_str = '\n'.join(textwrap.wrap(ds_str, width=45))
            
        ax0.text(0, 0.7, 'Datastream: ' + ds_str, size=fs)
        ax0.text(0, doi_y, '\n'.join(textwrap.wrap(doi, width=45)), va='top', size=fs)

        # Plot out the DA on the right plots
        ax1 = fig.add_subplot(gs[ii, 1:])
        y = pd.date_range(start, start + dt.timedelta(days=1), freq=str(t_delta) + 'T', closed='left')
        ax1.pcolormesh(c_dates, y, np.transpose(img), vmin=0, cmap='Blues', shading='flat')
        ax1.yaxis.set_major_locator(HourLocator(interval=6))
        ax1.yaxis.set_major_formatter(DateFormatter('%H:%M'))
        ax1.set_xlim([pd.to_datetime(c_start), pd.to_datetime(c_end) + pd.Timedelta('1 days')])

    ext = 'png'
    if 'outname' in conf:
        filename = conf['outname']
    plt.savefig(filename)
    print(pd.Timestamp.now() - now)
