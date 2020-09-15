from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
import csv
import json

import logging

class Listing:
    def __init__(self,price=None):
        self.price = price

listingUrls=[]
data=[]
page=1

GEOCODING_API_KEY=""

ZOLO_TAGS = {
    "listings":["li", {"class": "listing-column"}],
    "address1":["h1",{"class":"address"}],
    "address2":["div",{"class":"area"}],
    "sectionListing":["section",{"class":"section-listing-content"}],
    "dl_property":["dl",{"class":"column"}],
    "dt_columnLabel":["dt",{"class":"column-label"}],
    "dd_columnValue":["dd",{"class":"column-value"}],
    "info":["section",{"class","sm-mb3"}],
    "property":["div",{"class":"column"}],
    "columnLabel":["div",{"class":"column-label"}],
    "columnValue":["div",{"class":"column-value"}],
    "price":["section",{"class":"listing-price"}],
    "priv":["span",{"class":"priv"}]
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
    address1 = address2 = latitude = longitude = walkScore = postalCode = propertyType = style = yearBuilt  = bedrooms = bathrooms = parking = garage = lotDepth = lotFrontage = price =""
    address1 = secondarySoup.find(*ZOLO_TAGS["address1"]).getText().lstrip()
    address2 = secondarySoup.find(*ZOLO_TAGS["address2"]).getText().lstrip()
    address2 = " ".join(i for i in address2.split(", ")[::-1])

    for info in secondarySoup.findAll(*ZOLO_TAGS["sectionListing"]):
        for column in (info.findAll(*ZOLO_TAGS["dl_property"])):
            try:
                if column.find(*ZOLO_TAGS["dt_columnLabel"]).getText() == "Walk Score":
                    walkScore = column.find(*ZOLO_TAGS["dd_columnValue"]).getText()
            except:
                logging.error("Walk Score not found")
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
                if column.find(*ZOLO_TAGS["columnLabel"]).getText() == "Bedrooms":
                    bedrooms = column.find(*ZOLO_TAGS["columnValue"]).getText()
                if column.find(*ZOLO_TAGS["columnLabel"]).getText() == "Bathrooms":
                    bathrooms = column.find(*ZOLO_TAGS["columnValue"]).getText()
                if column.find(*ZOLO_TAGS["columnLabel"]).getText() == "Total Parking":
                    parking = column.find(*ZOLO_TAGS["columnValue"]).getText()
                if column.find(*ZOLO_TAGS["columnLabel"]).getText() == "Number of Garage Spaces":
                    garage = column.find(*ZOLO_TAGS["columnValue"]).getText()
                if column.find(*ZOLO_TAGS["columnLabel"]).getText() == "Lot Size Depth (m)":
                    lotDepth = column.find(*ZOLO_TAGS["columnValue"]).getText()
                if column.find(*ZOLO_TAGS["columnLabel"]).getText() == "Lot Size Frontage (m)":
                    lotFrontage = column.find(*ZOLO_TAGS["columnValue"]).getText()
            except:
                logging.error(url+" throwed error")
    try:
        if secondarySoup.find(*ZOLO_TAGS["price"]).find(*ZOLO_TAGS["priv"]).getText().strip().replace(",","")[1:].isnumeric():
            price = secondarySoup.find(*ZOLO_TAGS["price"]).find(*ZOLO_TAGS["priv"]).getText().strip()[1:]
    except:
        logging.error(url+" doesn't have price")

    try:
        location = address1.replace(" ","+")+","+address2.replace(" ","+")
        data = urlopen(Request('https://maps.googleapis.com/maps/api/geocode/json?address='+location+'+Canada&key='+GEOCODING_API_KEY+'/'')).read()
        geocode = json.loads(data.decode('utf-8'))
        latitude = geocode["results"][0]["geometry"]["location"]["lat"]
        longitude = geocode["results"][0]["geometry"]["location"]["lng"]
    except:
        logging.error(url+" doesnt have location/sketchy location")
    return [url, location, latitude, longitude, postalCode, walkScore, propertyType, style, yearBuilt, bedrooms, bathrooms, parking, garage, lotDepth, lotFrontage, price]

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

    
for url in listingUrls:
    print(url)
    data.append(getDatafromUrl(url))

with open('data.csv', 'w',newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    writer.writerow(['url','location','latitude','longitude','postalCode', 'walkScore', 'propertyType','style','yearBuilt','bedrooms','bathrooms','parking','garage','lotDepth','lotFrontage','price'])
    for i in data:
        if i is not None:
            writer.writerows([i])

    

