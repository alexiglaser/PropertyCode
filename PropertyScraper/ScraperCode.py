
# coding: utf-8

# In[140]:

"""
python-gumtree

Gumtree scraper written in Python

Copyright 2013 Oli Allen <oli@oliallen.com>
"""

USER_AGENT = "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)"
REQUEST_HEADERS = {'User-agent': USER_AGENT,}

import requests
import re
from bs4 import BeautifulSoup
#import html5lib
gumtreeURL = "https://www.gumtree.com"


# In[150]:

class SearchListing:
    """
    A gumtree search result set containing GTItem objects
    """

    def __init__(self, category="all", query="", location="", distance=0):
        self.category = category
        self.distance = distance
        self.query = query    
        self.location = location

        self.listing_results = self.doSearch()


    def __str__(self):
        return "Search listing"

    def doSearch(self):
        """
        Performs the search against gumtree
        """

        url = "https://www.gumtree.com/search?distance=%s&search_category=%s&q=%s&search_location=%s" % (self.distance, self.category.replace(" ", "+"), self.query.replace(" ", "+"), self.location.replace(" ", "+"))
        request = requests.get(url, headers=REQUEST_HEADERS)

        if request.status_code == 200:
            # Got a valid response

            listing_results = []

            souped = BeautifulSoup(request.text, "html.parser")
            for listings_wrapper in souped.find_all("article", class_="listing-maxi"):
                title = listings_wrapper.get("data-q")
                if title is not None:
                    for listing in listings_wrapper.find_all("a", class_="listing-link"):
                        item_instance = GTItem(title=title)
                        item_instance.url = gumtreeURL + listing.get("href")
                        item_instance.price = listing.find(itemprop="price").get_text()
                        item_instance.description = listing.find(itemprop="description").get_text()
                        item_instance.location =  listing.find(class_="listing-location").get_text()
                        item_instance.thumbnail = listing.find(class_="listing-thumbnail").get("src")
                        item_instance.adrecency = listing.find(itemprop="adAge").get_text()
                        item_instance.adref = title.split("-")[-1]
                        
                    listing_results.append(item_instance)
            return listing_results
        else:
            # TODO: Add error handling
            print "Server returned code %s" % request.status_code
            return []


# In[207]:

class GTItem:
    """
    An individual gumtree item
    """
    def __init__(self, title, summary="", description="", thumbnail="", price="", location="", adref="", url="", contact_name="", contact_number="", images=[]):
        self.title = title
        self.summary = summary
        self.thumbnail = thumbnail
        self.price = price
        self.location = location
        self.adref = adref
        self.url = url
                
        self._description = None
        self._contact_name = None
        self._contact_number = None
        self._images = None

        self._longitude = None
        self.latitude = None

    @property
    def images(self):
        if not self._images:
            
            self._images = ['test',]
        return self._images

    @property
    def description(self):
        if not self._description:
            self.getFullInformation()
        return self._description
	
    @property
    def contact_name(self):
        if not self._contact_name:
            self.getFullInformation()
        return self._contact_name

    @property
    def contact_number(self):
        if not self._contact_number:
            self.getFullInformation()
        return self._contact_number

    @property
    def latitude(self):
        if not self._latitude:
            self.getFullInformation()
        return self._latitude

    @property
    def longitude(self):
        if not self._longitude:
            self.getFullInformation()
        return self._longitude

    def __str__(self):
        return self.title
	

    def getFullInformation(self):
        """
        Scrape information from a full gumtree advert page
        """
        print self.url
        request = requests.get(self.url, headers=REQUEST_HEADERS)
        if request.status_code == 200:
            # Got a valid response
            souped = BeautifulSoup(request.text, "html.parser")
            #description = souped.find("div", id="vip-description-text").string
            #if description:
            #    self._description = description.strip()
            #else:
            #    self._description = ""
            _contact_name = souped.find("h2", itemprop="name").get_text()
            _contact_number = souped.find("strong", itemprop="telephone").get_text()
            print _contact_number
            #if not contact:
            #    self._contact_name, self._contact_number = ["",""]
            #else:
            #    if " on " in contact.string:
            #        self._contact_name, self._contact_number = contact.string.split(" on ")
            #    else:
            #        self._contact_name, self._contact_number = ["", contact.string]

            gmaps_link = souped.find("a", class_="open_map")
            if gmaps_link:
                self._latitude, self._longitude = re.search("center=(-?\w.*),(-?\d.*)&sensor", gmaps_link.get("data-target")).groups()
            else:
                self._latitude, self._longitude = ["", ""]

            return
        else:
            # TODO: Add error handling
            print "Server returned code %s for %s" % (request.status_code, url)
            return []


# In[210]:

# Need to find a way of scrolling over mutliple pages
# Add list so that you can scroll over location data
s = SearchListing(query="2 bedroom flat", location="kings cross")


# In[217]:

for item in items:
    print item.location, item.title, item.price


# In[215]:

dir(items[0])

