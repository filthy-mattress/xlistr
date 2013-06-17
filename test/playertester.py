import xlistr.gui as gui
import xlistr.xmlreader as xmlr
import tkFileDialog
def main(func=gui.PlayerFrame):
	gui.create(func,xmlr.Playlist(tkFileDialog.askopenfilename()))