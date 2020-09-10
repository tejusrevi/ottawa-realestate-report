from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
import csv

import logging

class Listing:
    def __init__(self,price=None):
        self.price = price

listingUrls=[]
data=[]
page=1

ZOLO_TAGS = {
    "listings":["li", {"class": "listing-column"}],
    "address1":["h1",{"class":"address"}],
    "address2":["div",{"class":"area"}],
    "info":["section",{"class","sm-mb3"}],
    "property":["div",{"class":"column"}],
    "columnLabel":["div",{"class":"column-label"}],
    "columnValue":["div",{"class":"column-value"}]
            }

def getListingUrl(soup):
    urls = []
    listings = soup.findAll(*ZOLO_TAGS["listings"])
    for listing in listings: 
        urls.append(listing.find("a")["href"])
    return urls

def getDatafromUrl(url):
    try:
        listingPage = urlopen(Request(url, headers={'User-Agent': 'Mozilla/5.0'})).read()
    except ValueError:
        return
    secondarySoup = BeautifulSoup(listingPage, 'html.parser')
    address1 = address2 = postalCode = propertyType = style = yearBuilt = ""
    address1 = secondarySoup.find(*ZOLO_TAGS["address1"]).getText().lstrip()
    address2 = secondarySoup.find(*ZOLO_TAGS["address2"]).getText().lstrip()
    for info in secondarySoup.findAll(*ZOLO_TAGS["info"]):
        for column in (info.findAll(*ZOLO_TAGS["property"])):
            try:
                if column.find(*ZOLO_TAGS["columnLabel"]).getText() == "Postal Code":
                    postalCode = column.find(*ZOLO_TAGS["columnValue"]).getText()
                if column.find(*ZOLO_TAGS["columnLabel"]).getText() == "Property Type":
                    propertyType = column.find(*ZOLO_TAGS["columnValue"]).getText()
                if column.find(*ZOLO_TAGS["columnLabel"]).getText() == "Style":
                    style = column.find(*ZOLO_TAGS["columnValue"]).getText()
                if column.find(*ZOLO_TAGS["columnLabel"]).getText() == "Year Built":
                    yearBuilt = column.find(*ZOLO_TAGS["columnValue"]).getText()
            except:
                print(url)
    
    return [address1+address2,postalCode,propertyType,style,yearBuilt]

while(True):
    try:
        homepage = urlopen(Request('https://www.zolo.ca/ottawa-real-estate/page-'+str(page), headers={'User-Agent': 'Mozilla/5.0'})).read()
        primarySoup = BeautifulSoup(homepage, 'html.parser')
        listingUrls+=getListingUrl(primarySoup)
    except HTTPError:
        break
    except URLError:
        logging.error("No internet connection")
        break
    page+=1

print(listingUrls)
for url in listingUrls:
    data.append(getDatafromUrl(url))

print(data)
with open('data.csv', 'w',newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    writer.writerow(['address','postalCode','propertyType','style','yearBuilt'])
    for i in data:
        if i is not None:
            writer.writerows([i])

    

