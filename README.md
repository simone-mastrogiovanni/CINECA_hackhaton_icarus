# Software set up for the Hackhaton

Follow the next steps to install and run icarogw for the Hackhaton on the Marconi 100 cluster.

Once logged in on the clusters

```
module load python/3.8.2
python3 -m venv icarogw
source icarogw/bin/activate
```

```
pip install git+https://github.com/simone-mastrogiovanni/icarogw.git@CINECA_hackhaton_2023
```

```
conda install -c conda-forge gprof2dot
```

```
conda install -c anaconda graphviz
```

```
conda install -c conda-forge cupy==12.0
```

# Get the data for the Hackhaton

Simply clone this repository

# Work on icarogw for the Hackhaton

If you plan to modify icarogw, please ask Simone Mastrogiovanni (mastrosi@roma1.infn.it) to add you as a developer for [this branch](https://github.com/simone-mastrogiovanni/icarogw/tree/CINECA_hackhaton_2023)





