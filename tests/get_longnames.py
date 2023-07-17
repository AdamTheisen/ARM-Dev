import act
import glob

ds = {
    'gucaosnephdry1mM1.b1': ['Bbs_B_Dry_Neph3W', 'Bbs_G_Dry_Neph3W', 'Bbs_R_Dry_Neph3W', 'Bs_B_Dry_Neph3W',
                           'Bs_B_Dry_Neph3W_raw', 'Bs_G_Dry_Neph3W', 'Bs_G_Dry_Neph3W_raw', 'Bs_R_Dry_Neph3W',
                           'Bs_R_Dry_Neph3W_raw', 'P_Neph_Dry', 'RH_Neph_Dry', 'T_Neph_Dry', 'impactor_state'],
    'gucaospsap3w1mM1.b1': ['Ba_B_Weiss', 'Ba_B_raw', 'Ba_G_Weiss', 'Ba_G_raw', 'Ba_R_Weiss', 'Ba_R_raw',
                            'impactor_state', 'sample_flow_rate', 'transmittance_blue', 'transmittance_green',
                            'transmittance_red'],
    'epcaosapsM1.b1': ['dN_dlogDp', 'total_N_conc'],
    'gucaossmpsM1.b1': ['dN_dlogDp', 'total_N_conc', 'diameter_mobility', 'diameter_mobility_bounds'],
    'gucaosccn2colaavgM1.b1': ['N_CCN', 'N_CCN_dN', 'aerosol_number_concentration', 'base_time', 'droplet_size',
                               'droplet_size_bounds', 'setpoint', 'supersaturation_calculated', 'time_offset']
}

for d in ds:
    site = d[:3]
    files = glob.glob('/data/archive/'+site+'/'+d+'/*')

    obj = act.io.armfiles.read_netcdf(files[0])
    for v in ds[d]:
        print(d, ';', v, ';', obj[v].attrs['long_name'])
