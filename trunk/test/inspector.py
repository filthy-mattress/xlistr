import os,sys
if __name__=="__main__":
    HOME= os.path.abspath('.')
    PARENT= os.path.split(HOME)[0]
    SUPER=os.path.split(PARENT)[0]
    print HOME,PARENT,SUPER
    sys.path.append(PARENT)
    sys.path.append(SUPER)
    #print sys.path
import xlistr,tkFileDialog
xlistr.HOME=PARENT
xlistr.PARENT=SUPER
import xmlreader as xml
print "cmd or gui?"
resp=raw_input(">").lower()
if resp=='cmd':
    _input=lambda :raw_input("File name:")
elif resp=='gui':
    _input=lambda :tkFileDialog.askopenfilename()
commands={'exit':sys.exit}
def inspectplaylist():
    plist=xml.Playlist(_input())
    text='''Title:%s
Creator:%s
Songs:
--------------------------------------------------------------------------
Filt?|Title                  |Artist                  |Album Title
--------------------------------------------------------------------------
''' % (plist.get_title(),plist.get_creator())
    for song in plist.get_songs():
        if plist.test_song(song):
            text+='Pass'
        else:
            text+='Fail'
        text+=' |'+song.get_title()+'|'+song.get_artist()+'|'+song.get_albumtitle()
        text+='\n'
    text+='''Albums:
--------------------------------------------------------------------------
Title                   |Artist
--------------------------------------------------------------------------
'''
    for album in plist.get_albums():
        tup=(album.get_title(),album.get_artist())
        text+="%s|%s\n" % tup
    text+="Filters:\n"
    for filt in plist.get_filters():
        text+=filt.get_href()+"\n"
    print text
commands['insp plist']=inspectplaylist



while True:
    try:
        commands[raw_input('>')]()
    except(KeyError):
        print 'invalid command'
    except(SystemExit):
        break
