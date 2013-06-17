import pyglet
import pyglet.media as media
from threading import Thread
def threadrun(target=pyglet.app.run,**kw):
  t=Thread(target=target,kwargs=kw)
  t.start()
  return t
def printtimes(**kw):
  player=kw['player']
  src=kw['src']
  while player.time<src.duration:
    print player.time,'/',src.duration
def main():
  print media.driver
  fname='D:\\Music\\JRR Tolkien\\LotR Part I The Fellowship of the Ring\\01-- 0001 Credits.mp3'
  src=media.load(fname)
  print "source loaded:"+str(src)
  player=media.Player()
  print 'Player created'
  player.queue(src)
  print 'source queued'
  player.volume=1.0
  print 'volume set'
  #player.seek(2.5)
  #print 'seeked'
  player.play()
  print 'playing'
  threadrun(printtimes,player=player,src=src)
  try:
    t=threadrun()
    #pyglet.app.run()
    print 'run started'
  except KeyboardInterrupt:
    print 'error'
    player.next()
    print 'next'
  
if __name__=="__main__":
  main()
