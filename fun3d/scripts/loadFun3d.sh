#!/bin/bash

# This script does everything needed to run FUN3D

# Unload conflicting modules
# By default Topaz loads compiler/intel/16.0.0 and mpi/sgimpt/2.13-11280
# We need to load the versions we compiled FUN3D with
# These unload anything that matches a part
module unload mpi compiler

# Load required modules
module load mpi/intelmpi/15.0.3
module load fun3d/fun3d-12.9-0555546-clarey-v0_test/intel-15.0.3--intel-mpi-15.0.3
