"""Utility functions for the fun3d package"""

def copyFilesOfPattern(patterns=['*'], sourceDir='./', destDir='./copyFolder'):
    """Copy files from source directory that match one of the patterns to a directory"""
    import os
    import shutil
    import re

    for filename in os.listdir(sourceDir):
        for pattern in patterns:
            if re.match(pattern, filename):
                shutil.copy(filename, destDir)

def detectLocation():
    """
    Figure out if running on AFIT or topaz network

    returns:
    networkName - lower case string of the network name as defined here.
                  empty if it could not match.
    """

    import socket

    # Detect if we're on AFIT or topaz network
    ip = socket.gethostbyname(socket.gethostname()).split('.')

    if ip[0] == '129':
        # Probably AFIT
        networkName = 'afit'
    elif ip[0] == '140':
        # Probably topaz
        networkName = 'topaz'
    else:
        networkName = ''

    return networkName