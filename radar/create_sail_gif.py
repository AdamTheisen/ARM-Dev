import glob
import imageio


dirs = glob.glob('/home/theisen/www/sail_radar/*')
for d in dirs:
    filenames = glob.glob(d+'/*png')
    #images = []
    #for filename in filenames:
    #    images.append(imageio.imread(filename))
    title = d +'/ppi_1_gif'
    #imageio.mimsave(title, images, format='png')

    with imageio.get_writer(title, mode='I') as writer:
        for filename in filenames:
            image = imageio.imread(filename, format='png')
            writer.append_data(image)
