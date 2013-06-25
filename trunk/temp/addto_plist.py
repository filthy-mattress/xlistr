
master=None
def execute(event=None):
	filt=master.current_editor().filt
	if filt:
		import tkFileDialog
		from xmlreader import Playlist
		plist=Playlist(tkFileDialog.askopenfilename())
		plist.add_filter(filt)
		