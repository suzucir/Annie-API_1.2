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
import pandas as pd

# #######################################################################
# Columns in the output file
# #######################################################################
# Set parameters which you'd like to see
# Need to set the exact same name as in API response

response_main_element = 'product_ranks'
columns = ['country', 'category', 'interval', 'feed', 'type', 'rank']

# set prefix_columns to put some specific data ahead of main data
# check exporter.prefix_data when you changed prefix_columns
prefix_columns = ['product_name', 'device']

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
    description='Extract App Annie Store Intelligence App History data \
                 via App Annie API')
parser.add_argument(
    "-s", "--store", dest="opts_store", metavar="STORE", default="iphone",
    help="specify a type of device (Options: iphone | ipad | android)")
parser.add_argument(
    "-i", "--id", dest="opts_id", metavar="ID", default="443904275",
    help="specify an app id (e.g. 443904275) compatible with GP class codes")
parser.add_argument(
    "-c", "--country", dest="opts_country", metavar="CCODE", default="JP",
    help="specify a country code (a two-letter code e.g. JP, US, CN)")
parser.add_argument(
    "-f", "--feeds", dest="opts_feeds", metavar="FEEDS", default="free",
    help="specify a type of feeds (Options: free | paid | grossing | \
    new | top_new_free | top_new_paid | new_rising.)")
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
    default="1", help="0 ")
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
url = "https://api.appannie.com/v1.2/apps/" + \
    query_market + "/app/" + str(product_id) + "/ranks?" + \
    "countries=" + opts.opts_country

# Add optional parameters to the Request URI
if isinstance(opts.opts_feeds, str):
    url = url + "&feed=" + opts.opts_feeds
if isinstance(opts.opts_store, str):
    url = url + "&device=" + opts.opts_store

# Create a result file
filename = "result_StoreStats_RankHistory_" + opts.opts_store + \
          "_" + str(product_id) + \
          "_" + str(opts.opts_country) + \
          "_" + str(opts.opts_start_date) + \
          "_" + str(opts.opts_end_date) + \
          ".tsv"

if isinstance(opts.opts_file_prefix, str):
    filename = opts.opts_file_prefix + "_" + filename

# Set a path for the result file
filename = opts.opts_output_dir + filename

# Format date
print opts.opts_start_date
start_date = datetime.datetime.strptime(opts.opts_start_date, '%Y-%m-%d')
end_date = datetime.datetime.strptime(opts.opts_end_date, '%Y-%m-%d')

# Make a Request insatance
request = annieapi.Request()
# exporter = annieapi.Exporter()

# Main
request_url = url + "&start_date=" + start_date.strftime('%Y-%m-%d') + \
      "&end_date=" + end_date.strftime('%Y-%m-%d')
print request_url

# Retrieve a JSON response
try:
    response = request.get_response(request_url, key, user_agent)
except:
    sys.exit()

# Prepare for a file
f = open(filename, "w")
f.write("product_name" + "\t")
f.write(response['product_name'] + "\n")
f.write("device" + "\t")
f.write(response['device'] + "\n")
f.write("\n")
f.close()

# Write data to the output file
result = {}
for i in response['product_ranks']:
    result[str(i['category']) + " : " + str(i['feed']) ] = i['ranks']

df = pd.DataFrame(result)
f = open(filename, "a")

df.to_csv(f, sep='\t', index_label="date")

print df

f.close

sys.exit()
