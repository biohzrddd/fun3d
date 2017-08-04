class Pbs:
    """Class to setup PBS runs in various ways"""

    # class variables shared by all instances

    def __init__(self, hostFile='hosts', startDir=''):
        """
        Stuff
        """

        import os
        from datetime import datetime

        # instance variables unique to each instance
        self.hostFile = hostFile

        if startDir == '':
            self.startDir = os.getcwd()
        self.jobDir = ''
        self.runDir = ''

        self.clusterName = ''

        self.jobId = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

        self.numProcess = 1

    def runSetup(self):
        """
        When our job gets launched from queue to running on a node,
        we need to setup some stuff.

        Query information available in the environment under
        PBS_* and BC_* (if available).

        If this is available, override defaults
        """

        import os
        from datetime import datetime

        import utils

        # Copy starting folder to work directory
        # ==============================================

        # Grab directory where submit was performed
        if 'PBS_O_WORKDIR' in os.environ:
            self.startDir = os.environ['PBS_O_WORKDIR']

        # Extract job id numbers by splitting off before the dot
        if 'PBS_JOBID' in os.environ:
            self.jobId = os.environ['PBS_JOBID'].split('.')[0]

        # Where we want to copy the run folder to
        clusterName = utils.detectLocation()
        if 'PBS_JOBNAME' in os.environ:
            self.jobName = os.environ['PBS_JOBSNAME']
        else:
            self.jobName = 'python'

        if clusterName == '':
            self.jobDir = '.'.join([self.jobName, self.jobId])
        else:
            self.jobDir = '.'.join([self.jobName, self.jobId, clusterName])

        # Make a folder next to the startup folder
        self.runDir = os.path.join(self.startDir, '..', self.jobDir)
        os.mkdir(self.runDir)

        # --------------------------------
        # Store the name of the sorted unique PBS assigned hosts
        # (nodes) to the file hosts
        if 'PBS_NODEFILE' in os.environ:
            nodeFile = os.environ['PBS_NODEFILE']
            with open(nodeFile) as f:
                nodes = f.readlines()
        else:
            nodes = []

        self.numProcess = self.getNumProcess(nodes)

        # Get a unique set of the nodes
        uNodes = set(nodes)

        # Write to a file for mpirun to read
        with open(self.hostFile) as f:
            f.writelines(uNodes)

    def getNumProcess(self, nodes=[]):
        import os

        if 'BC_MPI_TASKS_ALLOC' in os.environ:
            # Count by input environment variable
            # This method usable on topaz
            numProcess = os.environ['BC_MPI_TASKS_ALLOC']
        elif 'PBS_NODEFILE' in os.environ:
            # Count by number of nodes (probably duplicates)
            # This method usable on afit
            """ 
            Depending on PBS setup, nodes can be a duplicated based on number of processors per node
             e.g.
             nodeX and nodeY have 2 cores each and we requested 4, then nodes would be
             nodeX
             nodeX
             nodeY
             nodeY
            """
            numProcess = nodes.count()
        else:
            numProcess = 1

        return numProcess