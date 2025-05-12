import glob
import act

dates = act.utils.dates_between('20250427', '20250503')
files = []
radar = 'bnfcsapr2'
for d in dates:
    files += glob.glob('/data/www/tool/dq/bnf/'+radar+'/'+ d.strftime('%Y%m%d') + '/images/*ppi*')

print('Processing')
filename = '/data/www/userplots/theisen/bnfcsaprmovie/'+radar+'_ppi_'+dates[0].strftime('%Y%m%d')+ '_'+dates[-1].strftime('%Y%m%d')+'.mp4'
result = act.utils.generate_movie(files, write_filename=filename, fps=30, codec='libx264')
