#!/usr/bin/env python
__version__     = '2011.07.10-03'
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
####        Thin xiin frontend class
####
################################################################################

class XIIN(object):
    """
    A very thin frontend to all of xiin.  Keeps the external API while allowing
    parts of xiin to be updated on the fly.
    """

    def __init__(self, textConf = 'xiin'):
        self = self
        self.remoteUrl   = 'http://pyne.googlecode.com/svn/branches/testing/PyneTools/xiin/'
        self.localUrl    = '{0}/'.format(os.getcwd())
    #end

    def main(self, xiinArgs):
        """
        Mostly a traffic director
        """
        # self update
        self.__update_xiin()
        # do some xiin
        self.xiin(xiinArgs)
    #end

    def __update_xiin(self):
        """
        Update all modules to the newest versions.
        """        
        # update xiin modules
        update = SelfUpdate()
        update.update_all(self.localUrl, self.remoteUrl)
    #end

    def xiin(self, xiinArgs):
        """
        The actual xiin workhorse.  See base.py for more information.
        """
        from base import Base
        xiinAction = Base()
        xiinAction.xiin(xiinArgs)
    #end
#end

################################################################################
####
####        xiin self updater class
####
################################################################################

class SelfUpdate(object):

    def __init__(self, blocksize = 1024):
        self = self
        self.blockSize = blocksize
        self.modUpdateList = ['base.py', 'PythonVersionCheck.py', 'reader.py', 'spinner.py', 'uploader.py']
    #end

    def update_all(self, localUrl, remoteUrl):
        """
        Iterates over the module list.
        """
        for modUpdate in self.modUpdateList:
            self.download(remoteUrl + modUpdate, localUrl + modUpdate)
    #end

    def download(self, source, destination):
        """
        Download a module.
        """
        import urllib2
        connection  = urllib2.urlopen(source)
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
#end

if __name__ == '__main__':
    xiin = XIIN()
    xiin.main(sys.argv)
#end

# For inxi downloader.
# Do not change this last line.
# Do not move it to any other location.
# EOF checkPython