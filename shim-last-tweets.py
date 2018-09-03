# This Python file uses the following encoding: utf-8

import config

import twitter
import pandas

print 'Connecting to Twitter…'
api = twitter.Api(consumer_key=config.CONSUMER_KEY,
                  consumer_secret=config.CONSUMER_SECRET,
                  access_token_key=config.ACCESS_KEY,
                  access_token_secret=config.ACCESS_TOKEN_SECRET,
                  sleep_on_rate_limit=False)

faves = pandas.read_csv('faves.csv')

faves_lacking_text = faves.loc[faves['text'].isnull()]

statuses = api.GetStatuses(status_ids=faves_lacking_text['id'], trim_user=True, include_entities=False)

for status in statuses:
    try:
        faves.loc[faves['id'] == status.id, 'text'] = status.text
    except:
        print "some error with", status.id, status.text

faves.to_csv('missing-statuses.csv', encoding='utf-8', index=False)
