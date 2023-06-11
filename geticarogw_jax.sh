conda env create -f environment_jax.yml --name icarogwjax
conda activate icarogwjax
pip install --upgrade pip
pip install git+https://github.com/simone-mastrogiovanni/icarogw.git@jax_comparison
pip install --upgrade "jax[cuda11_pip]" -f https://storage.googleapis.com/jax-releases/jax_cuda_releases.html
