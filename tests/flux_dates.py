import glob
import act

dirs = glob.glob('/data/archive/sgp/sgp5ebbr*b1*')
dirs.sort()
for d in dirs:
    files = glob.glob(d + '/*')
    files.sort()
    obj = act.utils.DatastreamParserARM(files[0])
    e_obj = act.utils.DatastreamParserARM(files[-1])
    print(obj.site, obj.facility, obj.date, e_obj.date)
