import act
import matplotlib.pyplot as plt

sonde_ds = act.io.armfiles.read_netcdf('/data/archive/sgp/sgpsondewnpnC1.b1/sgpsondewnpnC1.b1.20210201.173000.cdf')

# Calculate stability indicies
sonde_ds = act.retrievals.calculate_stability_indicies(
    sonde_ds, temp_name="tdry", td_name="dp", p_name="pres")
print(sonde_ds["lifted_index"])

# Set up plot
skewt = act.plotting.SkewTDisplay(sonde_ds, figsize=(15, 10))

# Add data
skewt.plot_from_u_and_v('u_wind', 'v_wind', 'pres', 'tdry', 'dp')
sonde_ds.close()
plt.savefig('/home/theisen/www/sounding_example_act.png', format='png', dpi=300)
