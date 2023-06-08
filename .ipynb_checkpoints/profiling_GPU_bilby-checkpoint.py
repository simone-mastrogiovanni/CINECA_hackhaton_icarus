import os
import icarogw
import numpy as np
import h5py
from astropy.cosmology import FlatLambdaCDM
import time
from tqdm import tqdm
import sys
import bilby

Nev = 1
Nrep = 100
timing_flag = True

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
prior*=icarogw.conversions.source2detector_jacobian(data['injections/redshift'][()],cosmo_ref) # Add jacobian to convert prior in detector frame
# Prepare the input data
injections_dict={'mass_1':data['injections/mass1'][()],'mass_2':data['injections/mass2'][()],
                'luminosity_distance':data['injections/distance'][()],
                'right_ascension':data['injections/right_ascension'][()],'declination':data['injections/declination'][()]}
# Initialize the injections as usual
inj=icarogw.injections.injections(injections_dict,prior=prior,ntotal=data.attrs['total_generated'],Tobs=time_O3)
# Select injections with IFAR higher than 4yr
inj.cupyfy()
inj.update_cut(ifarmax>=4)
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

posterior_dict={}
for i in range(Nev):
    GW190814=h5py.File('GW190814_pubsamp.hdf5') # We load the PE release for GW190814

    # We extract all the data we need for GW190814
    ppd={'mass_1':GW190814['PE/mass_1'][:], # m1 in detector frame
        'mass_2':GW190814['PE/mass_2'][:], # m2 in detector frame
        'luminosity_distance':GW190814['PE/luminosity_distance'][:], # Luminosity distance in Mpc
        'right_ascension':GW190814['PE/right_ascension'][:], # right ascension in radians
        'declination':GW190814['PE/declination'][:]} # Declination in radians
    posterior_dict['GW'+str(i)]=icarogw.posterior_samples.posterior_samples(ppd,
                                                                             prior=np.power(GW190814['PE/luminosity_distance'][:],2.))
    posterior_dict['GW'+str(i)].pixelize(nside)
    posterior_dict['GW'+str(i)].cupyfy()
posterior_dict = icarogw.posterior_samples.posterior_samples_catalog(posterior_dict)

# Likelihood definition
likelihood=icarogw.likelihood.hierarchical_likelihood(posterior_dict,inj,rate_model,nparallel=5096,neffINJ=None,neffPE=20)


prior_dict = {'Om0':0.308,'alpha':3.78,'beta':0.81,'mmin':4.98,'mmax':112.5,'delta_m':4.8,'mu_g':32.27,'sigma_g':3.88,
                          'lambda_peak':0.03,'gamma':4.59,'kappa':2.86,'zp':2.47,'mmin_NS':1.,'mmax_NS':3.,'delta_m_NS':0.,
'H0':bilby.prior.Uniform(30,140)}

res = bilby.core.sampler.run_sampler(likelihood, priors=prior_dict, label='GPU', outdir='bilby_runs', sampler='dynesty',npool=1)
res.plot_corner()