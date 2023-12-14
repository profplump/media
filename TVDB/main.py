# Imports
import re
import os
import pathlib
import argparse
from datetime import datetime
import tvdb_v4_official

# Default config
default_apikey = os.path.expanduser('~/.tvdb_apikey')
default_lang   = 'eng'
default_order  = 'default'

# Local helpers
def readConfigLine(file, opt=False):
  value = None
  try:
    with open(file, 'r') as f:
      for line in f:
        if re.match('^\s*#', line):
          continue
        else:
          value = line.strip()
          break
  except Exception as error:
    if not opt:
      print('Unable to read config: {e}'.format(e=error))
  return value

# CLI config
parser = argparse.ArgumentParser('TVDB Renamer')
parser.add_argument('--verbose', '-v', action='store_true', help='Display debug and episode data')
parser.add_argument('--api', default=default_apikey, help='Path to a file containing the TVDB API key')
parser.add_argument('--lang', '-l', help='Force TVDB language code')
parser.add_argument('--order', '-o', help='Force TVDB order type')
parser.add_argument('path', type=pathlib.Path, help='The directory containing files to be renamed')
cli = parser.parse_args()
if not os.path.isfile(cli.api):
  print('Invalid API key file path: {path}'.format(path=cli.api))
  exit(1)
if not os.path.isdir(cli.path):
  print('Invalid path: {path}'.format(path=cli.path))
  exit(1)
if cli.lang == 'None' or cli.lang == '':
  cli.lang = None
if cli.verbose:
  print('Path: {p}'.format(p=cli.path))
  print('Forced Lang/Order: {l}/{o}'.format(l=cli.lang, o=cli.order))

# Move to keep the file paths flat
try:
  os.chdir(cli.path)
except Exception as error:
  print('Unable to move to target directory: {e}'.format(e=error))
  exit(1)

# Read the local directory
seasons = {}
try:
  dirfiles = os.listdir('.')
except Exception as error:
  print('Unable to read to target directory: {e}'.format(e=error))
  exit(1)
for file in dirfiles:
  f = {}
  f['file'] = file
  try:
    split = os.path.splitext(file)
    f['base'] = split[0]
    f['extension'] = split[1]
    se = re.search('S(\d+)E(\d+)', file, flags=re.IGNORECASE)
    if se is None:
      # Does not contain a season/episode block
      continue
    f['season'] = int(se.group(1))
    f['number'] = int(se.group(2))
    if not f['season'] in seasons:
      seasons[ f['season'] ] = {}
    if not f['number'] in seasons[ f['season'] ]:
      seasons[ f['season']  ][ f['number'] ] = []
    seasons[ f['season'] ][ f['number'] ].append(f)
  except Exception as error:
    print('Unable to parse filename "{f}": {e}'.format(e=error, f=file))
    continue

# Fetch the TVDB episode list
try:
  apikey = readConfigLine(cli.api)
  id = readConfigLine('.tvdb')

  if cli.lang is not None:
    lang = cli.lang
  else:
    lang = readConfigLine('.tvdb_lang', opt=True)
  if lang is None:
    lang = default_lang

  if cli.order is not None:
    order = cli.order
  else:
    order = readConfigLine('.tvdb_order', opt=True)
  if order is None:
    order = default_order

  if apikey is None or id is None:
    print('Invalid TVDB parameters')
    exit(1)
  if cli.verbose:
    print('Series: {id}'.format(id=id))
    print('Lang/Order: {l}/{o}'.format(l=lang, o=order))

  tvdb = tvdb_v4_official.TVDB(apikey)
  if lang is None:
    series = tvdb.get_series(id=id)
  else:
    series = tvdb.get_series_translation(id=id, lang=lang)
  data = tvdb.get_series_episodes(id=id, lang=lang, season_type=order)
  del tvdb
  del id
  del apikey
except Exception as error:
  print(
    "Unable to fetch series {id}: {e}\nSeries:\n{s}\nEpisodes:\n{ep}".format(
      id=id, e=error, s=series, ep=data
    )
  )
  exit(1)

# Parse and clean the data we need
episodes = []
try:
  series_name = series['name'].strip()
  if cli.verbose:
    print('Series: {name}'.format(name=series_name))
  for episode in data['episodes']:
    e = {}
    e['series'] = series_name
    e['season'] = int(episode['seasonNumber'])
    e['number'] = int(episode['number'])
    e['name'] = episode['name'].strip()
    e['date'] = None if episode['aired'] is None else datetime.strptime(episode['aired'], '%Y-%m-%d')
    e['description'] = '' if episode['overview'] is None else episode['overview'].strip()
    e['filename'] = '{series} - S{season:02d}E{number:02d} - {name}'.format(
      series=e['series'], season=e['season'], number=e['number'], name=e['name']
    )
    e['filename'] = e['filename'].replace(':', ' -').replace('/', ' - ').replace('  ', ' ')
    episodes.append(e)
except Exception as error:
  print('Unable to parse episode data: {e}'.format(e=error))
  exit(1)

# Find unexpected episodes
if cli.verbose:
  db_seasons = {}
  for e in episodes:
    if not e['season'] in db_seasons:
      db_seasons[ e['season'] ] = {}
    if not e['number'] in db_seasons[ e['season'] ]:
      db_seasons[ e['season'] ][ e['number'] ] = True
  for snum, s in seasons.items():
    for enum, elist in s.items():
      for e in elist:
        if (
          not e['season'] in db_seasons or
          not e['number'] in db_seasons[ e['season'] ]
        ):
          print('Unexpected: {f}'.format(f=e['file']))
  del db_seasons

# Rename matched files
for e in episodes:
  if (
    not e['season'] in seasons or
    not e['number'] in seasons[ e['season'] ]
  ):
    if cli.verbose:
      if e['date'] is None or e['date'] <= datetime.today():
        print('Missing: {m}'.format(m=e['filename']))
    continue
  files = seasons[ e['season'] ][ e['number'] ]
  for file in files:
    if file['base'] != e['filename']:
      src = file['file']
      dest = e['filename'] + file['extension']
      print('Rename\n\t{s}\n\t{d}'.format(s=src, d=dest))
      if (
        os.path.exists(dest) and
        file['base'].casefold() != e['filename'].casefold()
      ):
        print('Target exists: {d}'.format(d=dest))
        continue
      try:
        os.rename(src, dest)
      except Exception as error:
        print('Unable to rename {s}: {e}'.format(s=src, e=error))
        continue
    else:
      if cli.verbose:
        print('Found: {m}'.format(m=e['filename']))
