from pymongo import MongoClient
import datetime

client = MongoClient()

db = client['pyreal']

f = open('Auction_20151110.csv','w')

headers = [ u'Address',
            u'Suburb',
            u'State',
            u'Number_Of_Bedrooms',
            u'Land_Size',
            u'Auction_Date',
            u'Auction_Result',
            u'Price',
            u'Link',
            u'Agency_Name',
            u'Agency_Web_Link']
school_header = [
                'Primary School Sector'
                ,'Primary School Name'
                ,'Primary School Distance'
                ,'Primary School Year Range'
                ,'Primary School Type'
                ,'Secondary School Sector'
                ,'Secondary School Name'
                ,'Secondary School Distance'
                ,'Secondary School Year Range'
                ,'Secondary School Type'
                ]

f.write('|'.join(headers) + '|' + '|'.join(school_header) + '\n')

condition = {"Scrape_Date":{"$gte":datetime.datetime(2015,11,10,0,0,0,0)}}

count = db.auction.find(condition).count()
print 'Total Number : ' + str(count)
result = db.auction.find(condition)

tmp = []
for x in result:
    tmp = []
    for key in headers:
        tmp.append(str(x[key]))
    #print x["Features"]["Schools"]
    if x["Features"]["Status"] == "Ok":
        if "primary" in x["Features"]["Schools"].keys():
            primary_school = x["Features"]["Schools"]["primary"]

            tmp.append(primary_school[0]["sector"])
            tmp.append(primary_school[0]["name"])
            tmp.append(str(primary_school[0]["distance"]["value"]) + primary_school[0]["distance"]["unit"])
            tmp.append(primary_school[0]["year_range"])
            tmp.append(primary_school[0]["school_type"])
        else:
            tmp.extend(['N/A','N/A','N/A','N/A','N/A'])

        if "secondary" in x["Features"]["Schools"].keys():
            secondary_school = x["Features"]["Schools"]["secondary"]

            tmp.append(secondary_school[0]["sector"])
            tmp.append(secondary_school[0]["name"])
            tmp.append(str(secondary_school[0]["distance"]["value"]) + secondary_school[0]["distance"]["unit"])
            tmp.append(secondary_school[0]["year_range"])
            tmp.append(secondary_school[0]["school_type"])
        else:
            tmp.extend(['N/A','N/A','N/A','N/A','N/A'])
    #print tmp
    f.write(u'|'.join(map(lambda x: x.encode('ascii','ignore') if x else u"N/A",tmp)) + '\n')

client.close()
f.close()


