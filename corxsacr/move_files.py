import glob
import os
import shutil
import sys

files = glob.glob('./images/*png')

dates = [f.split('.')[-3] for f in files]

base_dir = '/data/home/theisen/plot/cor/corxsacr'
for d in dates:
    pdir = base_dir+'/'+d+'/'
    if os.path.isdir(pdir) is False:
        os.mkdir(pdir)
   
    sfiles = glob.glob('./images/*'+d+'*') 
    [shutil.move(sf, pdir) for sf in sfiles]
