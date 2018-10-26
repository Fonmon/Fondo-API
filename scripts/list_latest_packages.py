#!/usr/bin/python
import urllib.request
import json

pypi_url = "https://pypi.org/pypi/{}/json"

file = open('../requirements.txt', 'r')

for line in file.readlines():
    index = line.find('=')
    package = line[:index]
    contents = urllib.request.urlopen(pypi_url.format(package)).read()
    json_content = json.loads(contents)
    print(package, json_content['info']['version'])

file.close()
