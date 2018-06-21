#!/usr/bin/env python

import os
import json
import requests
import subprocess

KEY = os.environ['AIRTABLE_KEY']
API_BASE = 'https://api.airtable.com/v0/apph6Hzhk8tmLKXl8/'

api = requests.Session()
api.headers.update({'Authorization': 'Bearer %s' % KEY})

def write_book(name):
    print('Generating %s' % name)
    offset = None
    slug = get_slug(name)
    tex_filename = '%s.tex' % slug
    output = open(tex_filename, "wt")
    output.write(
    r"""
    \documentclass{article}
    \usepackage{graphicx}

    \begin{document}

    """)

    while True:
        filterf = '(FIND("%s",{Flag for External Identification}))' % name
        resp = api.get(
            API_BASE + 'Lakeland Photos ALL', 
            params={
                'filterByFormula': filterf,
                'offset': offset
            }
        )
        results = resp.json()

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

    proc = subprocess.Popen(['pdflatex', tex_filename], stdout=subprocess.DEVNULL)
    proc.communicate()

    os.remove(tex_filename)
    os.remove('%s.log' % slug)
    os.remove('%s.aux' % slug)
    os.rename('%s.pdf' % slug, 'books/%s.pdf' % slug)

def get_slug(s):
    return s.lower().replace('&', '').replace(' ', '-')

write_book('Diane Ligon')
write_book('George & Sissy Randall')
write_book('Jean Adams')
write_book('Delphine Gross')



