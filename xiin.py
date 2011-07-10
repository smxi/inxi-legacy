#!/usr/bin/env python
__version__     = '2011.07.10-02'
__author__      = 'Scott Rogers, aka trash80'
__stability__   = 'alpha'
__copying__     = """Copyright (C) 2011 W. Scott Rogers \
                        This program is free software.
                        You can redistribute it and/or modify it under the terms of the
                        GNU General Public License as published by the Free Software Foundation;
                        version 2 of the License.
                    """

#   Special thanks: h2, aka Harald Hope

import os
import sys

################################################################################
####
####        Main xiin class
####
################################################################################

class XIIN(object):
    """
    A very thin frontend to all of xiin.  Keeps the external API while allowing
    parts of xiin to be updated on the fly.
    """

    def __init__(self, textConf = 'xiin'):
        self = self
    #end

    def main(self, xiinArgs):

        # self update
        self.__update_xiin()

        # do some xiin
        self.xiin(xiinArgs)
    #end

    def __update_xiin(self):
        remoteUrl   = 'http://pyne.googlecode.com/svn/branches/testing/PyneTools/xiin/'
        localUrl    = '{0}/'.format(os.getcwd())
        
        # Check for newer versions of xiin modules
        update      = SelfUpdate()

        update.update_all(localUrl, remoteUrl)
#        update.update(localUrl, remoteUrl)
    #end

    def xiin(self, xiinArgs):
        from base import Base
        xiinAction = Base()
        xiinAction.xiin(xiinArgs)
    #end
#end

class SelfUpdate(object):

    def __init__(self, blocksize = 1024):
        self = self
        self.blockSize = blocksize
        self.modUpdateList = ['base.py', 'PythonVersionCheck.py', 'reader.py', 'spinner.py', 'uploader.py']
    #end

    def update_all(self, localUrl, remoteUrl):

        for modUpdate in self.modUpdateList:
            self.download(remoteUrl + modUpdate, localUrl + modUpdate)
    #end

    def download(self, source, destination):
        """
        Download a new version of a module
        """
        import urllib2
        connection  = urllib2.urlopen(source)
        self.set_module_dir(destination)

        try:
            with open(destination, 'w') as localFile:
                while True:
                    modLine = connection.read(self.blockSize)
                    if not modLine:
                        break
                    localFile.write(modLine)
            return True
        except:
            return False
    #end

    def set_module_dir(self, destination):
        """
        Creates a place for xiin modules if the folder doesn't exist.
        """
        import os
        directory = os.path.dirname(destination)
        if not os.path.isdir(directory):
            os.makedirs(directory)
    #end
#end

if __name__ == '__main__':
    xiin = XIIN()
    xiin.main(sys.argv)
#end

# For inxi downloader.
# Do not change this last line.
# Do not move it to any other location.
# EOF checkPython