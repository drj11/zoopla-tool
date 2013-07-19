#!/usr/bin/env python

from collections import Counter,OrderedDict
import json
import sys
import codecs
sys.stdout = codecs.getwriter('utf8')(sys.stdout)

import requests
from lxml import etree
import scraperwiki

ZOOPLA_KEY = open("tool/zoopla.key").read().strip()

def subTagText(element, tag):
    """Get the descendent of *element* with *tag*;
    return its text. If there is more than one descendent
    with that tag, return the text of the first one.
    If no descendent, or the descendent is empty, returns None.
    """
    subs = element.xpath('./' + tag)
    if not subs:
        return None
    sub = subs[0]
    if sub is None:
        return None
    try:
        return float(sub.text)
    except (TypeError, ValueError):
        pass
    return sub.text

def propertyListings(**kwargs):
    r = requests.get("http://api.zoopla.co.uk/api/v1/property_listings",
      params=dict(api_key=ZOOPLA_KEY,
        radius=1.2,
        property_type='houses',
        listing_status='sale',
        ordering='ascending',
        page_size=100,
        **kwargs))
    with codecs.open('response.xml', 'w', 'utf-8') as f:
        f.write(r.text)

    propertyListingsFromString(r.text.encode('utf-8'))

def propertyListingsFromString(response):
    """Save the list of properties. Takes the XML response
    as a python string (not unicode)."""

    root = etree.XML(response)
    scraperwiki.sql.execute('drop table if exists House')
    scraperwiki.sql.execute('drop table if exists property')
    allTags = Counter()
    for el in root.xpath('/response/listing'):
      for subel in el:
        allTags[subel.tag] +=1
      d = OrderedDict()
      for tag in ['listing_id', 'price', 'image_url',
        'displayable_address',
        'details_url',
        'latitude', 'longitude', 'short_description',
        'floor_plan',
        'num_bedrooms',
        'num_bathrooms',
        # 'num_floors', # Always 0
        'num_recepts',
        'outcode',
        'first_published_date'
        ]:

        d[tag] = subTagText(el, tag)
      if d['listing_id']:
        scraperwiki.sql.save(['listing_id'], d, table_name='House')
    with open('xmltags.json', 'w') as f:
        json.dump(allTags, f)

def main(argv=None):
    import getopt
    if argv is None:
        argv = sys.argv
    opts,arg = getopt.getopt(argv[1:], '', ['xml='])
    for o,v in opts:
        if o == '--xml':
            propertyListingsFromString(open(v).read())
            return
    postcode = arg[0]
    propertyListings(postcode=postcode)

if __name__ == '__main__':
    main()
