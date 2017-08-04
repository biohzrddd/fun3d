#!/usr/bin/env python

import os

from fun3d import Pbs
from fun3d import Fun3d

# Sets up everything needed to run an mpirun out of a working directory
p = Pbs(hostFile='', startDir='')
p.runSetup()

# Send info off to Fun3d to run
f = Fun3d(numProcess=p.numProcess,
          hostFile=p.hostFile,
          outputFile='sim.out',
          startDir=p.startDir,
          useMpirun=True,
          requiredModules=[''])
f.runSequence()
