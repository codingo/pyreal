#! /usr/bin/python

import Image
import pytesseract
import urllib
from bs4 import BeautifulSoup
import base64
import cStringIO
from time import gmtime, strftime
from datetime import datetime
import re
import json
from pymongo import MongoClient



states = ['nsw','vic','wa','sa','qld','tas','act']
#states = ['tas']
base_url = 'https://www.realestate.com.au/auction-results/'
pro_url = 'https://www.realestate.com.au'

#run_date = strftime("%c",gmtime())
#str_run_date = strftime("%Y%m%d",gmtime())

def get_school_dict(ele_school_div):
    base_url = 'http://school-service.realestate.com.au/closest_by_type?'
    lat = ele_school_div['data-latitude']
    lon = ele_school_div['data-longitude']
    r = urllib.urlopen(base_url + 'lat=' + lat + '&lon=' + lon + '&count=5').read()
    return json.loads(r)



# return a dict for all features from the main page
def get_property_features(prop_url):
    detail = {}
    general = {}
    indoor = {}
    outdoor = {}
    eco = {}
    other = {}
    try:
        r = urllib.urlopen(prop_url).read()
        detail['Status'] = 'Ok'
        soup = BeautifulSoup(r)
        # get description
        desc = soup.find("div",{"id":"description"})
        if desc:
            detail['Description'] = desc.find("p",class_="body").text
        else:
            detail['Description'] = 'null'
        f_all = soup.find_all("div",class_="featureList")
        for f in f_all:
            for ul in f.find_all("ul"):
                if ul.find("li",class_="header").text == 'General Features':
                    for li in ul.find_all("li"):
                        if li.text <> 'General Features':
                            if ':' in li.text:
                                key, value = li.text.split(':')[0], li.text.split(':')[1]
                                if key == 'Land Size':
                                    general[key] = re.sub(r'[^0-9]','',value)
                                elif key == 'Building Size':
                                    general[key] = re.sub(r'([0-9\.]+).*',r'\1',value)
                                else:
                                    general[key] = value
                            else:
                                general[li.text] = 'Yes'
                if ul.find("li",class_="header").text == 'Indoor Features':
                    for li in ul.find_all("li"):
                        if li.text <> 'Indoor Features':
                            if ':' in li.text:
                                key, value = li.text.split(':')[0], li.text.split(':')[1]
                                indoor[key] = value
                            else:
                                indoor[li.text] = 'Yes'
                if ul.find("li",class_="header").text == 'Outdoor Features':
                    for li in ul.find_all("li"):
                        if li.text <> 'Outdoor Features':
                            if ':' in li.text:
                                key, value = li.text.split(':')[0], li.text.split(':')[1]
                                outdoor[key] = value
                            else:
                                outdoor[li.text] = 'Yes'
                if ul.find("li",class_="header").text == 'Eco Friendly Features':
                    for li in ul.find_all("li"):
                        if li.text <> 'Eco Friendly Features':
                            if ':' in li.text:
                                key, value = li.text.split(':')[0], li.text.split(':')[1]
                                eco[key] = value
                            else:
                                eco[li.text] = 'Yes'
                if ul.find("li",class_="header").text == 'Other Features':
                    for li in ul.find_all("li"):
                        if li.text <> 'Other Features':
                            if ':' in li.text:
                                key, value = li.text.split(':')[0], li.text.split(':')[1]
                                other[key.replace('.','')] = value
                            else:
                                other[li.text.replace(',','')] = 'Yes'
        school_ele = soup.find("div",class_="rui-school-information")
        if school_ele:
            school_dict = get_school_dict(school_ele)
        else:
            school_dict = {}
        detail['General']=general
        detail['Indoor']=indoor
        detail['Outdoor']=outdoor
        detail['Eco_System']=eco
        detail['Other']=other
        detail['Schools']=school_dict
    except Exception as inst:
        detail['Status'] = 'Error'
        print inst
    return detail

def get_string_from_base64(base64_image):
    str_null = 'iVBORw0KGgoAAAANSUhEUgAAAA4AAAAiCAYAAABvJuicAAAAM0lEQVR42mNgGAWjYBQMH+Dg4MBiZO+xGxc2tvdYh1WjtnYoG1DyEx58fzR4R8EooCkAAL1cGle5CANKAAAAAElFTkSuQmCC'
    if base64_image == str_null:
        return '0'
    else:
        image_string = cStringIO.StringIO(base64.b64decode(base64_image))
        image = Image.open(image_string)
        return_str = pytesseract.image_to_string(image)
        return return_str.replace('$','').replace(',','')


def get_beds_from_base64(base64_image):
    enum = {}
    enum['iVBORw0KGgoAAAANSUhEUgAAAA4AAAAiCAYAAABvJuicAAAAeElEQVR42mNgGAV0AmY2XmpG9h7Lje09ZpOkCajhJRD/B+LXpGr6RrRGYwc3DZhNRnae4URp1HfykUbSFA02iGgb7T0mwTSRpBGLQaMaRzUOOo2mjp72QEXr0DBI4w90cSNbDz24RhN791ioQoLY1MHdZbRwHT4AAGPFdGQFdYoiAAAAAElFTkSuQmCC'] = 1
    enum['iVBORw0KGgoAAAANSUhEUgAAABAAAAAiCAYAAABWQVnHAAABPElEQVR42mNgGAWDEBg7uGkY27tPM7b3fGhs7/EHiH8A8QWgWKO5uScffs32HnlQTf+hGq8A8QcoH4Qfm9l4qeHSnAVV9NrI3j2RgaGBCdVVHvuh8vcdHBw4UDRra4eyASWegjAuG6BqLoANcXDPwFCga+MtaGjrqYXPiyCXgQwwsvdYTlYAm9h5eIFdYOexhSwDjOw8gqDhsIq8KLbz2IEzDIhwfjLU9qcYsUDQZkQUA9OIuyPRGkExAwpxqOZPoEAkWrOpg7sLKOVBNd8gFMWo/rX3bIUlXxMHjylE+xmk0MTeYxNU80tjO0830uLZ3n0bVPNJc2dncRKzsXsGRLP7NYLZFntUgfP/fxNHT2uSNZs6eBlAnf6OvDTu4OYDDzh7j3XEYGCAsyAZ4O6BVOoQhUHlw2gFMApgAADEkqV32uXWrgAAAABJRU5ErkJggg=='] = 2
    enum['iVBORw0KGgoAAAANSUhEUgAAABAAAAAiCAYAAABWQVnHAAABRUlEQVR42mNgGAWDCJjYeVYb2XssJwYb23vkYRgAlNgNlPhPAP+B0O7TSHahkYO7B1DzL6Dma7o23oIkaTa19zAFav4GxC/1nXykSdNs5yYL0gjEX4wc3YxJ0qzt4MAD1HgF5G+QF0j2t7Gdxw5woDm4Z5AerfYeM8E223v0kW4zMJ6h0fbL2MFzAhAHaGuHspFggHsjljTwwcjBs4BEtzQwmTi46RjZedSDYgHiJfe5ZCV1YCyoAA14DjbEziOILEOAsRIPdcU2sgwABSQ0PD6RmWcbmKAGfCMvHIBJGWrAOQynmdh7tjo4OHAQSB+roIFYj2oyJJpA+fwatjQPMhiWMoH4sbm5Jx+KAlD+hpkOxXeBeL6Jg8cUoMbF0NwIEn9p6uBlgLfQMLF3P4i9JPJcSnRZAHIiuAQC5gEQTShsRsGQBwDEKaZfG5fquQAAAABJRU5ErkJggg=='] = 3
    enum['iVBORw0KGgoAAAANSUhEUgAAABEAAAAiCAYAAAC5gzL5AAAA/0lEQVR42mNgGAXDABjZe6YZ2XssN7b3KCLLAFNHT3ug5v9QvI5kAwxtPUWBGp8D8TuyDQF6YTdIM8g7ZBkC1FAJ0ei+0MjRzZhkQ0wcPa2hmq44ODhwGNm725JkiJmzszA0HD6Z2XipQbxFoiEm9h6bwOFg5xGECBsSDAGlA7BiB88JqAFMpCHGjl7mQEV/gDFylIGhgYlkQ3RtvAWN7T0fAhW9NHd2FseMaiIMMbbz2ABSZOrg7oI9vRAwxMjBswCmAKQYGwbK5YHUmNi7H4SJmdp4KyEH5h+kvEE0NnHwmIKIUiCHEIZ5F4jvwsXsPUJJzEMkJrZRQ0bBKCAIACz1sGFn0JZiAAAAAElFTkSuQmCC'] = 4
    enum['iVBORw0KGgoAAAANSUhEUgAAABAAAAAiCAYAAABWQVnHAAABTElEQVR42mNgGAWDDBg5eBYY2Xssx4eN7T1m4zbA3n0bUMF/Avg1TgNAkkD8i2wvADX/AeKXZGnWdnDgATnRxN5jE5m2uztC/Oi5lDwDHDwDwC5w8JhCXhTauyeCDDCy84w2dXB3AbqoFmQYUCzPxNHTmhgvTING0wcc0XfD1NHTHqcBwMBbDHaBvcdRcIJycPMxsfPwAuJkkBjMIKALw3EY0cBkZOuhhyeKs6CG/DB2cNMgK5yAruyCGjKfLAMMbT1FoQZ8oyS1fgEZoq0dykauAT9ABjg4OLCQHgYObjpQLzzGWhaA/EggsUGyu51HM4oEJOWBTb5vau9hiq7R3NyTDyi3CppXHoL4WEz36ENKdcdBJQ8oKUNLoW8wzWY2Xmp4ijR3D6DCk1iS8S9gZpuga+MtSFRgmTs7i4OSMiiHAv1tC0qlozXGsAYALkCo2GqAo7AAAAAASUVORK5CYII='] = 5
    if base64_image in enum.keys():
        return str(enum[base64_image])
    else:
        return '6'

# run_date, auction_date, state, sub, address, beds, price, result
properties = []

if __name__ == '__main__':
    client = MongoClient()
    db = client['pyreal']
    auction_collection = db.auction
    for state in states:
        url = base_url + state
        r = urllib.urlopen(url).read()
        soup = BeautifulSoup(r)
        results = soup.find_all("table", class_="rui-table rui-table-hover rui-table-striped auction-results-table")
        for result in results:
            sub = result.find("div",class_="col-suburb-name").text
            print 'Processing state/suburb: %s/%s' % (state.upper(), sub)
            for p in result.find_all("tbody"):
                tmp_p = {}
                tmp_p['Scrape_Date'] = datetime.utcnow()
                try:
                    # get address
                    ele_addr = p.find("a",class_="col-address")
                    if ele_addr:
                        addr = ele_addr.text
                        real_id = ele_addr['href'][1:]
                        addr_link = pro_url + ele_addr['href']
                        # print '\tGetting property features %s' % real_id
                        features = get_property_features(addr_link)
                        # get land size
                        # print features.keys()
                        if features['Status'] == 'Ok' and 'Land Size' in features['General'].keys():
                            LandSize = features['General']['Land Size']
                        else:
                            LandSize = '0'
                    else:
                        ele_addr = p.find("div",class_ = "col-address")
                        if ele_addr:
                            addr = ele_addr.text
                            addr_link = '#'
                            real_id = '0'
                        else:
                            print 'col-address not found'

                    # get price
                    ele_price = p.find("div",class_ = "col-property-price noscrape")
                    if ele_price:
                        price = get_string_from_base64(ele_price.find("img")['src'][22:])
                    else:
                        print 'col-property-price noscrape not found'

                    # get num of beds
                    ele_beds = p.find("div",class_ = "col-num-beds noscrape")
                    if ele_beds:
                        beds = get_beds_from_base64(ele_beds.find("img")['src'][22:])
                    else:
                        print 'col-num-beds noscrape not found'

                    # get property type
                    ele_type = p.find("div",class_="col-property-type")
                    if ele_type:
                        p_type = ele_type.text
                    else:
                        print 'col-property-type not found'

                    # get result
                    ele_result = p.find("div",class_="col-auction-result")
                    if ele_result:
                        auction_result = ele_result.text
                    else:
                        print 'col-auction-result not found'

                    # get auction date
                    ele_date = p.find("div",class_ = "col-auction-date noscrape")
                    if ele_date:
                        auction_date = get_string_from_base64(ele_date.find("img")['src'][22:])
                    else:
                        print 'col-auction-date noscrape not found'

                    # get agency information
                    ele_agent = p.find("div",class_ = "col-agent ellipsis")
                    if ele_agent:
                        ele_agency_profile_url = ele_agent.find("a",class_="agency-profile-url")
                        ele_mobile_agency_profile_url = ele_agent.find("a",class_="mobile-agency-profile-url")
                        if ele_agency_profile_url:
                            agency_name = ele_agency_profile_url.text
                            agency_link = pro_url + ele_agency_profile_url['href']
                            agency_mobile_link = pro_url + ele_mobile_agency_profile_url['href']
                        else:
                            agency_nanme = ele_agent.text
                            agency_link = '#'
                            agency_mobile_link = '#'
                    else:
                        print 'col-auction-date noscrape not found'

                    tmp_p['Property_Id'] = int(real_id)
                    tmp_p['Auction_Date'] = auction_date
                    tmp_p['State'] = state.upper()
                    tmp_p['Suburb'] = sub
                    tmp_p['Address'] = addr
                    tmp_p['Number_Of_Bedrooms'] = int(beds)
                    tmp_p['Price'] = int(price)
                    tmp_p['Land_Size'] = int(LandSize)
                    tmp_p['Auction_Result'] = auction_result
                    tmp_p['Agency_Name'] = agency_name
                    tmp_p['Agency_Web_Link'] = agency_link
                    tmp_p['Agency_Mob_Link'] = agency_mobile_link
                    tmp_p['Link'] = addr_link
                    tmp_p['Features'] = features
                    auction_collection.insert(tmp_p)
                except Exception as inst:
                    print tmp_p
                    print inst.args
                    print inst
    client.close()
