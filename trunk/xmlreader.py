import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element
import pyglet.media as media
import xlistr
import os
if not media.have_avbin:
	xlistr.installAVbin()
#Constants
autosave=True
TITLE     ="title"
CREATOR   ="creator"
ALBUMS    ="albums"
ALBUM     ="album"
SONGS     ="songs"
SONG      ="song"
FILTER    ="filter"
META      ="meta"
POSITION  ="position"
TIME      ="time"
COUNTER   ="counter"
SHUFFLE   ="shuffle"
LOOP      ="loop"
VOLUME    ="volume"
ART       ="art"
ARTIST    ="artist"
YEAR      ="year"
SONGCOUNT ="songcount"
HREF      ="href"
INDEX     ="index"
DURATION  ="duration"
RATING    ="rating"
GENRE     ="genre"
ENABLED   ="enabled"
ALBUMTITLE="albumtitle"
'''
nothing=lambda val:val
common_tags=[TITLE,YEAR,GENRE]
playlist_tags=[ALBUMS,SONGS,META]
playlist_meta_tags=[CREATOR,FILTER,POSITION,TIME,COUNTER,SHUFFLE,LOOP,VOLUME]
album_tags=[ART,ARTIST,YEAR,SONGCOUNT,HREF,GENRE]
song_tags=[ALBUMTITLE,ARTIST,INDEX,HREF,DURATION,RATING,GENRE]
filter_tags=[CREATOR,HREF,ENABLED]
attribset=lambda elem,attr,val:elem.find(attr).set(val)
spec_setters={HREF:attribset,ART:None,ENABLED:attribset,ALBUMS:None,SONGS:None}
spec_getters={META:lambda elem,attr:elem.find(attr)}
casters={INDEX:int,TIME:float,DURATION:float,SONGCOUNT:int,POSITION:int,COUNTER:int,VOLUME:float,YEAR:int,SONGCOUNT:int}
'''
#Functions
def get_elem_text(elem,attr,default=None):
	sub=elem.find(attr)
	if sub!=None:
		return sub.text
	else:
		return default
def set_elem_text(elem,attr,val):
	sub=elem.find(attr)
	if sub is None:
		sub=ET.SubElement(elem,attr)
	sub.text=str(val)
def write_file(filename,text):
	import os
	f=open(os.path.abspath(filename),'w')
	f.write(text)
	f.flush()
	os.fsync(f)
def read_file(filename):
	import os
	return open(os.path.abspath(filename),'r').read()
def new_playlist(title,fname=None,creator="",songs=[],albums=[]):
	if fname==None:
		fname=title.lower()+".xml"
	write_file(fname,'''<?xml version="1.0"?>
<root>
	<meta>
	</meta>
	<albums>
	</albums>
	<songs>
	</songs>
</root>''')
	playlist=Playlist(fname,title,creator)
	for s in songs:
		playlist.add_song(s)
	for a in albums:
		playlist.add_album(a)
	return playlist
def new_song(filename,title=None,artist=""):
	elem=ET.Element(SONG,{HREF:filename})
	import eyeD3
	af=eyeD3.load(filename)
	if title==None:
		title=af.tag.title
	if artist==None:
		artist=af.tag.artist
	res= Song(elem,title=title,artist=artist)
	res.set_genre(af.tag.genre)
	res.set_albumtitle(af.tag.album)
def new_filter(filename,enabled=True,gencode=True):
	if gencode:
		import gui
		write_file(filename,gui.make_code())
	filename=os.path.relpath(filename,xlistr.HOME)
	elem=ET.Element(FILTER,{HREF:filename,ENABLED:str(enabled)})
	return Filter(elem)
def rel_to_abs(path,start):
	start=os.path.abspath(start)
	return os.path.join(os.path.split(start)[0],path)
def randomname(dirname,ext='.py'):
	import random
	name=dirname+os.sep+'temp_'+str(random.randint(0,10**12))+ext
	if os.path.exists(name):
		return randomname(dirname)
	else:
		return name
#Classes
class ElemWrapper(object):
	def __init__(self,elem):
		self.elem=elem
	def get_text(self,attr):
		return self.elem.find(attr).text
class Playlist(ElemWrapper):
	def __init__(self,filename,title=None,creator=None):
		self.filename=filename
		self.tree=ET.parse(filename)
		self.root=self.tree.getroot()
		self.player=media.Player()
		self.player.eos_action=media.Player.EOS_NEXT
		self.player.on_eos=self.queue
		self.player.volume=1.0
		self.tracklog=[]
		self.currentsong=None
		if title!=None:
			self.set_title(title)
		if creator!=None:
			self.set_creator(creator)
	def play(self):
		time=self.get_time()
		pos=self.get_pos()
		songs=self.filtered_songs()
		self.tracklog.append(pos)
		self.currentsong=songs[pos]
		if time!=self.player.time:#seek position
			self.seek(float(time))
		self.player.play()
		self.queue()
	def seek(self,time):
		return self.player.seek(time)
	def pause(self):
		self.player.pause()
		self.set_time(self.player.time)
	def inc_pos(self):
		pos=self.next_pos()
		self.set_pos(self.next_pos())
		return pos
	def next_pos(self):
		pos=self.get_pos()+1
		l=len(self.filtered_songs())
		if self.is_shuffle():
			import random
			rand=lambda :int(random.random()*l)
			pos=rand()
			if len(self.tracklog)==l:
				if self.is_loop():
					self.tracklog=[]
				else:
					return None
			while pos in self.tracklog:
				pos=rand()
		elif pos>=l:
			if self.is_loop():
				pos=0
			else:
				return None
		#self.set_pos(pos)
		return pos
	def next(self):
		self.player.next()
		pos=self.next_pos()
		self.playlist.set_time(0)
		self.tracklog.append(pos)
		self.currentsong=self.playlist.filtered_songs()[pos]
		self.queue()
	def prev(self):
		pos=self.tracklog[len(self.tracklog)-1]
		self.queue(pos)
		self.player.next()
	def queue(self,pos=None):
		if pos==None:
			pos=self.inc_pos()
		if pos!=None:
			self.player.queue(self.filtered_songs()[pos].get_source(self))
		else:
			self.pause()
	def is_playing(self):
		return self.player.playing
	def set_meta(self,attr,val):
		set_elem_text(self.get_meta(),attr,val)
		self.auto_save()
	def set_title(self,title):
		self.set_meta(TITLE,title)
	def set_creator(self,creator):
		self.set_meta(CREATOR,creator)
	def set_pos(self,val):
		self.set_meta(POSITION,val)
	def set_time(self,val):
		self.set_meta(TIME,val)
	def set_count(self,val):
		self.set_meta(COUNTER,val)
	def set_shuffle(self,val):
		self.set_meta(SHUFFLE,val)
	def set_loop(self,val):
		self.set_meta(LOOP,val)
	def set_volume(self,val):
		self.set_meta(VOLUME,val)
	def get_albums(self):
		albums=self.root.find(ALBUMS).findall(ALBUM)
		res=[]
		for al in albums:
			album=Album(al,[self])
			res.append(album)
		return res
	def add(self,attr,elem):
		self.root.find(attr).append(elem)
		self.auto_save()
	def add_album(self,album):
		album.parents.append(self)
		self.add(ALBUMS,album.elem)
	def get_songs(self):
		songs=self.root.find(SONGS).findall(SONG)
		res=[]
		for s in songs:
			song=Song(s,[self])
			res.append(song)
		return res
	def add_song(self,song,position=None):
		song.parents.append(self)
		if position==None:
			self.add(SONGS,song.elem)
		else:
			self.root.find(SONGS).insert(position,song)
	def get_filters(self):
		filters=self.get_meta().findall(FILTER)
		res=[]
		for f in filters:
			res.append(Filter(f,[self]))
		return res
	def add_filter(self,filter):
		filter.parents.append(self)
		self.add(META,filter.elem)
	def save(self):
		self.tree.write(self.filename)
	def auto_save(self):
		if autosave:
			self.save()
	def get_meta(self,attr=None):
		if attr!=None:
			return self.get_meta().find(attr)
		return self.root.find(META)
	def get_meta_text(self,attr,default=None):
		try:
			res= self.get_meta(attr).text
			if res=='None':
				return default
			else:
				return res
		except(AttributeError):
			return default
	def get_title(self):
		default=os.path.split(self.filename)[1].replace('.xml','')
		return self.get_meta_text(TITLE,default)
	def get_creator(self):
		return self.get_meta_text(CREATOR)
	def get_pos(self):
		return int(self.get_meta_text(POSITION,"0"))
	def get_time(self):
		try:
			return float(self.get_meta_text(TIME,"0"))
		except(ValueError):
			self.set_time(0.0)
			return self.get_time()
	def get_count(self):
		return int(self.get_meta_text(COUNTER,"0"))
	def get_meta_bool(self,attr,default=False):
		try:
			txt=self.get_meta_text(attr).lower()
			return txt=="true"
		except(AttributeError):
			return default
	def is_shuffle(self):
		return self.get_meta_bool(SHUFFLE)
	def is_loop(self):
		return self.get_meta_bool(LOOP)
	def get_volume(self):
		return int(self.get_meta_text(VOLUME))
	def test_song(self,song):
		for filt in self.get_filters():
			if filt!=None and filt.is_enabled() and (not filt.test(song)):
				return False
		return True
	def filtered_songs(self):
		return filter(self.test_song,self.get_songs())
class Album(ElemWrapper):
	def __init__(self,elem,parents=[],title=None,artist=None):
		self.elem=elem
		self.parents=parents
		if title!=None:
			self.set_title(title)
		if artist!=None:
			self.set_artist(artist)
	def get_art(self,parent=None):
		filepath=self.elem.find(ART).attrib[HREF]
		if parent:
			filepath=rel_to_abs(filepath,parent.filename)
		import PIL.Image,PIL.ImageTk
		image=PIL.Image.open(filepath)
		return PIL.ImageTk.PhotoImage(image),image
	def set_text(self,attr,val):
		set_elem_text(self.elem,attr,val)
		for parent in self.parents:
			parent.auto_save()
	def get_text(self,attr):
		return get_elem_text(self.elem,attr)
	def get_title(self):
		return self.get_text(TITLE)
	def get_artist(self):
		return self.get_text(ARTIST)
	def get_year(self):
		return int(self.get_text(YEAR))
	def get_songcount(self):
		return int(self.get_text(SONGCOUNT))
	def set_title(self,title):
		self.set_text(TITLE,title)
	def set_artist(self,artist):
		self.set_text(ARTIST,artist)
	def set_art(self,href):
		self.elem.find(ART).attrib[HREF]=href
		for parent in self.parents:
			parent.auto_save()
	def set_year(self,year):
		self.elem.find(YEAR).text=str(year)
	def set_songcount(self,count):
		self.elem.find(SONGCOUNT).text=str(count)
	def add_song(self,song):
		idx=self.get_songcount()+1
		self.set_songcount(idx)
		song.set_index(idx)
		song.set_albumtitle(self.get_title())
	def get_genres(self):
		res=[]
		for song in self.get_songs():
			g=song.get_genre()
			if g not in res:
				res.append(g)
		return res
class Song(ElemWrapper):
	def __init__(self,elem,parents=[],title=None,artist=None):
		self.elem=elem
		self.parents=parents
		if title:
			self.set_title(title)
		if artist:
			self.set_artist(artist)
		if self.get_duration()==0:
			if len(parents)==0:
				self.set_duration(self.get_source().duration)
			else:
				self.set_duration(self.get_source(parents[0]).duration)
	def get_href(self):
		return self.elem.attrib[HREF]
	def get_title(self):
		return get_elem_text(self.elem,TITLE)
	def get_artist(self):
		return self.get_text(ARTIST)
	def get_text(self,attr,default=None):
		res= get_elem_text(self.elem,attr)
		if res:
			return res
		else:
			return default
	def get_albumtitle(self):
		return self.get_text(ALBUMTITLE)
	def get_index(self):
		return int(self.get_text(INDEX,"0"))
	def get_duration(self):
		return float(self.get_text(DURATION,"0"))
	def get_playcount(self):
		return int(self.get_text(COUNTER,"0"))
	def get_rating(self):
		return int(self.get_text(RATING,"5"))
	def get_genre(self):
		return self.get_text(GENRE)
	def get_source(self,parent=None):
		href=self.get_href()
		if parent:
			href=rel_to_abs(href,parent.filename)
		return media.load(os.path.abspath(href))#TODO catch exception, install AVbin
	def set_href(self,val):
		self.elem.set(HREF,str(val))
		for parent in self.parents:
			parent.auto_save()
	def set_text(self,attr,val):
		set_elem_text(self.elem,attr,val)
		for parent in self.parents:
			parent.auto_save()
	def set_title(self,title):
		self.set_text(TITLE,title)
	def set_artist(self,artist):
		self.set_text(ARTIST,artist)
	def set_albumtitle(self,val):
		self.set_text(ALBUMTITLE,val)
	def set_index(self,val):
		self.set_text(INDEX,val)
	def set_duration(self,val):
		self.set_text(DURATION,val)
	def set_playcount(self,val):
		self.set_text(COUNTER,val)
	def set_rating(self,val):
		self.set_text(RATING,val)
	def set_genre(self,val):
		self.set_text(GENRE,val)
class Filter(ElemWrapper):
	def __init__(self,elem,parents=[]):
		self.parents=parents
		self.elem=elem
		self.temp_href=None
		try:
			href=self.elem.attrib[HREF]
		except(KeyError):
			href=randomname(xlistr.HOME+os.sep+'temp')
			write_file(href,self.elem.text)
			self.temp_href=href
		self.load_module()
	def istemp(self):
		return self.temp_href!=None
	def load_module(self):
		href=os.path.relpath(self.get_href(),xlistr.HOME)
		#print href
		self.module=xlistr.import_by_fname(href)
		self.test=self.module.test
	def is_enabled(self):
		txt=self.elem.attrib[ENABLED].lower()
		return txt=="true"
	def set_enabled(self,val):
		self.elem.set(ENABLED,str(val))
		self.auto_save()
	def get_href(self):
		try:
			return self.elem.attrib[HREF]
		except(KeyError):
			return self.temp_href
	def set_href(self,val):
		self.elem.set(HREF,str(val))
		self.auto_save()
	def get_genres(self):
		res=[]
		for p in self.parents:
			for s in p.get_songs():
				g=s.get_genre()
				if g not in res:
					res.append(g)
		return res
	def auto_save(self):
		for parent in self.parents:
			parent.auto_save()
#------------------------------------------------------
#Testing
def test():
	print "testing..."#TODO implement some tests
	raw_input("press enter to exit.")
if __name__ == '__main__':
	test()
