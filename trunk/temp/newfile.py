
master=None
def execute(event=None):
	import tkFileDialog
	fname=tkFileDialog.asksaveasfilename()
	if fname!=None and fname!='':
		master.newfile(fname)
		