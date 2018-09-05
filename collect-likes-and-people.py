# This Python file uses the following encoding: utf-8

import config

import json
import twitter
import csv
import re
import os
import logging

# Not enough data in most MP's twitter bios
# def get_type(description):
#     type = ''
#     if re.search(r'\bNDP|ndp|[Nn]ew [Dd]emocrat\b', description, re.IGNORECASE):
#         type = 'NDP'
#     elif re.search(r'\bgreen\b', description, re.IGNORECASE):
#         type = 'Green'
#     elif re.search(r'\b[Ll]iberal\b', description, re.IGNORECASE):
#         type = 'Liberal'
#     elif re.search(r'\b[Bb]loq|BQ\b', description, re.IGNORECASE):
#         type = 'Bloc'
#     elif re.search(r'\b[Cc]on*\b', description, re.IGNORECASE):
#         type = 'Conservative'
#     return type

print('Connecting to Twitter… (pauses to stay under rate limit)')
api = twitter.Api(consumer_key=config.CONSUMER_KEY,
                  consumer_secret=config.CONSUMER_SECRET,
                  access_token_key=config.ACCESS_KEY,
                  access_token_secret=config.ACCESS_TOKEN_SECRET,
                  sleep_on_rate_limit=True)

# mps = api.GetListMembers(slug='mps', owner_screen_name='NZParliament')
mps = api.GetListMembers(slug='canadian-mp-twitter-list', owner_screen_name='cjpac')

mps_latest_fave_status_ids = {}

# Loops through file if exists and creates dictionary of each unique user and the most recent tweet's status id
if os.path.isfile('faves.csv'):
    print('Found existing faves.csv')
    previous_user = None
    with open('faves.csv', 'r') as faves_csv:
        for row in csv.reader(faves_csv):
            current_user = row[0]
            if current_user != previous_user:
                previous_user = current_user
                mps_latest_fave_status_ids[current_user] = row[2]

faved_screennames = set()

# ### Used to get a csv of MP twitter handles to manually label by Party
# m = pd.DataFrame.from_dict(mps_latest_fave_status_ids, orient = 'index')
# m.reset_index(inplace = True)
# m.columns = ['name', 'id']
# m.to_csv('mps.csv')
# ###

with open('faves.csv', 'a') as faves_csv:
    writer = csv.writer(faves_csv)
    if not os.path.isfile('faves.csv'):
        writer.writerow(['from', 'to', 'id', 'text', 'from_screenname', 'to_screenname'])

    for mp in mps:
        since_id = None
        if mp.name in mps_latest_fave_status_ids:
            since_id = mps_latest_fave_status_ids[mp.name]
            print('Looking for tweets for', mp.name, 'after', since_id)
        # If an account is private, a hard error is given and script stops. This try block works around that.
        try:
            favorites = api.GetFavorites(user_id=mp.id, since_id=since_id)
        except Exception:
            pass

        for favorite in favorites:
            print(mp.name, '❤️ ', favorite.user.name, favorite.created_at)
            writer.writerow([mp.name, favorite.user.name, favorite.id, favorite.text, mp.screen_name, favorite.user.screen_name])
            faved_screennames.add(favorite.user.screen_name)

with open('people.csv', 'a') as people_csv:
    writer = csv.writer(people_csv)
    if not os.path.isfile('people.csv'):
        writer.writerow(['label', 'type', 'description', 'screen_name', 'image'])

    for screen_name in faved_screennames:
        # TODO: check whether they're in the MPs list, for setting the type more accurately
        # TODO: check whether user is already in people.csv, and skip if so
        user = api.GetUser(screen_name=screen_name)
        row = user.name, '', user.description, user.screen_name, user.profile_image_url
        writer.writerow(row)

print("New tweets collected:", len(faved_screennames))
