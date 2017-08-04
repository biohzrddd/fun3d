#!/bin/bash


function makepbs () {

# Take a skeleton pbs submit script, copy to pwd, fill it in as needed
#
# Inputs:
#   Note: This requires a email.address file in $HOME with the first line as the email address to be notified
#
#  The inputs are expected to be in order. You can't switch order and expect it to work.
#     changeText          The text description of what is different about this run
#     numberOfNodes (Opt) Default: 4. Number of nodes to submit to #PBS -l select=4 <--nodes
#     numberOfHours       Default: 7.
#     numberOfMinutes     Default: 0.
#       queueName         Default: standard
#
# Example:
# submit a job with "changedSpecies" as the name on 4 nodes for 7 hours and 0 minutes
# to the standard (default) queue
# mysub "changedSpecies" 4 7 0
#
# to the debug queue
# mysub "changedSpecies" 4 7 0 debug

# Default inputs
changeText=""
numberOfNodes="4"
numberOfHours="07"
numberOfMinutes="00"
queueName="standard"

#=====================================
#User options
# Where to pull skeleton from
skeletonDir="$PROJECTS_HOME/AFITUS3D/share/scripts"

# How many levels above the pwd to include in name (excluding current)
# Example: /a/b/c/d/run
# given 3 should give a name of b_c_d
numDirLevels=5

# If no configuration file defined in $HOME/, use this
emailAddress='ERROR_NOEMAIL_DEFINED@us.af.mil'


#=====================================
# Pull some configuration stuff from a file on users profile
# This gets a few user-specific variables
configFile=$HOME/clusterConfig.sh
if [ ! -f $HOME/clusterConfig.sh ]; then
    echo "Error: No configuration file found: $configFile"
    exit 1
else
    echo "Reading: $configFile"
    source $configFile
fi


# Make a job name from the folder tree of an input number of levels up
currentDir=$(pwd)
jobName=$(gawk \
         -v awk_dir="$currentDir" \
         -v awk_ndir="$numDirLevels" \
         -vFS="" \
         'BEGIN {
                 # Split by the path separator
                 n=split(awk_dir, array, "/");

                 # Loop over starting where we need to until the end
                 tmp=""
                 for (i=n-awk_ndir; i < n; i++)
                     # Concatenate
                     tmp = (tmp "_" array[i])

                 # Remote first underscore
                 print substr(tmp,2)
                }')

# Check inputs
if [ "$1" ]
then
    changeText=$1
fi

if [ "$2" ]
then
    numberOfNodes=$2
fi

if [ "$3" ]
then
    numberOfHours=$(printf "%02d" $3)
fi
if [ "$4" ]
then
    numberOfMinutes=$(printf "%02d" $4)
fi

if [ "$5" ]
then
    queueName=$5
fi



# Copy the skeleton pbs script to a new one in the pwd that we can modify
skeletonScript="$skeletonDir/pbs-topaz.sh.skeleton"
submitScript="./pbs-topaz.sh"
\cp -f $skeletonScript $submitScript

# Modify stuff
# substitute abc for XYZ: s/abc/XYZ/
# /g global
sed --in-place --expression="s#{SH_NODES}#${numberOfNodes}#g" $submitScript
sed --in-place --expression="s#{SH_HOURS}#${numberOfHours}#g" $submitScript
sed --in-place --expression="s#{SH_MINUTES}#${numberOfMinutes}#g" $submitScript
sed --in-place --expression="s#{SH_QUEUE}#${queueName}#g" $submitScript
sed --in-place --expression="s#{SH_JOBNAME}#${jobName}#g" $submitScript
sed --in-place --expression="s#{SH_EMAIL}#${emailAddress}#g" $submitScript
sed --in-place --expression="s#{SH_PBS_SUBPROJECT_ID}#${pbsSubprojectId}#g" $submitScript

# Show user everything
echo "---------changeText: '$changeText'"
echo "------numberOfNodes: $numberOfNodes"
echo "------numberOfHours: $numberOfHours"
echo "----numberOfMinutes: $numberOfMinutes"
echo "----------queueName: $queueName"
echo "------------jobName: '$jobName'"
echo "-------emailAddress: '$emailAddress'"

# Submit!
#qsub ./pbs-topaz.sh

}
