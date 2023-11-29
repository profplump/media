#!/usr/bin/python3

# Imports
import re
import os
import pathlib
import argparse

# CLI config
parser = argparse.ArgumentParser('MergeSubs')
parser.add_argument('path', type=pathlib.Path, help='Path to the base media file')
parser.add_argument('--verbose', '-v', action=count, default=0, help='Increasing verbosity')
cli = parser.parse_args()
if not os.path.isdir(cli.path):
  print('Invalid path: {path}'.format(path=cli.path))
  exit(1)

