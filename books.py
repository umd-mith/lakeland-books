#!/usr/bin/env python

import os
import re
import sys
import json
import jinja2
import datetime
import requests
import subprocess

KEY = os.environ['AIRTABLE_KEY']
API_BASE = 'https://api.airtable.com/v0/apph6Hzhk8tmLKXl8/'

api = requests.Session()
api.headers.update({'Authorization': 'Bearer %s' % KEY})

env = jinja2.Environment(
    loader=jinja2.FileSystemLoader('templates')
)

try:
    template = env.get_template('book.tex')
except jinja2.TemplateSyntaxError as e:
    print("jinja2 parse error: {} in {} at {}".format(e.message, e.filename, e.lineno))
    sys.exit()

def write_book(name):

    print('Generating %s' % name)

    # collect the images from the AirTable
    offset = None
    images = []

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

            images.append({"path": path, "filename": filename})

        offset = results.get('offset', None)

        if offset is None:
            break

    # write the tex file using the template
    slug = get_slug(name)
    tex_filename = '%s.tex' % slug
    with open(tex_filename, 'w') as output:
        output.write(template.render(
            name=name.replace('&', 'and'),
            images=images,
            date=datetime.date.today().strftime('%B %-d, %Y')
        ))

    # lean on pdflatex to conver the tex to pdf
    proc = subprocess.Popen(['pdflatex', tex_filename], stdout=subprocess.DEVNULL)
    proc.communicate()

    # clean up everything but the pdf
    os.remove(tex_filename)
    os.remove('%s.log' % slug)
    os.remove('%s.aux' % slug)
    os.rename('%s.pdf' % slug, 'books/%s.pdf' % slug)

def get_slug(s):
    return re.sub(' +', '-', s.lower().replace('&', ''))

write_book('Diane Ligon')
write_book('George & Sissy Randall')
write_book('Jean Adams')
write_book('Delphine Gross')



