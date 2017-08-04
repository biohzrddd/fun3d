#!/bin/bash

function fun3d_run() {

# Run fun3d
outputFile='sim.out'
mpirun \
  --np ${BC_MPI_TASKS_ALLOC} \
  --hostfile hosts \
  nodet_mpi \
  >& ${outputFile}

}

function fun3d_sequence() {
# This function runs fun3d in sequence based on namelist availability
#
# Good for running a set of runs you know need to be in order but must
# change the namelist file between runs (e.g. to switch between 2 to 5 species)
#
# Assumes a few things:
# - You want any existing files untouched at the start
# - It's OK for FUN3D to modify them when running
# - You have files sequenced via the following method in your directory
#   where X can be any starting number, zero padded if needed.
#      fun3d.nml.X
#      ...
#      fun3d.nml.Y
# 
# Expected inputs:
#       numProcess - (Default:1) Number to pass to mpirun -np option
#       hostFile   - (Default:hosts) File to pass to mpirun --hostfile option


# Process inputs
if [ -z "$1" ]; then
    numProcess=$1
else
    numProcess=1
fi

if [ -z "$2" ]; then
    hostFile=$2
else
    hostFile='hosts'
fi

# Find fun3d.nml.XX in pwd
fun3dInputFiles=$(ls *.nml.* | sort)

# Count them
numInputFiles=$(wc -l $fun3dInputFiles)

# Loop over them
for inputFile in $fun3dInputFiles; do
    # Copy fun3d.nml.X to fun3d.nml
    cp $inputFile fun3d.nml
    
    # Grab X off fun3d.nml.X
    # ${variable##pattern}
    #    Trim the longest match from the beginning 
    X=${inputFile##*.}
    
    # Copy output files that can be modified/overwritten by fun3d to a folder
    # FUN3D_Manual-12.9.pdf Ch 5.3 Output Files
    newFolder=run$X
    mkdir $newFolder
    cp --preserve ./{*.flow,*_hist.dat,*_subhist.dat,*.forces} $newFolder/.

    # Copy output file we made
    cp --preserve ./$outputFile $newFolder/.
done

}

