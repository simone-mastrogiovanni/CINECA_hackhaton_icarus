# Conda set up on M100 clusters

After you are logged in on the m100 cluster

```
module load anaconda/2020.11
```

Then you can source conda in your shell by running

```
echo ". /cineca/prod/opt/tools/anaconda/2020.11/none/etc/profile.d/conda.sh" >> ~/.bashrc
```

You just need to run the previous lines once. The next time you are going to open your shell conda will be automatically sourced.

# Get icarogw software and data

Once you have your conda set up on m100, you will need to clone this repository

```
git clone https://github.com/simone-mastrogiovanni/CINECA_hackhaton_icarus.git
```

Enter in the cloned repository. To install icarogw you can run the file

```
./geticarogw.sh
```

After you installed icarogw, you might neeed to

```
conda activate icarogw
```

To get the data inputs you need run 

```
./getdata.sh
```

You are ready to run icarogw. Try to run the script `profiler_CPU.py` or `profiler_GPU.py` and see if it is working.

