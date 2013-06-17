#-------------------------------------------------------------------------------
# Name:  module1
# Purpose:
#
# Author:    thighfill
#
# Created:   05/06/2013
# Copyright:   (c) thighfill 2013
# Licence:   <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python
import xlistr,eyed3,tkFileDialog,os
import xmlreader as io
#print os.curdir
def main():
    xmlfile=tkFileDialog.askopenfilename()
    content=""
    while True:
        files=tkFileDialog.askopenfilenames()
        files=files[:len(files)-1].replace("{","").split("} ")
        idx=0
        for fname in files:
            if fname!="":
                af=eyed3.load(fname)
                fname=os.path.relpath(fname,xmlfile)
                tag=af.tag
                content+= '''
        <song href="%s">
            <title>%s</title>
            <artist>%s</artist>
            <albumtitle>%s</albumtitle>
            <index>%i</index>
            <genre>%s</genre>
        </song>''' % (fname,tag.title,tag.artist,tag.album,idx,tag.genre)
                idx+=1
        resp=raw_input("More?")
        if resp!="y":
            break
    io.write_file(xmlfile,io.read_file(xmlfile).replace("<!Content here>",content))
if __name__ == '__main__':
    main()
