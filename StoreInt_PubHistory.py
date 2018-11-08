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
                  'publisher_id', 'publisher_name',
                  'company_id', 'company_name',
                  'parent_company_id', 'parent_company_name'
                  ]

# Element name for main contents
response_main_element = 'list'

# Need to set the exact same name as in API response
columns = ['feed', 'device', 'category', 'date', 'estimate']

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
    description='Extracting App Annie Store Intelligence Publisher History data \
                 via App Annie API')
parser.add_argument(
    "-s", "--store", dest="opts_store", metavar="STORE", default="all",
    help="specify a type of device (Options: all | iphone | ipad | android)")
parser.add_argument(
    "-i", "--id", dest="opts_id", metavar="ID", default="359067226",
    help="specify a publisher id (e.g. 359067226)")
parser.add_argument(
    "-c", "--country", dest="opts_country", metavar="CCODE", default="JP",
    help="specify a country code (a two-letter code e.g. JP, US, CN)")
parser.add_argument(
    "-a", "--category", dest="opts_category", metavar="CATEGORY",
    default="Overall",
    help="specify a category (e.g. Overall > Games)")
parser.add_argument(
    "-g", "--granularity", dest="opts_granularity",
    metavar="GRANULARITY", default="daily",
    help="specify data granularity (Options: monthly | weekly | daily)")
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
    default="1", help="0 ")
parser.add_argument(
    "-o", "--output_dir", dest="opts_output_dir", metavar="OUTPUTDIR",
    default="./result/", help="directory path for the output file")
opts = parser.parse_args()
# #######################################################################

# Set up "market" and convert Google Play Class code
publisher_id = opts.opts_id
if opts.opts_store == "android":
    query_market = "google-play"
else:
    query_market = "ios"

# Request URI for Store Intelligence App History
url = "https://api.appannie.com/v1.2/intelligence/apps/" + \
    query_market + "/publisher/" + str(publisher_id) + "/history?" + \
    "countries=" + opts.opts_country + \
    "&categories=" + urllib2.quote(opts.opts_category)

# Add optional parameters to the Request URI
if isinstance(opts.opts_feeds, str):
    url = url + "&feeds=" + opts.opts_feeds
if isinstance(opts.opts_granularity, str):
    url = url + "&granularity=" + opts.opts_granularity
if isinstance(opts.opts_store, str):
    url = url + "&device=" + opts.opts_store

# Create a result file
filename = "result_StoreInt_PubHistory_" + opts.opts_store + \
          "_" + str(publisher_id) + \
          "_" + str(opts.opts_country) + \
          "_" + str(opts.opts_category).replace(" > ", "-") + \
          "_" + str(opts.opts_granularity) + \
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
exporter = annieapi.Exporter()

# Prepare for a file
exporter.filename = filename
exporter.prefix_columns = prefix_columns
exporter.main_element = response_main_element
exporter.columns = columns
exporter.is_write_header = int(opts.opts_write_header)
exporter.create_file()

# Main
request_url = url + "&start_date=" + start_date.strftime('%Y-%m-%d') + \
      "&end_date=" + end_date.strftime('%Y-%m-%d')
print request_url

# Retrieve a JSON response
try:
    response = request.get_response(request_url, key, user_agent)
except:
    sys.exit()

# Write data to the output file
exporter.response = response
exporter.to_tsv()

sys.exit()
