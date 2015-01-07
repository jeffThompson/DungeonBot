
'''
DUNGEON BOT
Jeff Thompson | 2013 | www.jeffreythompson.org

Forever trapped, a bot-wanderer walks through 
a 9x9-section of an infinite dungeon. No treasure,
no enemies - just endless wandering...

'''

from OAuthSettings import settings				# import from settings.py
from random import random						# randomize tiles and direction
from random import randrange
import numpy as np								# for 2D array manipulation
import os										# for misc file handling duties
from sys import exit							# for exiting when done posting
import twitter									# for posting to Twitter

def generate_text():
	amount = [ 'a little', 'more', 'a hint of', 'only' ]
	pos_nouns = [ 'hope', 'fresh air', 'dim light' ]
	neg_nouns = [ 'gray', 'moss', 'gloom', 'weariness', 'putrid water', 'dripping slime', 'darkness', 'musty air', 'danger', 'cold', 'gravel', 'loose stone', 'dripping', 'echoes in the dark', 'fear', 'sleep', 'hunger', 'stench', 'bats', 'creaking in the distance' ]
	hopeless_nouns = [ 'terror', 'peril', 'despair', 'sadness', 'hopelessness' ]
	
	if random() < chance_nothing:											# nothing
		return '...'
	else:																	# something
		text = ''
		if random() < chance_amount:										# add amount word
			text += amount[randrange(0, len(amount))] + ' '
		if random() < chance_positive:										# noun
			text += pos_nouns[randrange(0, len(pos_nouns))]
		elif random() < chance_hopeless:
			text += hopeless_nouns[randrange(0, len(hopeless_nouns))]
		else:
			text += neg_nouns[randrange(0, len(neg_nouns))]
		
		return text															# return resulting text


# LEVEL VARIABLES
create_new_level =  False			# generate a brand new level?
input_filename = 	'level.txt'		# filename to read/write
width = 			9				# level dimensions
height = 			9
x = 				4				# player's placement in the level
y = 				4
chance_wall = 		0.3				# chance a wall will be generated
dir = 				'N'				# direction of move (updated from file and move direction)
iteration = 		1				# how many moves have we made?
chance_amount = 	0.3
chance_positive = 	0.5
chance_hopeless = 	0.001
chance_nothing = 	0.05
chance_sleep = 		0.05

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


# PLAYER/TILE VARIABLES
player = u'\u25B2'.encode('utf-8')
player_N = u'\u25B2'.encode('utf-8')
player_E = u'\u25B6'.encode('utf-8')
player_S = u'\u25BE'.encode('utf-8')
player_W = u'\u25C0'.encode('utf-8')

print player_S

white = u'\u25FB'.encode('utf-8')
black = u'\u25FC'.encode('utf-8')

terrain = [ 'o', 'b' ]


# LOAD OAUTH DETAILS FROM FILE TO ACCESS TWITTER
# see notes at top for format
consumer_key = settings['consumer_key']
consumer_secret = settings['consumer_secret']
access_token_key = settings['access_token_key']
access_token_secret = settings['access_token_secret']


# CLEAR SCREEN
print '\n\n'
os.system('cls' if os.name=='nt' else 'clear')
print '\nI AM A WANDERER, TRAPPED IN AN INFINITE DUNGEON.\n'


# CREATE LEVEL
if create_new_level:
	print 'creating new level...'
	level_list = []
	for ty in range(height):
		chars = []
		for tx in range(width):
			if random() > chance_wall or tx == x and ty == y:
				chars.append('o')
			else:
				chars.append('b')
				# chars.append(terrain[randrange(0,len(terrain))])
		level_list.append(chars)
	level = np.array(level_list)


# LOAD PREVIOUS LEVEL
else:
	print 'loading level from file...'
	level_list = []
	iteration = 0
	with open(os.path.join(__location__, input_filename)) as file:
		for i, line in enumerate(file):
			if i != height:
				chars = []
				for c in line.strip():
					chars.append(c)
				level_list.append(chars)
			else:
				data = line.strip().split(',')
				dir = data[0]
				iteration = int(data[1])
				chance_positive = float(data[2])
				chance_hopeless = float(data[3])
	level = np.array(level_list)


# SLEEP OR NEXT MOVE
if random() < chance_sleep:
	tweet = 'Now I sleep, and save my strength...'

else:
	print 'moving player, updating level...'
	move = randrange(0,4)
	for i in range(move, move+4):
		if (i%4) == 0 and level.item((y-1,x)) != 'b':		# U
			dir = 'N'
			# player = player_N
			level = np.roll(level, 1, axis=0)
			for tx in range(width):
				if random() < chance_wall:
					level[height-1,tx] = 'b'
				else:
					level[height-1,tx] = 'o'
			break
		
		elif (i%4) == 1 and level.item((y,x+1)) != 'b':		# R
			dir = 'E'
			# player = player_E
			level = np.roll(level, -1, axis=1)
			for ty in range(height):
				if random() < chance_wall:
					level[ty,width-1] = 'b'
				else:
					level[ty,width-1] = 'o'
			break
		
		elif (i%4) == 2 and level.item((y+1,x)) != 'b':		# D
			dir = 'S'
			# player = player_S
			level = np.roll(level, -1, axis=0)
			for tx in range(width):
				if random() < chance_wall:
					level[0,tx] = 'b'
				else:
					level[0,tx] = 'o'
			break
		
		elif (i%4) == 3 and level.item((y,x-1)) != 'b':		# L
			dir = 'W'
			# player = player_W
			level = np.roll(level, 1, axis=-1)
			for ty in range(height):
				if random() < chance_wall:
					level[ty,0] = 'b'
				else:
					level[ty,0] = 'o'
			break


	# FORMAT TWEET FROM LEVEL
	tweet = ''
	for ty in range(height):
		for tx in range(width):
			tile = level[ty,tx]
			if tx == x and ty == y:
				tweet += player
			elif tile == 'b':
				tweet += black
			else:
				tweet += white
		tweet += '\n'

	# ADD RANDOMIZED TEXT
	tweet += generate_text()
	chance_positive *= 0.999
	chance_hopeless *= 1.001


# ADD DIRECTION AND ITERATION
# tweet += dir + ' (' + '{0:06d}'.format(iteration) + ')'
# tweet += dir + ' (' + str(iteration) + ')'


# CONNECT TO TWITTER API, POST and PRINT RESULT
print '\n' + tweet + '\n'
try:
	api = twitter.Api(consumer_key = consumer_key, consumer_secret = consumer_secret, access_token_key = access_token_key, access_token_secret = access_token_secret)
	print 'posting to Twitter...'
	status = api.PostUpdate(tweet)
	print '  post successful!'
except twitter.TwitterError:
	print '  error posting!'


# SAVE TO FILE
print 'saving updated level to file...'
iteration += 1
with open(os.path.join(__location__, input_filename), 'w') as file:
	for ty in range(height):
		line = ''
		for tx in range(width):
			line += level[ty,tx]
		file.write(line + '\n')
	file.write(dir + ',' + str(iteration) + ',' + str(chance_positive) + ',' + str(chance_hopeless))


# ALL DONE!
print ('\n' * 2)
exit()

