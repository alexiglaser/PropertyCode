
# coding: utf-8

# In[2]:

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


# In[141]:

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
        #print url
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
                        price = listing.find(itemprop="price")
                        if price is not None:
                            item_instance.price = price.get_text()
                        else:
                            item_instance.price = None
                        item_instance.description = listing.find(itemprop="description").get_text()
                        item_instance.location =  listing.find(class_="listing-location").get_text()
                        item_instance.thumbnail = listing.find(class_="listing-thumbnail").get("src")
                        adrecency = listing.find(itemprop="adAge")
                        if adrecency is not None: 
                            item_instance.adrecency = adrecency.get_text()
                        else:
                            item_instance.adrecency = None
                        item_instance.adref = title.split("-")[-1]
                        
                    listing_results.append(item_instance)
            return listing_results
        else:
            # TODO: Add error handling
            print "Server returned code %s" % request.status_code
            return []


# In[142]:

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
        #print self.url
        request = requests.get(self.url, headers=REQUEST_HEADERS)
        if request.status_code == 200:
            # Got a valid response
            souped = BeautifulSoup(request.text, "html.parser")
            #description = souped.find("div", id="vip-description-text").string
            #if description:
            #    self._description = description.strip()
            #else:
            #    self._description = ""
            #_contact_name = souped.find("h2", itemprop="name").get_text()
            #_contact_number = souped.find("strong", itemprop="telephone").get_text()
            #print _contact_number
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


# In[ ]:

# Get all locations
url = "https://www.gumtree.com/all/central-london/2+bedroom+flat"
request = requests.get(url, headers=REQUEST_HEADERS)


# In[111]:

# Need to find a way of scrolling over mutliple pages
# Add list so that you can scroll over location data
s = dict()
if request.status_code == 200:
    # Got a valid response
    souped = BeautifulSoup(request.text, "html.parser")
    for location_id in souped.find_all("div", class_="box space-mbs"):
        for location in location_id.find_all("a", class_="space-mrxs"): 
            s_location = location.get_text().replace(" ", "+")
            s[s_location] = SearchListing(query="2 bedroom flat", location=s_location)


# In[143]:

items = dict()
for key in s:
    items[key] = s[key].doSearch()


# In[144]:

i = 0
for key in s:
    for item in items[key]:
        if i == 0:
            print dir(item)
        i += 1
print i


# In[174]:

# Write to csv file
import csv
f = open("all_adverts.csv", 'wt')
writer = csv.writer(f)
#writer.writerow(('_contact_name, item._contact_number, item._description, item._images, item._longitude, item.adrecency, item.adref, item.contact_name, item.contact_number, item.description, item.getFullInformation, item.images, item.latitude, item.location, item.longitude, item.price, item.summary, item.thumbnail, item.title, item.url'))
writer.writerow(('adrecency', 'adref', 'description', 'images', 'location', 'price', 'summary', 'thumbnail', 'title', 'url'))
for key in s:
    for item in items[key]:
        #print item.url
        if item.price is None:
            item.price = "-"
        #print item.adrecency, item.adref, item.description, item.images, item.latitude, item.location, item.longitude, item.price, item.summary, item.thumbnail, item.title, item.url
        writer.writerow((item.adrecency, item.adref, item.description.encode('utf-8').strip(), item.images, item.location, item.price.encode('utf-8').strip(), item.summary, item.thumbnail, item.title, item.url.encode('utf-8').strip()))
        #.encode('utf-8').strip()
        #writer.writerow(item._contact_name, item._contact_number, item._description, item._images, item._longitude, item.adrecency, item.adref, item.contact_name, item.contact_number, item.description, item.getFullInformation, item.images, item.latitude, item.location, item.longitude, item.price, item.summary, item.thumbnail, item.title, item.url)


# In[45]:

url = "https://www.gumtree.com/all/central-london/2+bedroom+flat"
#url = "https://www.gumtree.com/search?distance=0&search_category=all&q=2+bedroom+flat&search_location=Central+London"
request = requests.get(url, headers=REQUEST_HEADERS)


# In[48]:

if request.status_code == 200:
    # Got a valid response
    souped = BeautifulSoup(request.text, "html.parser")
    #print souped
    for location_and_value in souped.find_all("div", class_="box space-mbs"):
        #print location_and_value
        for location in location_and_value.find_all("a", class_="space-mrxs"): 
            print location.get_text().replace(" ", "+")


# In[27]:

if request.status_code == 200:
    # Got a valid response
    souped = BeautifulSoup(request.text, "html.parser")
    #print souped
    for location in souped.find_all("a", class_="space-mrxs"): 
        print location#.get_text().replace(" ", "+")


# In[30]:

print souped.find_all("a", class_="space-mrxs")


# In[33]:

print souped.find_all(class_="box space-mbs")


# In[61]:

url2 = "https://www.gumtree.com/all/shoreditch/2+bedroom+flat"
request2 = requests.get(url2, headers=REQUEST_HEADERS)
if request2.status_code == 200:
    # Got a valid response
    souped2 = BeautifulSoup(request2.text, "html.parser")
    #for location_id in souped.find_all("div", class_="box space-mbs"):
    #    for location in location_id.find_all("a", class_="space-mrxs"): 
    #        s_location = location.get_text().replace(" ", "+")
    #        s[s_location] = SearchListing(query="2 bedroom flat", location=s_location)


# In[65]:

for listings_wrapper in souped2.find_all("article", class_="listing-maxi"):
    title = listings_wrapper.get("data-q")
    if title is not None:
        print title.split("-")[-1]


# In[ ]:



