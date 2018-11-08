#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright Shigenori Suzuki <suzuki@appannie.com>
#

import urllib2
import sys
import datetime
import time
import argparse
import settings
import annieapi

# #######################################################################
# Columns in the output file
# #######################################################################

# set prefix_columns to put some specific data ahead of main data
prefix_columns = ['market', 'granularity', 'country',
                  'product_id', 'product_code', 'product_name',
                  'unified_product_id', 'unified_product_name',
                  'publisher_id', 'publisher_name',
                  'company_id', 'company_name',
                  'parent_company_id', 'parent_company_name'
                  ]

# Element name for main contents
response_main_element = 'list'

# Need to set the exact same name as in API response
columns = ['feed', 'device', 'date', 'estimate']

# #######################################################################
# Imported from settings.py
# #######################################################################
# Set API Key and User-Agent
key = settings.key
user_agent = settings.user_agent

# #######################################################################
# Set up command line option for CUI using argparse
# #######################################################################
parser = argparse.ArgumentParser(
    description='Retrieve App Annie Store Intelligence App History data \
                 via App Annie API')
parser.add_argument(
    "-s", "--store", dest="opts_store", metavar="STORE", default="all",
    help="specify a type of device (Options: all | iphone | ipad | android)")
parser.add_argument(
    "-i", "--id", dest="opts_id", metavar="ID", default="443904275",
    help="specify an app id (e.g. 443904275) compatible with GP class codes")
parser.add_argument(
    "-c", "--country", dest="opts_country", metavar="CCODE", default="JP",
    help="specify a country code (a two-letter code e.g. JP, US, CN)")
parser.add_argument(
    "-f", "--feeds", dest="opts_feeds", metavar="FEEDS",
    default="downloads",
    help="specify a type of feeds (Options: downloads | revenue)")
parser.add_argument(
    "-b", "--start_date", dest="opts_start_date", metavar="STARTDATE",
    help="default is the beggining date")
parser.add_argument(
    "-e", "--end_date", dest="opts_end_date", metavar="ENDDATE",
    help="dafault value is today")
parser.add_argument(
    "-x", "--file_prefix", dest="opts_file_prefix", metavar="FILEPREFIX",
    help="for file name")
parser.add_argument(
    "-w", "--write_header", dest="opts_write_header", metavar="WRITEHEADER",
    default="0", help="0 ")
parser.add_argument(
    "-o", "--output_dir", dest="opts_output_dir", metavar="OUTPUTDIR",
    default="./result/", help="directory path for the output file")
opts = parser.parse_args()
# #######################################################################

# Set up "market" and convert Google Play Class code
product_id = opts.opts_id
if opts.opts_store == "android":
    query_market = "google-play"
    if "." in opts.opts_id:
        url = "https://api.appannie.com/v1.2/apps/" + query_market + \
             "/package-codes2ids?package_codes=" + str(product_id)
        # API Call & Response
        android_app_id = annieapi.request_api(url, key, user_agent)
        product_id = android_app_id['items'][0]['product_id']
else:
    query_market = "ios"

# Request URI for Store Intelligence App History
request_url = "https://api.appannie.com/v1.2/intelligence/apps/" + \
    query_market + "/app/" + str(product_id) + "/history?" + \
    "countries=" + opts.opts_country + "&granularity=monthly" 

# Add optional parameters to the Request URI
if isinstance(opts.opts_feeds, str):
    request_url = request_url + "&feeds=" + opts.opts_feeds
if isinstance(opts.opts_store, str):
    request_url = request_url + "&device=" + opts.opts_store

# Create a result file
filename = "total_StoreInt_" + opts.opts_store + \
          "_" + str(product_id) + \
          "_" + str(opts.opts_country) + \
          "_" + str(opts.opts_feeds)

if isinstance(opts.opts_start_date, str):
    start_date = datetime.datetime.strptime(opts.opts_start_date, '%Y-%m-%d')
else:
    if query_market == "ios":
        start_date = datetime.datetime.strptime("2010-07-01", '%Y-%m-%d')
    else:
        start_date = datetime.datetime.strptime("2012-01-01", '%Y-%m-%d')

request_url = request_url + "&start_date=" + start_date.strftime('%Y-%m-%d')
filename = filename + "_" + start_date.strftime('%Y-%m-%d')

if isinstance(opts.opts_end_date, str):
    end_date = datetime.datetime.strptime(opts.opts_end_date, '%Y-%m-%d')
    request_url = request_url + "&end_date=" + end_date.strftime('%Y-%m-%d')
    filename = filename + "_" + str(opts.opts_end_date)
else:
    filename = filename + "_latest"

filename = filename + ".tsv"

if isinstance(opts.opts_file_prefix, str):
    filename = opts.opts_file_prefix + "_" + filename

# Set a path for the result file
filename = opts.opts_output_dir + filename

# Make a Request insatance
request = annieapi.Request()
exporter = annieapi.Exporter()

# Prepare for a file
exporter.filename = filename
exporter.prefix_columns = prefix_columns
exporter.main_element = response_main_element
exporter.columns = columns
exporter.is_write_header = int(opts.opts_write_header)
exporter.create_file()

# Retrieve a JSON response
try:
    response = request.get_response(request_url, key, user_agent)
except:
    sys.exit()

total = []
for i in response['list']:
    if isinstance(i['estimate'], (int, long)):
        total.append(i['estimate'])

output = []
for i in prefix_columns:
    output.append(str(response[i]))
output.append(opts.opts_feeds)
output.append(str(sum(total)))

f = open(filename, "w")
f.write("\t".join(output))
print response['product_id'] + ", " + \
      response['product_name'] + ": " + str(sum(total))

f.write('\n')
f.close()

sys.exit()
