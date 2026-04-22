#!/usr/bin/env python3
"""Usage: get_release_url.py <pattern>
Reads GitHub release JSON from stdin, prints the browser_download_url
of the first asset whose name matches the given regex pattern.
"""
import sys
import json
import re

assets = json.load(sys.stdin)['assets']
pat = sys.argv[1]
matches = [a['browser_download_url'] for a in assets if re.search(pat, a['name'])]
print(matches[0] if matches else '')
