#-------------------------------------------------------------------------------
# Name:         xlistr
# Purpose:      Play music playlists from exactly where they left off
#
# Author:      thighfill
#
# Created:     22/05/2013
# Copyright:   (c) thighfill 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python
import os,sys
print os.curdir
HOME=os.path.abspath(".")
if not HOME.endswith('xlistr'):
    HOME+=os.sep+'xlistr'
PARENT=os.path.split(HOME)[0]
print "HOME=%s\nPARENT=%s" % (HOME,PARENT)
pathset=set(sys.path)
pathset.add(HOME)
pathset.add(PARENT)
sys.path=list(pathset)
os.curdir=HOME
#print sys.path
from xmlreader import *
import gui,tkFileDialog
print gui.format(129.787667)
VERSION="ALPHA 0.0.1"
FNAME_ALL="playlists/all.xml"
all_songs=None
try:
    all_songs=Playlist(FNAME_ALL,title="All")
except(IOError):
    try:
        all_songs=new_playlist("All",FNAME_ALL)
    except(IOError):
        pass
class XlistrException(Exception):
    pass
def add_song(filename,title=None):
	all_songs.add_song(new_song(filename,title=title))
def installAVbin():
    gui.messagebox("AVbin is required to use this app.\nIt will now be installed.")
    url=None
    is_64bits = sys.maxsize > 2**32
    if sys.platform.startswith('linux'):
        if is_64bits:
            url="https://github.com/downloads/AVbin/AVbin/install-avbin-linux-x86-64-v10"
        else:
            url="https://github.com/downloads/AVbin/AVbin/install-avbin-linux-x86-32-v10"
    elif sys.platform.startswith('win'):
        if is_64bits:
            url="https://github.com/downloads/AVbin/AVbin/AVbin10-win64.exe"
        else:
            url="https://github.com/downloads/AVbin/AVbin/AVbin10-win32.exe"
    elif sys.platform=='darwin':
        url="https://github.com/downloads/AVbin/AVbin/AVbin10.pkg"
    if url:
        fname=os.path.join(HOME,os.path.split(url)[1])
        import urllib
        urllib.urlretrieve(url,fname)
        os.system("\"%s\"" % fname)
        os.remove(fname)
    else:
        raise XlistrException("AVbin could not be installed: Unsopported operating system")
    gui.messagebox("The application will now exit.")
    sys.exit()
#Main section
def main():
    #gui.thread_create(gui.FilterEditor)
    #import xlistr.basictest as test
    #test.main()
    gui.create()
    delTemps()
def delTemps():#Delete temp files
    path=os.path.join(HOME,"temp")
    for f in os.listdir(path):
        if not f.endswith('__init__.py'):
            os.remove(path+os.sep+f)

if __name__ == '__main__':
    main()
