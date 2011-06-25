#!/usr/bin/env python

#    author: Scott Rogers
#    stability: alpha
#    copying: 'Copyright (C) 2011 W. Scott Rogers
#              This program is free software.
#              You can redistribute it and/or modify it under the terms of the
#              GNU General Public License as published by the Free Software Foundation;
#              version 2 of the License.
#
#   Special thanks: h2, aka Harald Hope

import os
import sys
import time
import ftplib
import optparse

################################################################################
####
####        Main xiin class
####
################################################################################

class XIIN(object):

    def __init__(self):
        self = self
    #end

    def read(self, xiinArg):
        """
        Starts the read capabilities
        """
        # http://docs.python.org/library/optparse.html

        checkPython = PythonVersionCheck()
        checkPython.check()

        xiinDesc = """ xiin is a directory parser meant to help debug inxi(www.inxi.org) bugs.
            xiin will take a given directory, usually /sys or /proc and write the contents
            to a specified file in key:value format where key is the directory/filename
            and value is the contents of key."""

        xiinUsage   = "%prog [-d] <directory to read> [-f] <file to write>"

        xiinVersion = "%prog 2011.06.25-alpha-3"

    #    defaultFile = os.environ['HOME'] + '/xiin.txt'
    #    defaultDir = '/sys'
    #    defaultDisplay = False

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

        parser = optparse.OptionParser(description = xiinDesc, usage = xiinUsage, version = xiinVersion)

        parser.add_option('-d', '--directory', dest = 'directory', help = dirHelp)
        parser.add_option('-f', '--file', dest = 'filename', help = fileHelp)
        parser.add_option('-o', '--out', action = 'store_true', dest = 'display', help = displayHelp)
        parser.add_option('-g', '--grep', dest = 'grep', help = grepHelp)
        parser.add_option('-u', '--upload', nargs=2, dest = 'upload', help = uploadHelp)

        (options, args) = parser.parse_args()

        options.args = xiinArg

        self.xiinUseChecker(options)
        self.xiinSwitch(options)

        exit(0)
    #end

    def xiinUseChecker(self, xiinArgDict):
        """
        Checks for use errors.
        """

        if xiinArgDict.upload is None:
        # no arguements specified, so display helpful error
            if len(xiinArgDict.args) < 2:
                parser.error('Nothing to do. Try option -h or --help.')
                exit(2)

        # no output specified
            elif xiinArgDict.filename is None and xiinArgDict.display is None and xiinArgDict.grep is None:
                parser.error('specify to display output or send to a file')
                exit(3)

        # reading /proc will hang system for a while, it's a big deep virtual-directory
            elif xiinArgDict.directory == '/proc':
                parser.error('xiin can not walk /proc')
                exit(4)

        # the directory needed when option used
            elif xiinArgDict.directory is None:
                parser.error('xiin needs a directory')
                exit(5)
        else:
            if len(xiinArgDict.upload ) < 2:
                print('')
                parser.error('ERROR: No xiin upload options given')
                parser.error('[Usage: uploader <source> <target> <uname> <password> ]')
                print('')
                exit(6)
    #end

    def xiinSwitch(self, xiinArgDict):
        """
        Traffic director.
        """

    # only display output
        if xiinArgDict.display is True and xiinArgDict.filename is None:
            print('Starting xiin...')
            print('')
            self.displayXiinInfo(xiinArgDict)

    # only write output
        elif xiinArgDict.display is None and xiinArgDict.filename is not None:
            print('Starting xiin...')
            print('')
            self.writeXiinInfo(xiinArgDict)

        elif xiinArgDict.grep is not None:
            print('Starting xiin...')
            print('')
            print('Searching files...')
            print('')
            self.grepXiinInfo(xiinArgDict.grep)

        elif xiinArgDict.upload is not None:
    #        xiin.ftp = {'source': '', 'destination': '', 'uname': '', 'password': ''}

            xiinArgDict.ftpSource      = None
            xiinArgDict.ftpDestination = None
            xiinArgDict.ftpUname       = None
            xiinArgDict.ftpPwd         = None

            if len(xiinArgDict.upload ) > 0:
                xiinArgDict.ftpSource      = xiinArgDict.upload[0]
                xiinArgDict.ftpDestination = xiinArgDict.upload[1]

            if len(xiinArgDict.upload ) > 2:
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

            uploader = XiinUploader()
            uploader.upload(xiinArgDict.ftpSource, xiinArgDict.ftpDestination, xiinArgDict.ftpUname, xiinArgDict.ftpPwd)
        else:
            print('ERROR: Unknown')
            exit(7)

    #end

    def displayXiinInfo(self, xiinArgDict):
        """
        Opens the write file and directs the walker, also displays output.
        """

        print("Getting info")
        print('')

        for root, dirs, files in os.walk(xiinArgDict.directory):
            for file in files:
                xiinArgDict.fullPathFile = os.path.join(root, file)
                self.xiinOpenFile(xiinArgDict)
    #end

    def writeXiinInfo(self, xiinArgDict):
        """
        Opens the write file and directs the walker, also displays output.
        """

        print("Getting info")
        print('')

        with open(xiinArgDict.filename, 'w') as xiinArgDict.outputFile:
            self.xiinDirectoryWalker(xiinArgDict)
    #end

    def xiinDirectoryWalker(self, xiinArgDict):
        """
        Walks the directory.
        """

        spinner = Spinner()

        count = 1

        for root, dirs, files in os.walk(xiinArgDict.directory):
            for file in files:
                spinner.render(count)
                count = count + 1
                xiinArgDict.fullPathFile = os.path.join(root, file)
                self.xiinOpenFile(xiinArgDict)
    #end

    def xiinOpenFile(self, xiinArgDict):
        """
        Opens a file and prep to read.
        """

        #  reading some file in /sys will turn off some monitors, so we do this:
        if xiinArgDict.directory == '/sys':
            try:
                if os.stat(xiinArgDict.fullPathFile).st_size:
                    with open(xiinArgDict.fullPathFile, 'r') as xiinArgDict.someFile:
                        self.xiinReadFileContents(xiinArgDict)
            except:
                pass
        else:
            # other files seem alright
            try:
                with open(xiinArgDict.fullPathFile, 'r') as xiinArgDict.someFile:
                    self.xiinReadFileContents(xiinArgDict)
            except IOError:
                pass
    #end

    def xiinReadFileContents(self, xiinArgDict):
        """
        Read file contents and either display them or write them to a file.
        """

        contents = []
        try:
            contents = xiinArgDict.someFile.readlines()
        except:
            pass

        if contents:
            key = str(xiinArgDict.fullPathFile)#.replace('/', '.').replace('.', '', 1)

            value = str(contents).replace('\\n','')

            if value != '[\'\']':
                if xiinArgDict.display:
                    print(key + ':' + value)
                else:
                    xiinArgDict.outputFile.writelines(key + ':' + value + ':' + '\n')
    #end
#end

################################################################################
####
####        xiin spinner class
####
################################################################################

class Spinner(object):

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
            print(spinner[self.mod]),
            sys.stdout.flush()
            sys.stdout.write('\r')

    #end

    def setSpinnerImage(self, typeOfSpinner):
        """
        typeOfSpinner: A dictionary of characters to use as the spinner.
        """
        self.typeOfSpinner = typeOfSpinner
    #end

    def setSpinnerColor(self, color):
        """
        color: The color of the spinner. Supports ASCII colors. [Default: stdio default ]
        """
        self.color = color
    #end

    def getSpinnerImage(self):
        return self.typeOfSpinner
    #end

    def getSpinnerColor(self):
        return self.color
    #end

#end

################################################################################
####
####        xiin Python version checker class
####
################################################################################

class PythonVersionCheck(object):
    # http://stackoverflow.com/questions/1093322/how-do-i-check-what-version-of-python-is-running-my-script

    def __init__(self):
        """

        """
        
        self = self
        self.lowestVersion = None
    #end

    def check(self):
            """
            Detects Python compatibility.
            """

            pythonVersionText = 'Detecting Python version...[version 2.6+ required]...'
            pythonVersionErrorText = 'ERROR: Incorrect Python version: 2.6+ is required'
            pythonVersionPassText = 'Passed...continuing'

            print('')
            print(pythonVersionText)

            if (self.lowestVersion is None):
                self.setMinimumVersion()

            if sys.hexversion < self.lowestVersion:
                print('')
                print(pythonVersionErrorText)
                exit(1)
            else:
                print(pythonVersionPassText)
                print('')
                return
        #end

    def setMinimumVersion(self, lowestVersion = 0x02060000):
        """
        lowestVersion:  The minimum python version required. [Default: 2.6 ]
        """
        self.lowestVersion = lowestVersion
    #end
#end

################################################################################
####
####        xiin uploader class
####
################################################################################

class XiinUploader(object):
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
                print('Opening /' + destinationFolder)
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

        print('Uploading: ' + workingFile)

        if extension in ('.tar.gz'):
            try:
                os.chdir(workingDir)
                print(ftp.pwd())
                ftp.storbinary('STOR ' + savedFileName, open(workingFile))
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

if __name__ == '__main__':
    xiin = XIIN()
    xiin.read(sys.argv)
#end