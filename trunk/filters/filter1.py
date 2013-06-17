dic={'Metal': True, 'Spoken Word': True, 'Audiobook': False, 'Punk': True, 'Pop': False, 'R&B': False, 'Rap': True, 'Rock': False}
def test(song):
	g=song.get_genre()
	for genre in dic:
		if (not dic[genre]) and genre==g:
			return False
	return True