# This Python file uses the following encoding: utf-8

import config

from distutils.util import strtobool
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe

print('Connecting to Google Sheet…')
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_dict(config.JSON_KEYFILE, scope)
gc = gspread.authorize(credentials)
sheets = gc.open_by_key(config.GOOGLE_SHEET_KEY)

print('Loading csv')
faves = pd.read_csv('faves.csv')

print('Adding up multiple tweets favorited by & from the same people')
faves_added = faves.pivot_table(index=['from','to'], values=['id','text'], aggfunc={'id':'count','text':'last'})
faves_added.reset_index(level=['from', 'to'], inplace=True)
faves_added.columns = ['from', 'to', 'faves', 'last_tweet']

print('Counting number of times each person has been favorited')
favees = faves.pivot_table(index=['to'], values=['from'], aggfunc='count')
favees.reset_index(level=['to'], inplace=True)
favees.columns = ['label','favees']

people = pd.read_csv('people.csv')
people.drop_duplicates(subset=['label'], inplace=True)
people = pd.merge(people, favees, how='outer', on=['label', 'label'])

print('Labeling people with less than 2 favees as singletons')
people.loc[(people['favees'] < 2) & (people['type'].isnull()), ['type']] = 'singleton'

print('Labelling MP accounts with their Party affiliation')
party = pd.read_csv('mps2.csv')
people = pd.merge(people, party, how = 'outer', on = ['label', 'label'])
people['type'] = people['party']
people.drop('party', axis = 1, inplace = True)

confirm = input('OK to delete & replace worksheets? (Y/n) ')
if confirm is '' or strtobool(confirm):
    print("Deleting")
    try: # currently needs one useless worksheet hanging about (can't delete all sheets)
        sheets.del_worksheet(sheets.worksheet('faves'))
        sheets.del_worksheet(sheets.worksheet('people'))
    except: print("Couldn't delete")

    print("Creating new worksheets")
    faves_worksheet = sheets.add_worksheet(title="faves", rows=faves_added.shape[0], cols=faves_added.shape[1])
    people_worksheet = sheets.add_worksheet(title="people", rows=people.shape[0], cols=people.shape[1])
    print("Uploading faves")
    set_with_dataframe(faves_worksheet, faves_added)
    print("Uploading people")
    set_with_dataframe(people_worksheet, people)
