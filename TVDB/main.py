# Imports
import re
import os
import argparse
from datetime import datetime
import tvdb_v4_official

# Default config
default_apikey = os.path.expanduser('~/.tvdb_apikey')

# Local helpers
def readConfigLine(file):
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
    print('Unable to read config: {e}'.format(e=error))
  return value

# CLI config
parser = argparse.ArgumentParser('TVDB Renamer')
parser.add_argument('path', help='The directory containing files to be renamed')
parser.add_argument('--api', default=default_apikey, required=False, help='Path to a file containing the TVDB API key')
cli = parser.parse_args()
if not os.path.isfile(cli.api):
  print('Invalid API key file path: {path}'.format(path=cli.api))
  exit(1)
if not os.path.isdir(cli.path):
  print('Invalid path: {path}'.format(path=cli.path))
  exit(1)

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
  series = readConfigLine('.tvdb')
  if apikey is None or series is None:
    print('Invalid TVDB parameters')
    exit(1)
  tvdb = tvdb_v4_official.TVDB(apikey)
  data = tvdb.get_series_episodes(series)
  del tvdb
  del series
  del apikey
except Exception as error:
  print('Unable to fetch series {id}: {e}'.format(id=series, e=error))
  exit(1)

# Parse and clean the data we need
episodes = []
try:
  seriesName = data['series']['name'].strip()
  for episode in data['episodes']:
    e = {}
    e['series'] = seriesName
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

# Rename matched files
for e in episodes:
  if (
    not e['season'] in seasons or
    not e['number'] in seasons[ e['season'] ]
  ):
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
