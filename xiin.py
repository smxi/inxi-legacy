import os.path
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
import ftplib
import optparse

def main(xiinArg):
    # http://docs.python.org/library/optparse.html

    checkPython()

    xiinDesc = """ xiin is a directory parser meant to help debug inxi(www.inxi.org) bugs.
        xiin will take a given directory, usually /sys or /proc and write the contents
        to a specified file in key:value format where key is the directory/filename
        and value is the contents of key."""

    xiinUsage   = "%prog [-d] <directory to read> [-f] <file to write>"

    xiinVersion = "%prog 2011.06.21-alpha"

#    defaultFile = os.environ['HOME'] + '/xiin.txt'
#    defaultDir = '/sys'
#    defaultDisplay = False

    dirHelp     = 'Directory containing files'
    fileHelp    = 'If used write report to file, otherwise write output to the screen'
    displayHelp = 'Prints to terminal not to a file.  Cannot use with -f option'
    grepHelp	= 'Grep-like function. Can be sent to display(default) or file. [Usage: unused at this time] [Example: ]'
    uploadHelp  = 'Uploads a specified file to a specified ftp sight.  [Usage: xiin -u <source> <target> ] [Example: xiin -u /home/myhome/.inxi/some.txt somedomain.com ]'

    parser = optparse.OptionParser(description = xiinDesc, usage = xiinUsage, version = xiinVersion)

    parser.add_option('-d', '--directory', dest = 'directory', help = dirHelp)
    parser.add_option('-f', '--file', dest = 'filename', help = fileHelp)
    parser.add_option('-o', '--out', action = 'store_true', dest = 'display', help = displayHelp)
    parser.add_option('-g', '--grep', dest = 'grep', help = grepHelp)
    parser.add_option('-u', '--upload', nargs=4, dest = 'upload', help = uploadHelp)
    
    (xiin, args) = parser.parse_args()

    xiin.args = xiinArg

    xiinUseChecker(xiin)
    xiinSwitch(xiin)

    exit(0)
#end

def xiinUseChecker(xiin):
    """ Checks for use errors """
    if xiin.upload is None:
    # no arguements specified, so display helpful error
        if len(xiin.args) < 2:
            parser.error('Nothing to do. Try option -h or --help.')
            exit(2)

    # no output specified
        elif xiin.filename is None and xiin.display is None and xiin.grep is None:
            parser.error('specify to display output or send to a file')
            exit(3)

    # reading /proc will hang system for a while, it's a big deep virtual-directory
        elif xiin.directory == '/proc':
            parser.error('xiin can not walk /proc')
            exit(4)

    # the directory needed when option used
        elif xiin.directory is None:
            parser.error('xiin needs a directory')
            exit(5)
    else:
        print('Using xiin upload feature')
#        xiin.ftp = {'source': '', 'destination': '', 'uname': '', 'password': ''}
        xiin.ftpSource      = xiin.upload[0]
        xiin.ftpDestination = xiin.upload[1]
        xiin.ftpUname       = xiin.upload[2]
        xiin.ftpPwd         = xiin.upload[3]
#end

def xiinSwitch(xiin):
    """ Traffic director """
# only display output
    if xiin.display is True and xiin.filename is None:
        print('Starting xiin...')
        print('')
        displayXiinInfo(xiin)

# only write output
    elif xiin.display is None and xiin.filename is not None:
        print('Starting xiin...')
        print('')
        print('Using options: ' + str(xiin))
        print('')
        writeXiinInfo(xiin)

    elif xiin.grep is not None:
	print('Starting xiin...')
	print('')
	print('Searching files...')
	print('')
	grepXiinInfo(xiin.grep)

    elif xiin.upload is not None:
        xiinLoader = XiinLoader()
        print('Starting xiin...')
        print('')
        print('Uploading debugging information...')
        print('')
        xiinLoader.uploadXiinInfo(xiin)

#end

# http://stackoverflow.com/questions/1093322/how-do-i-check-what-version-of-python-is-running-my-script
def checkPython():
        """ Detects Python compatibility.  Python 2.6+ required """
        print('checker')
        pythonVersionText = 'Detecting Python version...[version 2.6+ required]...'
        pythonVersionErrorText = 'ERROR: Incorrect Python version: 2.6+ is required'
        pythonVersionPassText = 'Passed...continuing'
        
        print('')
        print(pythonVersionText)
        if sys.hexversion < 0x02060000:
            print('')
            print(pythonVersionErrorText)
            exit(1)
        else:
            print(pythonVersionPassText)
            print('')
            return
    #end

def displayXiinInfo(xiin):
    """ Opens the write file and directs the walker, also displays output """
    print("Getting info")
    print('')

    for root, dirs, files in os.walk(xiin.directory):
	for file in files:
	    xiin.fullPathFile = os.path.join(root, file)
	    xiinOpenFile(xiin)
#end

def writeXiinInfo(xiin):
    """ Opens the write file and directs the walker, also displays output """
    print("Getting info")
    print('')

    with open(xiin.filename, 'w') as xiin.outputFile:
	xiinDirectoryWalker(xiin)
#end

def xiinDirectoryWalker(xiin):
    """ Walks the directory """

    count = 1
    
    for root, dirs, files in os.walk(xiin.directory):
	for file in files:
	    if int(count%25) > 4:
		count = 1
	    busySpinner(count)
	    count = count + 1
	    xiin.fullPathFile = os.path.join(root, file)
	    xiinOpenFile(xiin)
#end

def xiinOpenFile(xiin):
    """ Opens a file and prep to read """

    #  reading some file in /sys will turn off some monitors, so we do this:
    if xiin.directory == '/sys':
	try:
	    if os.stat(xiin.fullPathFile).st_size:
		with open(xiin.fullPathFile, 'r') as xiin.someFile:
		    xiinReadFileContents(xiin)
	except:
	    pass
    else:
	# other files seem alright
	try:
	    with open(xiin.fullPathFile, 'r') as xiin.someFile:
		xiinReadFileContents(xiin)
	except IOError:
	    pass
#end

def xiinReadFileContents(xiin):
    """ Read file contents and either display them or write them to a file """
    contents = []
    try:
	contents = xiin.someFile.readlines()
    except:
	pass

    if contents:
	key = str(xiin.fullPathFile).replace('/', '.').replace('.', '', 1)

	value = str(contents).replace('\\n','')

	if value != '[\'\']':
	    if xiin.display:
		print(key + ':' + value)
	    else:
		xiin.outputFile.writelines(key + ':' + value + ':' + '\n')
#end

def busySpinner(count):
    """ Displays a busy spinner"""
    spinner = [ ' -\\- ', ' -|- ', ' -/- ', ' --- ']

    if (int(count%25) == 1) or (int(count%25) == 2) or (int(count%25) == 3) or (int(count%25) == 4):
        print(spinner[count%25 - 1]),
        sys.stdout.flush()
        sys.stdout.write('\r')
#end

class XiinLoader(object):
    """ Class for xiin's uploading feature """

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
    #end

    def uploadXiinInfo(self, xiin):
        """ Uploads debugging information """

#        print(xiin.ftpSource)
#        print(xiin.ftpDestination)
#        print(xiin.ftpUname)
#        print(xiin.ftpPwd)

        destinationServer = os.path.split(xiin.ftpDestination)[0]
        destinationFolder = os.path.split(xiin.ftpDestination)[1]

        try:
            ftp = ftplib.FTP(destinationServer)
        except:
            print('ERROR: couldn\'t establish a connection')
            exit(3)

        try:
            if xiin.ftpUname == 'anon':
                ftp.login()
            else:
                ftp.login(xiin.ftpUname, xiin.ftpPwd)
        except:
            print('ERROR: couldn\'t login')
            exit(4)

        print(ftp.getwelcome())
        if ftp.getwelcome().find('220') >= 0:
            print('Connected...')
        else:
            print('ERROR: connection error')
            exit(3)

        try:
            if destinationFolder is not None:
                ftp.cwd(destinationFolder)
                print('Opening ' + destinationFolder)
        except:
            print('ERROR: couldn\'t find destination folder')
            exit(5)

        self.upload(ftp, xiin.ftpSource)

        ftp.quit()
        print('xiin successfully uploaded the file')
        exit(0)
    #end

    def upload(self, ftp, file):
        """ Does the upload work """

        extension = os.path.splitext(file)[1]
        origDir = os.getcwd()
        workingDir = os.path.split(file)[0]
        workingFile = os.path.split(file)[1]

        print('file: ' + workingFile)

        if extension in ('.tar.gz'):
            try:
                os.chdir(workingDir)
                print(ftp.pwd())
                ftp.storbinary('STOR ' + workingFile, open(workingFile))
                os.chdir(origDir)
            except IOError:
                print('ERROR: could not save file')
                exit(2)
        else:
            print('ERROR: Incorrect file')
            exit(1)
    #end

    def checkForSameName(self, workingFile, ftp):
        """ Check the server for a same file name """

#        fileList = ftp.nlst()
#        fileName = workingFile.
#
#        for file in fileList:
#            if file == workingFile;
#                workingFile = workingFile
    #end
#end

if __name__ == '__main__':
    main(sys.argv)
#end