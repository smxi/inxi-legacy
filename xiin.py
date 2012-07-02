#!/usr/bin/env python
__version__     = '2012.07.01-03'
__author__      = 'Scott Rogers, aka trash80'
__stability__   = 'beta'
__copying__     = """Copyright (C) 2011 W. Scott Rogers \
                        This program is free software.
                        You can redistribute it and/or modify it under the terms of the
                        GNU General Public License as published by the Free Software Foundation;
                        version 2 of the License.
                    """

#   Special thanks: h2, aka Harald Hope
import os
import sys
import time
import ftplib
import optparse

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
        self.remoteUrl   = 'http://inxi.googlecode.com/svn/branches/xiin'
        self.localUrl    = '{0}/'.format(os.getcwd())
    #end

    def main(self, xiinArgs):
        """
        Mostly a traffic director
        """
        # do some xiin
        self.xiin(xiinArgs)
    #end

    def xiin(self, xiinArgs):
        """
        The actual xiin workhorse.  See base.py for more information.
        """
        xiinAction = Base()
        xiinAction.xiin(xiinArgs)
    #end
#end

################################################################################
####
####        base.py
####
################################################################################

class Base(object):

    def __init__(self, textConf = 'xiin'):
        self = self
        self.version    = '%prog-{0}-{1}'
    #end

    def xiin(self, xiinArgs):
        """
        Starts the read capabilities
        """

        # http://docs.python.org/library/optparse.html

        xiinDesc = """ xiin is a directory parser meant to help debug inxi(www.inxi.org) bugs.
            xiin will take a given directory, usually /sys *[or /proc] and write the contents
            to a specified file in key:value format where key is the directory/filename
            and value is the contents of key."""

#        xiinUsage   = "%prog [-d] <directory to read> [-f] <file to write>"

        xiinVersion = self.version.format(__version__, __stability__)

        dirHelp     = 'Directory containing files. \
                        [Usage:  ] \
                        [Example:  ]'
        fileHelp    = 'If used write report to file, otherwise write output to the screen. \
                        [Usage:  ] \
                        [Example:  ]'
        displayHelp = 'Prints to terminal not to a file.  Cannot use with -f option. \
                        [Usage:  ] \
                        [Example:  ]'
        grepHelp    = 'Grep-like function. Can be sent to display(default) or file. \
                        [Usage: unused at this time] \
                        [Example: ]'
        uploadHelp  = 'Uploads a specified file to a specified ftp sight.  \
                        [Usage: xiin -u <source> <target> <uname> <password> ] \
                        [Example: xiin -u /home/myhome/.inxi/some.txt somedomain.com anon anon ]'
        upgradeHelp = 'Upgrades xiin to the newest version. \
                        [Usage: xiin -U <from url> \
                        [Example: xiin -u http://inxi.googlecode.com/svn/branches/xiin'

        self.parser = optparse.OptionParser(description = xiinDesc, version = xiinVersion)

        self.parser.add_option('-d', '--directory', dest = 'directory', help = dirHelp)
        self.parser.add_option('-f', '--file', dest = 'filename', help = fileHelp)
        self.parser.add_option('-o', '--out', action = 'store_true', dest = 'display', help = displayHelp)
        self.parser.add_option('-g', '--grep', dest = 'grep', help = grepHelp)
        self.parser.add_option('-u', '--upload', nargs=2, dest = 'upload', help = uploadHelp)
        self.parser.add_option('-U', '--update', nargs=1, dest = 'upgrade', help = upgradeHelp)

        (options, args) = self.parser.parse_args()

        options.args = xiinArgs

        self.__use_checker(options)
        self.__switch(options)

        exit(0)
    #end

    def __use_checker(self, xiinArgDict):
        """
        Checks for use errors.
        """
        if xiinArgDict.upload is None:
        # no arguements specified, so display helpful error
            if len(xiinArgDict.args) < 2:
                self.parser.error('Nothing to do. Try option -h or --help.')
                exit(2)

        # no output specified
            elif xiinArgDict.filename is None and xiinArgDict.display is None and xiinArgDict.grep is None:
                self.parser.error('specify to display output or send to a file')
                exit(3)

        # reading /proc will hang system for a while, it's a big deep virtual-directory
            elif xiinArgDict.directory == '/proc':
                self.parser.error('xiin can not walk /proc')
                exit(4)

        # the directory needed when option used
            elif xiinArgDict.directory is None:
                self.parser.error('xiin needs a directory')
                exit(5)

        elif len(xiinArgDict.upload ) < 2:
            print('')
            self.parser.error('ERROR: No xiin upload options given')
            self.parser.error('[Usage: uploader <source> <target> <uname> <password> ]')
            exit(6)
    #end

    def __switch(self, xiinArgDict):
        """
        Traffic director.
        """
        reader = Reader()

        # upgrade from specific url
        if xiinArgDict.upgrade is not None:
            print('In Development. DO NOT USE!')
#            print('Starting xiin upgrade')
#            print('')
#            # self update
#            if len(xiinArgDict.upgrade) == 0:
#                xiinArgDict.upgradeUrl = self.remoteUrl
#            elif len(xiinArgDict.upgrade) == 1:
#                xiinArgDict.upgradeUrl = xiinArgDict.upgrade[0]

#            self.__update_xiin()

        # Write output
        elif xiinArgDict.filename is not None:
            print('Starting xiin...')
            print('')
            with open(xiinArgDict.filename, 'w') as xiinArgDict.outputFile:
                reader.info(xiinArgDict)

        #Displays output.
        elif xiinArgDict.display:
            print('Starting xiin...')
            print('')
            reader.info(xiinArgDict)

        elif xiinArgDict.grep is not None:
            print('Starting xiin...')
            print('')
            print('Searching files...')
            print('')
            self.grepXiinInfo(xiinArgDict.grep)

        elif xiinArgDict.upload is not None:

            xiinArgDict.ftpSource      = None
            xiinArgDict.ftpDestination = None
            xiinArgDict.ftpUname       = None
            xiinArgDict.ftpPwd         = None

            if len(xiinArgDict.upload) > 0:
                xiinArgDict.ftpSource      = xiinArgDict.upload[0]
                xiinArgDict.ftpDestination = xiinArgDict.upload[1]

            if len(xiinArgDict.upload) > 2:
                # Legacy support
                if xiinArgDict.ftpUname is 'anon' or xiinArgDict.ftpUname is 'anonymous':
                    pass
                else:
                    xiinArgDict.ftpUname       = xiinArgDict.upload[2]
                    xiinArgDict.ftpPwd         = xiinArgDict.upload[3]

            print('Starting xiin uploader...')
            print('')
            print('Uploading debugging information...')
            print('')

            uploader = Uploader()
            uploader.upload(xiinArgDict.ftpSource, xiinArgDict.ftpDestination, xiinArgDict.ftpUname, xiinArgDict.ftpPwd)
        else:
            print('ERROR: Unknown')
            exit(7)
    #end

    def __check_python_version(self):
        # check the Version of python
        checkPython = PythonVersionCheck()
        checkPython.check()
    #end
#end

################################################################################
####
####        reader.py
####
################################################################################

class Reader(object):

    def __init__(self):
        self = self
    #end

    def info(self, xiinArgDict):
        """
        Walks the directory.
        """
        print("Getting info")
        print('')

        spinner = Spinner()

        count = 1

        for root, dirs, files in os.walk(xiinArgDict.directory):
            for file in files:
                xiinArgDict.fullPathFile = os.path.join(root, file)
                self.__readFile(xiinArgDict)
                # show spinner when writing files
                if not xiinArgDict.display:
                    spinner.render(count)
                    count = count + 1
    #end

    def __readFile(self, xiinArgDict):
        """
        Opens a file and prep to read.
        """
        try:
            if os.stat(xiinArgDict.fullPathFile).st_size:
                with open(xiinArgDict.fullPathFile, 'r') as xiinArgDict.key:
                    _hash = self.__hash(xiinArgDict)
                    if xiinArgDict.display:
                        print(_hash)
                    elif xiinArgDict.filename is not None:
                        xiinArgDict.outputFile.writelines(_hash)
                    else:
                        print('ERROR: Nothing to do')
                        exit(8)
        except:
            pass
    #end

    def __hash(self, xiinArgDict):
        """
        Returns a key[ directory ]:value [contents] hash.
        """
        _hash = ''

        try:
            return '{0}:{1}\n'.format(
                str(xiinArgDict.fullPathFile),
                str(xiinArgDict.key.readlines()).replace('\\n','')
            )
        except:
            pass

        return _hash
    #end
#end

################################################################################
####
####        spinner.py
####
################################################################################

class Spinner(object):
    """
    Spinner Class used to show a busy spinner within a loop.
    [Usage:     spinner.render(counter) ]
    """

    def __init__(self, typeOfSpinner = [ ' [\\] ', ' [|] ', ' [/] ', ' [-] '], color = None):
        """
        typeOfSpinner:  A dictionary of characters to use as the spinner.
        color:          The color of the spinner. Supports ASCII colors. [Default: stdio default ]
        """
        self = self
        self.typeOfSpinner  = typeOfSpinner
        self.color          = color
        self.mod            = 0
    #end

    def render(self, count):
        """
        Displays a busy spinner.
        """
        spinner = self.typeOfSpinner
        counter = (((count - 1)/4)%4)

        if (counter == self.mod):
            self.mod = self.mod + 1
            if self.mod > 3:
                self.mod = 0
            sys.stdout.write('\r' + str(spinner[self.mod]))
            sys.stdout.flush()

    #end

    def set_spinner_image(self, typeOfSpinner):
        """
        typeOfSpinner: A dictionary of characters to use as the spinner.
        """
        self.typeOfSpinner = typeOfSpinner
    #end

    def set_spinner_color(self, color):
        """
        color: The color of the spinner. Supports ASCII colors. [Default: stdio default ]
        """
        self.color = color
    #end

    def get_spinner_image(self):
        return self.typeOfSpinner
    #end

    def get_spinner_color(self):
        return self.color
    #end
#end

################################################################################
####
####        uploader.py
####
################################################################################

class Uploader(object):
    """
    Uploads a specified file to a specified ftp sight.  \
    [Usage: uploader <source> <target> <uname> <password> ] \
    [Example: uploader /home/myhome/.inxi/some.txt somedomain.com/directory anon anon ]
    """
    # exit(0): success
    # exit(1): incorrect file
    # exit(2): saving file error
    # exit(3): connection error
    # exit(4): login error
    # exit(5): error finding directory

    # http://effbot.org/librarybook/ftplib.htm
    # http://postneo.com/stories/2003/01/01/beyondTheBasicPythonFtplibExample.html
    # http://docs.python.org/library/ftplib.html

    def __init__(self):
        self = self

        # Success
        self.successFileUploaded        = 'SUCCESS: file uploaded'

        # Error
        self.errorConnectionFail        = 'ERROR: connection failed'
        self.errorPasswordMissing       = 'ERROR: password missing'
        self.errorLoginFail             = 'ERROR: login failed'
        self.errorConnectionError       = 'ERROR: connection error'
        self.errorDestinationNotFound   = 'ERROR: destination folder not found'
        self.errorFileNotSaved          = 'ERROR: file not saved'
        self.errorIncorrectFileType     = 'ERROR: Incorrect file type'
    #end

    def upload(self, source, target):
        self.upload(source, target, None, None)
    #end

    def upload(self, source, target, uname = None, password = None):
        """
        Uploads debugging information
        """
        destination = os.path.split(target)

        destinationServer = destination[0]
        if len(destination) > 1:
            destinationFolder = destination[1]

        try:
            ftp = ftplib.FTP(destinationServer)
        except:
            print(self.errorConnectionFail)
            exit(3)

        try:
            if uname is None:
                ftp.login()
            else:
                if password is not None:
                    ftp.login(uname, password)
                else:
                    print(self.errorPasswordMissing)
        except:
            print(self.errorLoginFail)
            exit(4)

        print(ftp.getwelcome())

        if ftp.getwelcome().find('220') >= 0:
            print('Connected...')
        else:
            print(self.errorConnectionError)
            exit(3)


        if destinationFolder is not None:
            try:
                ftp.cwd(destinationFolder)
                print('Opening: {0}'.format(destinationFolder))
            except:
                print(self.errorDestinationNotFound)
                exit(5)

        self.do_upload(ftp, source)

        ftp.quit()
        print(self.successFileUploaded)
        exit(0)
    #end

    def do_upload(self, ftp, file):
        """
        Upload the file.
        """
        extension       = os.path.splitext(file)[1]
        origDir         = os.getcwd()
        workingDir      = os.path.split(file)[0]
        workingFile     = os.path.split(file)[1]
        savedFileName   = self.check_file_name(workingFile, ftp)

        print('file: ' + workingFile)

        if extension in ('.tar.gz'):
            try:
                os.chdir(workingDir)
                print(ftp.pwd())
                ftp.storbinary('STOR ' + savedFileName, open(workingFile, 'rb'))
                os.chdir(origDir)
            except IOError:
                print(self.errorFileNotSaved)
                exit(2)
        else:
            print(self.errorIncorrectFileType)
            exit(1)
    #end

    def check_file_name(self, workingFile, ftp):
        """
        Check the server for a same file name.
        """
        fileList = ftp.nlst()

        for file in fileList:
            if file == workingFile:
                workingFile = self.rename_file(workingFile)

        return workingFile
    #end

    def rename_file(self, file):
        """
        Renames a file so that it no longer conflicts.
        """
        file = file.split('.', 1)
        extension = str(time.time()).split('.', 1)[0]
        newName = file[0] + '-' + extension + '.' + file[1]

        return newName
    #end
#end

################################################################################
####
####        PythonVersionCheck.py
####
################################################################################

class PythonVersionCheck(object):
    """
        Checks the Python version and stops progression is Python version is too old.
    """
    # http://stackoverflow.com/questions/1093322/how-do-i-check-what-version-of-python-is-running-my-script

    def __init__(self, lowestVersion = 0x02060000):
        self = self
        self.lowestVersion = lowestVersion
        self.pythonThreeVersion = 0x03000000
    #end

    def check(self, useVersionFile = False):
        """
        Detects Python compatibility.
        """
        pythonVersionText = 'Detecting Python version...[version 2.6+ required]...'
        pythonVersionErrorText = 'ERROR: Incorrect Python version: 2.6+ is required'
        pythonVersion3ErrorText = 'ERROR: Not Python3 compatible: 2.6-2.7 is required'
        pythonVersionPassText = 'Passed...continuing'

        print('')
        print(pythonVersionText)

        # create a file, if it exist, no reason to check again.
        verFile = os.path.join(os.getcwd(), str(sys.hexversion))

        if os.path.isfile(verFile) and useVersionFile is True:
            print('version file exists')
            pass
        else:
            if sys.hexversion < self.lowestVersion:
                print('')
                print(pythonVersionErrorText)
                exit(1)
#            elif sys.hexversion > self.pythonThreeVersion:
#                print('')
#                print(pythonVersion3ErrorText)
#                exit(1)
            else:
                print(pythonVersionPassText)
                print('')
                if useVersionFile is True:
                    with open(verFile, 'w') as xiinPyVer:
                        xiinPyVer.write(str(sys.hexversion))
                return
    #end

    def setMinimumVersion(self, lowestVersion):
        """
        lowestVersion:  The minimum python version required. [Default: 2.6 ]
        """
        self.lowestVersion = lowestVersion
    #end
#end

if __name__ == '__main__':
    # check the Version of python
    checkPython = PythonVersionCheck()
    checkPython.check()
    xiin = XIIN()
    xiin.main(sys.argv)
#end

# For inxi downloader.
# Do not change this last line.
# Do not move it to any other location.
# EOF checkPython