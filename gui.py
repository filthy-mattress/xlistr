from Tkinter import *
from ttk import *
import Tkdnd
import xlistr,tkFileDialog
from xmlreader import *
from ScrolledText import ScrolledText
from ToolTip import ToolTip
DESIGN="design"
CODE="code"
def getroot(widget):
	master=widget
	while not isinstance(master,Tk):
		try:
			master=master.master
		except(AttributeError):
			return None
	return master
def messagebox(text):
	root=Tk()
	root.title("Message")
	Label(root,text=text).grid(row=0,column=0)
	Button(root,text="OK",command=root.quit).grid(row=1,column=0)
	root.mainloop()
def make_code(content="return True",imports=""):
	return """%s
def test(song):
	%s""" % (imports,content)
def add_scroll(widget,orient):
	scroll=Scrollbar(widget,orient=orient)
	if orient=='vertical':
		scroll.pack(side=RIGHT,fill=Y)
		widget.config(yscrollcommand=scroll.set)
		scroll.config(command=widget.yview)
	elif orient=='horizontal':
		scroll.pack(side=BOTTOM,fill=X)
		widget.config(xscrollcommand=scroll.set)
		scroll.config(command=widget.xview)
	return scroll
def add_yscroll(widget):
	return add_scroll(widget,'vertical')
def add_xscroll(widget):
	return add_scroll(widget,'horizontal')
def xmlMenu_by_filename(master,filename,frame):
	return XMLMenu(master,read_file(filename),frame)
def current_id(nb):
	return nb.tabs()[nb.index("current")]
class BoolBox(Checkbutton):
	def __init__(self,master,default=True,**kw):
		Checkbutton.__init__(self,master)
		self.config(kw)
		self.val=IntVar(self,default)
		self.config(variable=self.val,onvalue=True,offvalue=False)
	def toggle(self):
		if self.val:
			self.deselect()
		else:
			self.select()
class XMLMenu(Menu):
	def __init__(self,master,text,frame, **kw):
		Menu.__init__(self,master, kw)
		master.config(menu=self)
		import xml.etree.ElementTree as ET
		root=ET.fromstring(text)
		self.funcs={}
		for method in root.find("python").findall("method"):
			name=method.get("name")
			fname=xlistr.HOME+"/temp/"+name
			write_file(fname+".py",method.text)
			#print method.text
			_mod=__import__("temp."+name,globals(),locals(),['master','execute'], -1)
			_mod.master=frame
			self.funcs[name]=_mod.execute
		self.submenus={"root":(self,self)}
		keys=[]
		for elem in root.find("menus").iter():
			default="root"
			if keys:
				default=keys[len(keys)-1]
			parent=self.submenus[elem.get("parent",default)][0]
			if elem.tag=="sep":
				parent.add_separator()
			else:
				label=elem.get("label")
				if elem.tag=="cmd":
					func=self.funcs[elem.get("command")]
					parent.add_command(label=label,command=func)
					bindkey=elem.get("bind")
					if bindkey:
						master.bind("<"+bindkey+">",func)
				elif elem.tag=="menu":
					newmenu=Menu(parent, kw)
					self.submenus[label]=(newmenu,parent)
					keys.append(label)
					parent.add_cascade(label=label,menu=newmenu)
class PlaylistNB(Notebook):
	def __init__(self,master,**kw):
		Notebook.__init__(self,master)
		self.config(kw)
		self.enable_traversal()
		self.keychars=[]
		self.tabsreg={}
	def addplaylist(self,playlist):
		frame=Frame(self)
		songslist=SongsFrame(frame,playlist)
		player=PlayerFrame(frame,playlist)
		songslist.grid(row=0,column=0,rowspan=6)
		player.grid(row=5,column=0)
		frame.pack()
		title=playlist.get_title()
		underline=self.getkeychar(title)
		if underline:
			self.keychars.append(underline)
			self.add(frame,text=title,underline=underline)
		else:
			self.add(frame,text=title)
		self.select(self.index("end")-1)
		tab_id=self.curr_id()
		self.tabsreg[tab_id]=playlist
	def curr_id(self):
		return self.tabs()[self.index("current")]
	def curr_playlist(self):
		return self.tabsreg[self.curr_id()]
	def getkeychar(self,title):
		idx=0
		for c in title:
			if c not in self.keychars:
				return idx
			idx+=1
		return None
class App(Frame):
	def __init__(self,master,width=800,height=600):
		Frame.__init__(self, master,width=width,height=height)
		self.pack()
		self.master.title('Xlistr ver:'+xlistr.VERSION)
		self.menu=xmlMenu_by_filename(master,xlistr.HOME+'/data/appMenu.xml',self)
		#Set up music library notebook
		self.musicnb=Notebook(self)
		self.musicnb.grid(row=0,column=0)
		self.musicnb.enable_traversal()
		#Set up tabs
		self.songsframe=SongsFrame(self.musicnb,xlistr.all_songs)
		self.albumframe=AlbumFrame(self.musicnb,xlistr.all_songs)
		self.musicnb.add(self.songsframe,text="Songs",sticky='n',underline=0)
		self.musicnb.add(self.albumframe,text="Albums",sticky='n',underline=0)
		self.songsframe.pack()
		self.albumframe.pack()
		#Separator
		Separator(self,orient='vertical').grid(row=0,column=1)
		#Playlists notebook
		self.playlistnb=PlaylistNB(self)
		self.playlistnb.grid(row=0,column=2)
		self.playlistnb.addplaylist(xlistr.all_songs)
		#TODO finish this class
	def save(self):
		for tab_id in self.playlistnb.tabsreg:
			self.playlistnb.tabsreg[tab_id].save()
	def openfile(self):
		fname=tkFileDialog.askopenfilename()
		if fname.endswith('.xml'):
			plist=Playlist(fname)
			self.playlistnb.addplaylist(plist)
			for song in plist.get_songs():
				self.addsong(song)
		elif fname.endswith('.mp3'):
			self.addsong(new_song(fname))
	def addsong(self,song):
		xlistr.all_songs.add_song(song)
		self.songsframe.addsong(song)
	def newfilteditor(self,playlist=None):
		thread_create(FilterEditor)
class SortButton(Button):
	def __init__(self,master,text,index,**kw):
		Button.__init__(self,master,text=text,command=self.sort)
		self.config(kw)
		self.index=index
	def sort(self):
		self.master.sort(self.index)
class SongsFrame(Canvas):
	def __init__(self,master,playlist):
		Canvas.__init__(self,master)
		self.playlist=playlist
		self.lines={}
		#add_yscroll(self)
		self.masterbtn=BoolBox(self,False,command=self.checkall)
		self.masterbtn.grid(row=0,column=0)
		col=1
		for item in ('Title','Artist','Rating'):
			SortButton(self,item,col+1).grid(row=0,column=col)
			col+=1
		self.load_songs()
	def checkall(self):
		for frame in self.lines:
			if frame.chk.val!=self.masterbtn.val:
				frame.chk.toggle()
				frame.cb()
	def load_songs(self):
		for song in self.playlist.get_songs():
			self.addsong(song)
	def addsong(self,song,selected=False):
		if song not in xlistr.all_songs.get_songs():
			f=SongLine(self,song)
			self.addframe(f)
	def addframe(self,frame):
		frame.grid(row=len(self.lines)+1,column=0,columnspan=4)
		self.lines[frame]=frame.tup
	def sort(self,index):
		temp={}
		for frame in self.lines:
			tup=self.lines[frame]()
			temp[tup[index]]=frame
		self.lines={}
		for key in temp:
			song=temp[key].song
			temp[key].destroy()
			self.addsong(song)
class SongLine(Frame):
	def __init__(self,master,song,selected=False):
		Frame.__init__(self,master)
		self.song=song
		binding="<Return>"
		#Set up checkbox
		self.chk=BoolBox(self,selected,command=self.cb)
		self.chk.grid(row=0,column=0)
		#set up title box
		self.title=Entry(self)
		self.title.insert(END,song.get_title())
		self.title.grid(row=0,column=1)
		self.title.bind(binding,self.update)
		#set up artist box
		self.artist=Entry(self)
		self.artist.insert(END,song.get_artist())
		self.artist.grid(row=0,column=2)
		self.artist.bind(binding,self.update)
		#Set up rating spinbox
		self.rating=Spinbox(self,from_=0,to=5,command=self.update)
		self.rating.grid(row=0,column=3)
		self.rating.insert(END,str(song.get_rating()))
	def cb(self,event=None):
		if self.chk.val:
			self.config(bg='blue')
		else:
			self.config(bg='white')
	def get_title(self):
		return self.title.get(0,END)
	def get_artist(self):
		return self.artist.get(0,END)
	def tup(self):
		return (self,self.chk.val,self.get_title(),self.get_artist(),self.rating.get())
	def update(self,event=None):
		tup=self.tup()
		self.song.set_title(tup[2])
		self.song.set_artist(tup[3])
		self.song.set_rating(tup[3])
class AlbumFrame(Frame):
	def __init__(self,master,playlist=None,width=4):
		Frame.__init__(self,master)
		self.playlist=playlist
		self.width=width
		self.row=0
		self.col=0
		self.frames=[]
		if playlist:
			self.addall(playlist.get_albums())
	def add(self,album):
		frame=AlbumIcon(self,album,self.playlist)
		self.frames.append(frame)
		frame.grid(row=self.row,column=self.col)
		self.col+=1
		if self.col>=self.width:
			self.col=0
			self.row+=1
	def addall(self,albums):
		for a in albums:
			self.add(a)
class AlbumIcon(Frame):
	def __init__(self,master,album,playlist):
		Frame.__init__(self,master)
		self.album=album
		#Art icon
		self.art=Label(self)
		self.art.image,self.art.source=album.get_art(playlist)
		self.art.config(image=self.art.image)
		self.art.grid(row=0,column=0,columnspan=2)
		#Album name
		self.title=Label(self,text=album.get_title())
		self.title.grid(row=1,column=0,columnspan=2)
		#Artist name
		self.artist=Label(self,text=album.get_artist())
		self.artist.grid(row=2,column=0,columnspan=2)
		#selection box
		self.select=BoolBox(self,False,command=self.update)
		self.select.grid(row=3,column=0)
		#Binding
		self.bind("<1>",self.select.toggle)
	def update(self):
		if self.select.val:
			self.config(bg='blue')
		else:
			self.config(bg='white')
def format(time):
	secs=int(time)
	mins=int(secs/60.0)
	secs-=mins*60
	hrs=int(mins/60.0)
	mins-=hrs*60
	if hrs==0:
		return "%i:%i" % (mins,secs)
	else:
		return "%i:%i:%i" % (hrs,mins,secs)
def addimg(widget,fname):
	img=PhotoImage(file=fname)
	widget.image=img
	widget.config(image=img)
playimg="data/play.gif"
pauseimg="data/pause.gif"
nextimg="data/next.gif"
previmg="data/prev.gif"
class PlayerFrame(Frame):
	def __init__(self,master,playlist,height=100):
		Frame.__init__(self,master,height=height)
		self.playlist=playlist
		self.seeking=False
		self.firstone=True
		self.thread=None
		#Loop button
		self.loopbtn=BoolBox(self,playlist.is_loop(),text="Loop")
		self.loopbtn.grid(row=0,column=0)
		#Previous button
		self.prevbtn=Button(self,command=self.prev)
		addimg(self.prevbtn,previmg)
		self.prevbtn.grid(row=0,column=1)
		#Playpause button
		self.playpausebtn=Button(self,command=self.playpause)
		addimg(self.playpausebtn,playimg)
		self.playpausebtn.grid(row=0,column=2)
		#Next button
		self.nextbtn=Button(self,command=self.next)
		addimg(self.nextbtn,nextimg)
		self.nextbtn.grid(row=0,column=3)
		#Shuffle button
		self.shufflebtn=BoolBox(self,playlist.is_shuffle(),text="Shuffle")
		self.shufflebtn.grid(row=0,column=4)
		#Currenttime
		self.currtime=Label(self,text=format(0))
		self.currtime.grid(row=1,column=0)
		#scale
		self.scale=Scale(self,from_=0)
		self.scale.grid(row=1,column=1,columnspan=3)
		#self.scale.bind("<ButtonPress-1>",self.md)
		self.scale.bind("<ButtonRelease-1>",self.mu)
		#Runtime
		self.runtime=Label(self,text=format(0))
		self.runtime.grid(row=1,column=4)
	def gettime(self):
		return format(self.scale.get())
	def updateplaylist(self):
		self.playlist.set_loop(self.loopbtn.val)
		self.playlist.set_shuffle(self.shufflebtn.val)
	def md(self,event=None):
		self.seeking=True
	def mu(self,event=None):
		restart=False
		if self.playlist.is_playing():
			self.playpause()
			restart=True
		time=self.scale.get()
		self.playlist.player.seek(time)
		self.seeking=False
		if restart:
			self.playpause()
	def playpause(self,event=None):
		if self.playlist.is_playing():
			self.playlist.pause()
			addimg(self.playpausebtn,playimg)
		else:
			if self.firstone:
				self.playlist.queue()
				self.firstone=False
			self.playlist.play()
			addimg(self.playpausebtn,pauseimg)
			self.thread=self.threadloop(self.scaleloop)
	def next(self,event=None):
		self.playlist.next()
		self.scale.config(to=self.playlist.currentsong.get_duration())
	def prev(self,event=None):
		self.playlist.prev()
		self.scale.config(to=self.playlist.currentsong.get_duration())
	def scaleloop(self):
		while self.playlist.is_playing():
			self.update()
	def update(self):
		song=self.playlist.currentsong
		dur,time=1,0
		if song:
			dur=song.get_duration()
			time=self.playlist.player.time
		if not self.seeking:
			self.scale.set(time)
		self.currtime.config(text=format(time))
		self.runtime.config(text=format(dur))
	def threadloop(self,func):
		from threading import Thread
		t=Thread(target=func)
		t.start()
		return t
	def mousedown(self,event):
		width=self.scale["width"]
		song=self.playlist.currentsong
		if song:
			duration=song.get_duration()
			pos=duration*(event.x/width)
			self.playlist.seek(pos)
constructor=App
def create(func=constructor,foo=None):
	root=Tk()
	if foo:
		app=func(root,foo)
	else:
		app=func(root)
	app.pack()
	app.mainloop()
	try:
		root.destroy()
	except(TclError):
		pass
def thread_create(func=App):
	from threading import Thread
	global constructor
	constructor=func
	t=Thread(target=create)
	t.start()
	return t
class FilterEditor(Frame):
	def __init__(self,master,view=DESIGN,playlist=None,w=300,h=200):
		Frame.__init__(self, master,width=w,height=h)
		self.playlist=playlist
		self.pack()
		if playlist:
			self.master.title('Filter Editor for '+playlist.get_title())
		else:
			self.master.title('Filter Editor')
		self.menu=xmlMenu_by_filename(master,xlistr.HOME+"/data/feMenu.xml",self)
		self.nb=Notebook(self)
		self.nb.enable_traversal()
		self.nb.pack()
		self.view=view
		self.tabs={}
		self.keychars=[]
		self.addtabs(playlist)
	def addtabs(self,playlist):
		if playlist!=None:
			for filt in playlist.get_filters():
				self.add_tab(filt)
	def addtabs_byname(self,filename):
		self.addtabs(Playlist(filename))
	def create_editor_frame(self,filt):
		nb=self.nb
		if self.view==DESIGN:
			return DesignEditor(nb,self,filt)
		elif self.view==CODE:
			return CodeEditor(nb,self,filt)
	def current_id(self):
		return current_id(self.nb)
	def current_editor(self):
		return self.tabs[self.current_id()]
	def add_tab(self,filt):
		frame=self.create_editor_frame(filt)
		frame.pack()
		import os
		name=open(filt.get_href(),'r').name
		segs=name.split(os.sep)
		if len(segs)==1:
			segs=name.split(os.altsep)
		name=segs[len(segs)-1]
		pos=0
		while pos<len(name) and name[pos] in self.keychars:
			pos+=1
		if pos>=len(name):
			self.nb.add(frame,text=name,sticky="n")
		else:
			self.nb.add(frame,text=name,sticky="n",underline=pos)
			self.keychars.append(name[pos])
		self.nb.select(self.nb.tabs()[self.nb.index('end')-1])
		self.tabs[self.current_id()]=frame
	def add_tab_byname(self,filename):
		self.add_tab(new_filter(filename,True,False))
	def newfile(self,filename):
		self.add_tab(new_filter(filename))
	def set_view(self,view):
		self.view=view
		filts=[]
		for key in self.tabs:
			filt=self.tabs[key].filt
			self.nb.forget(key)
			self.tabs[key].destroy()
			filts.append(filt)
		self.tabs={}
		self.keychars=[]
		for filt in filts:
			self.add_tab(filt)
	def toggle_view(self):
		if self.view==DESIGN:
			self.set_view(CODE)
		else:
			self.set_view(DESIGN)
class Editor(Frame):
	def __init__(self,nb,fe,filt):
		Frame.__init__(self, master=nb)
		self.fe=fe
		self.filt=filt
	def get_code(self):
		return ""
	def save(self):
		write_file(self.filt.get_href(),self.get_code())
	def cut(self):
		pass
	def copy(self):
		pass
	def paste(self):
		pass
class DesignEditor(Editor):
	def __init__(self,nb,fe,filt,cols=2,default=True):
		Editor.__init__(self,nb,fe,filt)
		self.genreboxes={}
		Label(self,text="Include:").grid(row=0,columnspan=cols,sticky=W)
		arr={}
		try:
			arr=filt.module.dic
		except(AttributeError):
			pass
		col,row=0,1
		if len(arr)==0:
			arr={'Pop':default,'R&B':default,'Rock':default,'Rap':default,'Spoken Word':default,'Audiobook':default, 'Punk':default,'Metal':default}
		for genre in arr:
			chk=BoolBox(self,arr[genre],text=genre)
			chk.grid(row=row,column=col)
			self.genreboxes[genre]=chk
			col+=1
			if col>=cols:
				col=0
				row+=1
	def get_code(self):
		dic={}
		for genre in self.genreboxes:
			dic[genre]=self.genreboxes[genre].val.get()==1
		content="""g=song.get_genre()
	for genre in dic:
		if (not dic[genre]) and genre==g:
			return False
	return True"""
		return make_code(content,"dic=%i").replace("%i",str(dic))
class CodeEditor(Editor):
	def __init__(self,nb,fe,filt):
		Editor.__init__(self,nb,fe,filt)
		code=""
		if filt is None:
			code=make_code()
		else:
			code=open(filt.get_href(),'r').read()
		self.text=ScrolledText(self)
		self.text.insert(END,code)
		self.text.pack(side=LEFT,fill=BOTH)
	def get_code(self):
		return self.text.get(1.0, END)
	def copy(self):
		self.text.clipboard_clear()
		text = self.text.get("sel.first", "sel.last")
		self.text.clipboard_append(text)
	def cut(self):
		self.copy()
		self.text.delete("sel.first", "sel.last")
	def paste(self):
		text = self.text.clipboard_get()
		self.text.insert('insert', text)#TODO fix
if __name__ == '__main__':
	xlistr.main()
