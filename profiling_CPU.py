import os
f = open("config.py", "w")
f.write('CUPY=False')
f.close()
import icarogw
import numpy as np
import h5py
from astropy.cosmology import FlatLambdaCDM
import time
from tqdm import tqdm
import sys
from icarogw.cupy_pal import *
os.remove('config.py')

Ntot = [5e4,1e5,5e5,1e6,5e6]
Nsamples = 5000
Nrep = 100
Ninj = 10000
timing_flag = 'timing/CPU.txt'

# Again we need to tell icarogw what reference cosmology was used to build the catalog
cosmo_ref=icarogw.cosmology.astropycosmology(zmax=10.)
cosmo_ref.build_cosmology(FlatLambdaCDM(H0=67.7,Om0=0.308))
cat = icarogw.catalog.galaxy_catalog()
# Load the galaxy catalog telling also the luminosity weight used
cat.load_hdf5('glade+_kband_lum1.hdf5',cosmo_ref,epsilon=1.)

nside =64

# For this check we will use NSBH injections from the R&P group
data=h5py.File('endo3_nsbhpop-LIGO-T2100113-v12.hdf5')
# We select the maximum IFAR among the searches
ifarmax=np.vstack([data['injections'][key] for key in ['ifar_cwb', 'ifar_gstlal', 'ifar_mbta', 'ifar_pycbc_bbh', 'ifar_pycbc_hyperbank']])
ifarmax=np.max(ifarmax,axis=0)

time_O3 = (28519200/86400)/365 # Time of observation for O3 in tr
# The prior for this injection set is saved in source frame
prior=data['injections/mass1_source_mass2_source_sampling_pdf'][()]*data['injections/redshift_sampling_pdf'][()]/(np.pi*4) # Add prior on sky angle (isotropic)
prior*=cp2np(icarogw.conversions.source2detector_jacobian(np2cp(data['injections/redshift'][()]),cosmo_ref)) # Add jacobian to convert prior in detector frame
# Prepare the input data
injections_dict={'mass_1':data['injections/mass1'][()][:Ninj],'mass_2':data['injections/mass2'][()][:Ninj],
                'luminosity_distance':data['injections/distance'][()][:Ninj],
                'right_ascension':data['injections/right_ascension'][()][:Ninj],'declination':data['injections/declination'][()][:Ninj]}
# Initialize the injections as usual
inj=icarogw.injections.injections(injections_dict,prior=prior[:Ninj],ntotal=data.attrs['total_generated'],Tobs=time_O3)
# Select injections with IFAR higher than 4yr
inj.cupyfy()
inj.update_cut(ifarmax[:Ninj]>=4)
# Pixelize the injections
inj.pixelize(nside=nside)

# Wrappers definition
cosmo_wrap=icarogw.wrappers.cosmology_wrappers_init('FlatLambdaCDM',zmax=2.)
mass_wrap=icarogw.wrappers.mass_wrappers_init('PowerLawPeak_NSBH')
rate_wrap=icarogw.wrappers.rate_wrappers_init('Madau')
# Rate definition
rate_model = icarogw.wrappers.CBC_catalog_vanilla_rate(cat,cosmo_wrap,
                                                       mass_wrap,rate_wrap,
                                                       average=True, # This flag tells you that you want to use a sky-averaged 
                                                       #detection probability to evaluate selection biases
                                                       scale_free=True)

if timing_flag is not None:
    fp=open(timing_flag,'w')

for nt in Ntot:
    Nev=int((nt-Ninj)/Nsamples)
    posterior_dict={}
    for i in range(Nev):
        GW190814=h5py.File('GW190814_pubsamp.hdf5') # We load the PE release for GW190814
        # We extract all the data we need for GW190814
        ppd={'mass_1':GW190814['PE/mass_1'][:Nsamples], # m1 in detector frame
          'mass_2':GW190814['PE/mass_2'][:Nsamples], # m2 in detector frame
         'luminosity_distance':GW190814['PE/luminosity_distance'][:Nsamples], # Luminosity distance in Mpc
         'right_ascension':GW190814['PE/right_ascension'][:Nsamples], # right ascension in radians
         'declination':GW190814['PE/declination'][:Nsamples]} # Declination in radians
        posterior_dict['GW'+str(i)]=icarogw.posterior_samples.posterior_samples(ppd,
                                                                             prior=np.power(GW190814['PE/luminosity_distance'][:Nsamples],2.))
        posterior_dict['GW'+str(i)].pixelize(nside)
        posterior_dict['GW'+str(i)].cupyfy()
    posterior_dict = icarogw.posterior_samples.posterior_samples_catalog(posterior_dict)

    # Likelihood definition
    likelihood=icarogw.likelihood.hierarchical_likelihood(posterior_dict,inj,rate_model,nparallel=Nsamples,neffINJ=-1,neffPE=-1)

    timing=np.zeros(Nrep)
    for i in tqdm(range(Nrep)):
        likelihood.parameters={'Om0':0.308,'alpha':3.78,'beta':0.81,'mmin':4.98,'mmax':112.5,'delta_m':4.8,'mu_g':32.27,'sigma_g':3.88,
                              'lambda_peak':0.03,'gamma':4.59,'kappa':2.86,'zp':2.47,'mmin_NS':1.,'mmax_NS':3.,'delta_m_NS':0.,'H0':67.7}
        start=time.time()
        _=likelihood.log_likelihood()
        end=time.time()
        timing[i]=end-start

    if timing_flag:
        fp.write('{:e}\t{:e}\t{:e}\n'.format(nt,np.median(timing),np.std(timing)))

fp.close()
