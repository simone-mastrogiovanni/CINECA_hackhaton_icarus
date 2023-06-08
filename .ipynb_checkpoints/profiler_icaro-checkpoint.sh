#!/bin/bash -e

# This script was created by sebastian Gomez Lopez, Simone Mastrogiovanni and Adriano Frattale Mascioli
# to participate in the CINECA GPU Open Hackathon 2023. 
#
# The following code makes the profiling of icarogw and visualizes its results using gprof2dot.

# To run it, you must have a conda environment with icarogw, bilby, gprof2dot, and graphviz installed.
# the seaborn, and progressbar dependencies must be fulfilled too.


echo
echo "To run this script you must use:"
echo "./profiler_icaro <input path> <output path>"
echo 
echo "input_path -> path to folder containing"
echo " injection file & posterior sample files" 
echo
echo "output_path -> output folder"

test_out=out
script="$1"
cpu=$(lscpu | grep 'Model name' | cut -f 2 -d ":" | awk '{$1=$1}1')
gpu=$(nvidia-smi --query-gpu=name --format=csv,noheader,nounits)

if [ ! -d "$test_out" ]; then
    mkdir -p "$test_out"
    echo "Directory created: $test_out"
fi

chmod u+rw "$test_out"

echo "${cpu}" >| ${test_out}/time_${script}.txt
echo "${gpu}" >| ${test_out}/time_${script}.txt
echo "# execution time[seconds]" >> ${test_out}/time_${script}.txt

SECONDS=0
echo
echo -e "\\n\\n>> [`date`] executing MCMC population analysis"
python -m cProfile -o ${test_out}/profile_${script}.out  ${script} "$@"
echo "${SECONDS}" >> ${test_out}/time_${script}.txt


echo
echo -e "\\n\\n>> [`date`] generating profile map"
python -m gprof2dot -f pstats ${test_out}/profile_${script}.out | dot -Tpng > ${test_out}/profile_${script}.png

