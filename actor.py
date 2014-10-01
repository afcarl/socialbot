import json
import twitter
import json
import time
from datetime import datetime
from numpy import random

class Actor(object):
	def __init__(self,path='/home/ubuntu/'):
			keys = json.loads(file(path + 'auth.json').read())

			auth = twitter.OAuth(keys['OAUTH_TOKEN'], keys['OAUTH_TOKEN_SECRET'],
                            keys['APP_KEY'], keys['APP_SECRET'])

			self.api = twitter.Twitter(auth=auth)
			self.path = path

	def unfollow(self, count = 1):
		bad_friends = json.load(open(self.path + 'data/bad_friends.json'))
		for i in range(count):
			if len(bad_friends) > 0:
				usr_id = bad_friends.pop()
				print 'Destroying friendship: ' + str(usr_id)
				self.api.friendships.destroy(user_id = usr_id)
		if len(bad_friends) == 0:
			bad_friends = []
		json.dump(bad_friends, open(self.path + 'data/bad_friends.json','wb'))
		return count     # no. api calls

	def follow(self, favoritetwt = True, count = 1):
		new_friends = json.load(open(self.path + 'data/new_friends.json'))
		for i in range(count):
			if len(new_friends) > 0:
				usr_id = new_friends.pop()
				print 'Created friendship: ' + str(usr_id)
				self.api.friendships.create(user_id = usr_id)
				if favoritetwt:
					status = self.api.statuses.user_timeline(user_id=usr_id, count = 1)[0]  # can be extended to favorite random twt
					to_favorite = json.load(open(self.path + 'data/to_favorite.json'))
					print 'Added status: ' + str(status) + ' for future favorite.' 
					json.dump(to_favorite.append(status['id']), open(self.path + 'data/to_favorite.json', 'wb'))
		if len(new_friends) == 0:
			new_friends = []
		json.dump(new_friends, open(self.path + 'data/new_friends.json','wb'))
		calls = count 
		if favoritetwt:
			calls += count
		return calls  # no. api calls

	def favoritePost(self, count = 1):  # Error in api ?
		to_favorite = json.load(open(self.path + 'data/to_favorite.json'))
		for i in range(count):
			if len(to_favorite) > 0:
				status_id = to_favorite.pop()
				print 'Favoriting status: ' + str(status_id)
				self.api.favorites.create(_id = status_id)
		if len(to_favorite) == 0:
			to_favorite = []
		json.dump(to_favorite, open(self.path + 'data/to_favorite.json', 'wb'))
		return count # no. api calls

	def postTwt(self, lat = 57.718524, lon = 11.983428):
		twts = [json.loads(line) for line in open(self.path + 'data/to_tweet.json')]
		lat = lat + random.normal(0,0.02)
		lon = lon + random.normal(0,0.02)
		if len(twts) > 0:
			twt = twts.pop()
			print 'Posting twt: ' + twt['text']
			self.api.statuses.update(status = twt['text'], lat = lat, long=lon)
		if len(twts) == 0:
			open(self.path + 'data/to_tweet.json','wb').write('')
		else:
			json.dump(twts, open(self.path + 'data/to_tweet.json','wb'))
		return 1  # no. api calls

	def retweet(self): #test method
		retwts = json.load(open(self.path + 'data/retweets.json'))
		if len(retwts) > 0:
			twt = retwts.pop()
			print 'Retweeting: ', twt
			self.api.statuses.retweet(id=twt)
		json.dump(retwts,open(self.path + 'data/retweets.json','wb'))
		return 1

	def send_log(self, method):
		msg = "Running routine", datetime.now(), method
		self.api.direct_messages.new(screen_name="SuperRexy",text=msg)

	def write_log(self, method):
		msg = "Running routine", datetime.now(), method, '\n'
		open(self.path + 'data/hiri.log','a').write(msg)


if __name__ == '__main__':
	#initial wait:
	#time.sleep(random.uniform(1,30))
	actor = Actor()

	counts = {'post':0, 'retwt':0, 'fol':0, 'unfol':0}
	maxes = {'post':1, 'retwt':1 , 'fol':25, 'unfol':25}
	methods = ['post', 'retwt', 'fol', 'unfol']
	start = time.time()

	while time.time() - start < 3600 or counts['post'] != 1:
		probs = [maxes[key] - counts[key] for key in methods]
		probs = [1.0*elm/sum(probs) for elm in probs]
		
		method = random.choice(methods, size = 1, replace = False, p = probs)[0]
		if method == 'post':
			actor.postTwt()
		elif method == 'retwt':
			actor.retweet()
			#actor.favoritePost()
			#counts['fav'] += 1
			#if counts['fav'] > maxes['fav']:
			#	counts['fav'] = maxes['fav']
		elif method == 'fol':
			actor.follow(favoritetwt = False)
		elif method == 'unfol':
			actor.unfollow()
		counts[method] += 1
		if counts[method] > maxes[method]:
			counts[method] = maxes[method]
		
		wait_time = random.poisson(1*60)
		actor.write_log(method)
		print method
		time.sleep(wait_time)

