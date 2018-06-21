#!/usr/bin/env python

import os
import json
import requests

KEY = os.environ['AIRTABLE_KEY']
API_BASE = 'https://api.airtable.com/v0/apph6Hzhk8tmLKXl8/'

api = requests.Session()
api.headers.update({'Authorization': 'Bearer %s' % KEY})

offset = None
output = open("images.latex", "wt")
output.write(
r"""
\documentclass{article}
\usepackage{graphicx}

\begin{document}

""")

while True:
    results = api.get(API_BASE + 'Lakeland Photos ALL', params={'filterByFormula': '(FIND("dligon",{File Paths}))', 'offset': offset}).json()
    for record in results['records']:
        fields = record.get('fields', {})
        url = fields.get('URL')

        if not url:
            continue

        filename = url.split('/')[-1]
        path = 'images/' + filename

        if not os.path.isfile(path):
            with open(path, 'wb') as file:
                response = requests.get(url)
                file.write(response.content)

        output.write(
"""

\\begin{{figure}}
    \\includegraphics[width=\\linewidth]{{{path}}}
    \\caption{{{filename}}}
    \\label{{{filename}}}
\\end{{figure}}

\\clearpage

""".format(path=path, filename=filename))

    offset = results.get('offset', None)

    if offset is None:
        break

output.write("\end{document}")
output.close()


