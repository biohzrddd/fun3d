
class Fun3d:
    """Class to setup fun3d runs in various ways"""

    # class variables shared by all instances
    inputName = 'fun3d.nml'

    # Stuff for running "module load blah" from within python env
    moduleExe = '/usr/bin/modulecmd'

    def __init__(self, numProcess=1, hostFile='hosts', outputFile='sim.out', startDir='', useMpirun=True,
                 requiredModules=['']):
        """
        Initialize Fun3d object with sane defaults.

        Args:
              numProcess - Number to pass to mpirun -np option
              hostFile   - File to pass to mpirun --hostfile option
              outputFile - stdout Output from mpirun nodet_mpi call
              startDir   - Directory to start run in. Leave empty for pwd
              useMpirun  - True to use mpirun before exe
              requiredModules - List of strings containing module file names to load
        """

        # instance variables unique to each instance
        import os
        import platform

        import utils

        # Set modules required depending on network
        if requiredModules.count() == 1 and requiredModules[0] == '':
            # No input, automatically set
            network = utils.detectLocation()
            if network == 'afit':
                self.requiredModules = [
                    'intel2015',
                    'openmpi/intel2015/openmpi-2.0.1',
                    'fun3d/openmpi-2.0.1/intel2015/fun3d-12.9-0555546-clarey'
                    ]
            elif network == 'topaz':
                self.requiredModules = [
                    'mpi/intelmpi/15.0.3',
                    'fun3d/fun3d-12.9-0555546-clarey-v0_test/intel-15.0.3--intel-mpi-15.0.3'
                    ]
            else:
                self.requiredModules = []
        else:
            # User input modules, use them
            self.requiredModules = requiredModules

        self.numProcess = numProcess
        self.hostFile = hostFile
        self.outputFile = outputFile
        if startDir == '':
            startDir = os.getcwd()
        self.startDir = startDir
        self.useMpirun = useMpirun

        # Get path stuff going so we can run right away
        self.setupFun3dPath()

    def setupFun3dPath(self):
        """ Load required modules to get everything on the path """
        import os

        # Clear out any existing modules
        cmd = os.popen(self.moduleExe, ' python purge')

        # Load up required modules
        for mod in self.requiredModules:
            cmd = os.popen(self.moduleExe + ' python load ' + mod)
            try:
                exec (cmd)
            finally:
                pass

    def run(self):
        """Run FUN3D via mpirun"""
        import subprocess

        import utils

        # (Selectively) Copy from submit folder to run folder
        filePatterns = [
            '*lines*',
            'fun3d.nml*', # To account for fun3d.nml.1 ... fun3d.nml.N
            '*.sh',
            'tdata',
            '*.flow',
            '*.ugrid',
            '*.mapbc',
            '*.partitioning',
            ]
        utils.copyFilesOfPattern(filePatterns, self.startDir, self.runDir)

        # Go into the run folder
        os.chdir(self.runDir)

        # Run fun3d
        if self.useMpirun:
            subprocess.Popen([
                'mpirun',
                '--np ' + str(self.numProcess),
                '--hostfile ' + self.hostFile,
                'nodet_mpi'
                ], stdout=self.outputFile)
        else:
            subprocess.Popen([
                'nodet_mpi'
                ], stdout=self.outputFile)

    def runSequence(self):
        """
        This function runs FUN3d in sequence based on namelist availability

        Good for running a set of runs you know need to be in order but must
        change the namelist file between runs (e.g. to switch between 2 to 5 species)

        Assumes a few things:
        - You want any existing files untouched at the start
        - It's OK for FUN3D to modify them when running
        - You have files sequenced via the following method in your directory
          where X can be any starting number, zero padded if needed.
             fun3d.nml.X
             ...
             fun3d.nml.Y

        Expected inputs:
              numProcess - Number to pass to mpirun -np option
              hostFile   - File to pass to mpirun --hostfile option
              outputFile - stdout Output from mpirun nodet_mpi call
        """

        import glob
        import shutil
        import os

        import utils

        # Find fun3d.nml.X in pwd
        inputFiles = glob.glob(os.path.join(self.startDir, self.inputName + '.*'))

        # Count them
        numInputFiles = inputFiles.len()

        # Loop over them
        for inputFile in inputFiles:
            # Startup
            # ===============================================

            # Copy fun3d.nml.X to fun3d.nml
            shutil.copyfile(inputFile, os.path.join(self.startDir, self.inputName))

            # Run!
            # ===============================================
            self.run()

            # Shutdown
            # ===============================================

            # Grab X off fun3d.nml.X
            X = inputFile.split('.')[-1]

            # Copy output files that can be modified/overwritten by fun3d to a folder
            # FUN3D_Manual-12.9.pdf Ch 5.3 Output Files
            newFolder = os.path.join(self.startDir, 'run' + X)
            os.mkdir(newFolder)

            outputFileTypes = ['*.flow', '*_hist.dat', '*_subhist.dat', '*.forces']
            utils.copyFilesOfPattern(outputFileTypes, self.startDir, newFolder)

            # Copy output file we made
            shutil.copy(self.outputFile, newFolder)
