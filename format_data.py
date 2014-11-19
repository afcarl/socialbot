import json
import pandas as pd
import time
from datetime import datetime

followers = json.loads(file('../data/followers.json').read())

df_times = pd.DataFrame.from_csv('foltimes.csv')


# load all profiles we have tried to follow
f = open('../data/tried_to_follow.json','r')

lines = f.read().split('\n')[:-1]

records = []

for line in lines:
	records.append(json.loads(line))

seen_users = []

data = []
for record in records:
	uid = record['id']
	tz = record['time_zone']
	fol_count = record['followers_count']
	fri_count = record['friends_count']
	created_at = record['created_at']
	created_at_time_struct = time.strptime(created_at,"%a %b %d %H:%M:%S +0000 %Y")
	timestamp = time.mktime(created_at_time_struct)
	language = record['lang']
	twt_count = record['statuses_count']
	fav_count = record['favourites_count']
	followback = uid in followers
	row = {
		'uid':uid,
		'tz':tz,
		'fol_count':fol_count,
		'fri_count':fri_count,
		'created_at':timestamp,
		'language':language,
		'twt_count':twt_count,
		'fav_count':fav_count,
		'followback':followback
	}
	if uid not in seen_users:
		data.append(row)
		seen_users.append(uid)

dataframe = pd.DataFrame(data)

alldata = dataframe.merge(df_times,on='uid')

alldata.to_csv('dataframe.csv')
