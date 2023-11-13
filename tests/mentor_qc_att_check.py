import act
import glob


sites = ['sgp']
data_dir = '/data/archive/'

for i, s in enumerate(sites):
    ds = s + '*.b1'
    dirs = glob.glob(data_dir + s + '/' + ds)
    dirs.sort()
    for d in dirs:
        files = glob.glob(d + '/*')[0:10]
        files.sort()
        for f in files:
            try:
                ds = act.io.armfiles.read_netcdf(f)
            except:
                break
            if 'Mentor_QC_Field_Information' in ds.attrs:
                print(f, len(ds.attrs['Mentor_QC_Field_Information']), 'Basic mentor QC checks' in ds.attrs['Mentor_QC_Field_Information'])
                break
