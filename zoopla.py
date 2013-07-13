#!/usr/bin/env python

from collections import OrderedDict
import sys
import codecs
sys.stdout = codecs.getwriter('utf8')(sys.stdout)

import requests
from lxml import etree
import scraperwiki

ZOOPLA_KEY = open("tool/zoopla.key").read().strip()
POSTCODE = sys.argv[1]

def subTagText(element, tag):
    """Get the descendent of *element* with *tag*;
    return its text."""
    subs = element.xpath('./' + tag)
    if not subs:
        return None
    sub, = subs
    if sub is None:
        return None
    try:
        return float(sub.text)
    except (TypeError, ValueError):
        pass
    return sub.text

def propertyListings():
    r = requests.get("http://api.zoopla.co.uk/api/v1/property_listings",
      params=dict(api_key=ZOOPLA_KEY,
        postcode=POSTCODE, radius=1.2,
        property_type='houses',
        listing_status='sale',
        ordering='ascending',
        page_size=100))
    print r.text
    root = etree.XML(r.text.encode('utf-8'))
    scraperwiki.sql.execute('drop table if exists House')
    scraperwiki.sql.execute('drop table if exists property')
    for e in root.xpath('/response/listing')[0]:
      print e.tag
    for el in root.xpath('/response/listing'):
      d = OrderedDict()
      for tag in ['listing_id', 'price', 'image_url',
        'displayable_address',
        'details_url',
        'latitude', 'longitude', 'short_description',
        'num_bedrooms',
        'num_bathrooms',
        # 'num_floors', # Always 0
        'num_recepts']:

        d[tag] = subTagText(el, tag)
      if d['listing_id']:
        scraperwiki.sql.save(['listing_id'], d, table_name='House')

def main():
    propertyListings()

if __name__ == '__main__':
    main()
