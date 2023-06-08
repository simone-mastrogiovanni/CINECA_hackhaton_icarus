import icarogw
from astropy.cosmology import FlatLambdaCDM
# Again we need to tell icarogw what reference cosmology was used to build the catalog
cosmo_ref=icarogw.cosmology.astropycosmology(zmax=10.)
cosmo_ref.build_cosmology(FlatLambdaCDM(H0=67.7,Om0=0.308))
 


