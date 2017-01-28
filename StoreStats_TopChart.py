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

# Set prefix_columns to put some specific data ahead of main data
prefix_columns = ['market', 'device']

# Element name for main contents
response_main_element = 'products'

# Need to set the exact same name as in API response
columns = ['country', 'category', 'feed', 'date',
           'rank', 'rank_variation', 'product_id',
           'product_name', 'icon', 'price', 'has_iap',
           'publisher_id', 'publisher_name'
           ]

# #######################################################################
# Import from settings.py
# #######################################################################
# Set API Key and User-Agent
key = settings.key
user_agent = settings.user_agent

# #######################################################################
# Set up command line option for CUI using argparse
# #######################################################################
parser = argparse.ArgumentParser(
    description='Retrieve App Annie Store Intelligence Top Apps data \
                 via App Annie API')
parser.add_argument(
    "-s", "--store", dest="opts_store", metavar="STORE", default="ios",
    help="specify a type of device (Options	iphone | ipad | android)")
parser.add_argument(
    "-c", "--country", dest="opts_country", metavar="CCODE", default="JP",
    help="specify a country code (a two-letter code e.g. JP, US, CN)")
parser.add_argument(
    "-a", "--category", dest="opts_category", metavar="CATEGORY",
    default="Overall",
    help="specify a category (e.g. Overall > Games)")
parser.add_argument(
    "-f", "--feeds", dest="opts_feeds", metavar="FEEDS",
    default="free+paid+grossing",
    help="specify a type of feeds (Options	free | paid | grossing)")
parser.add_argument(
    "-r", "--ranks", dest="opts_ranks", metavar="RANKS",
    default="1000", help="result up to which rank should be returned")
parser.add_argument(
    "-p", "--page_index", dest="opts_page_index", metavar="PAGEINDEX",
    default="0", help="for the large response")
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

# Set up a string of "market"
if opts.opts_store == "android":
    query_market = "google-play"
else:
    query_market = "ios"

# Request URI for Store Intelligence Top Chart
url = "https://api.appannie.com/v1.2/apps/" + \
    query_market + "/ranking?" + \
    "&countries=" + opts.opts_country + \
    "&categories=" + urllib2.quote(opts.opts_category) + \
    "&ranks=" + opts.opts_ranks

# Add optional parameters to the Request URI
if isinstance(opts.opts_feeds, str):
    url = url + "&feeds=" + opts.opts_feeds
if isinstance(opts.opts_store, str):
    url = url + "&device=" + opts.opts_store

# Create a result file
filename = "result_StoreStats_TopChart_" + opts.opts_store + \
          "_" + str(opts.opts_country) + \
          "_" + str(opts.opts_category).replace(" > ", "-") + \
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
run_date = start_date

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
while (end_date - run_date).days + 1 > 0:
    request_url = url + "&start_date=" + run_date.strftime('%Y-%m-%d') + \
                        "&end_date=" + run_date.strftime('%Y-%m-%d')
    print request_url

    # Retrieve a JSON response
    response = request.get_response(request_url, key, user_agent)

    # Write data to the output file
    exporter.response = response
    exporter.to_tsv()
    run_date = run_date + datetime.timedelta(days=1)

sys.exit()
