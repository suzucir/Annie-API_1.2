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
# Set parameters which you'd like to see
# Need to set the exact same name as in API response

columns = ['rating', 'reviewer', 'version', 'text', 'language',
           'title', 'date', 'country', 'device']
response_main_element = 'reviews'

# set prefix_columns to put some specific data ahead of main data
# check exporter.prefix_data when you changed prefix_columns
prefix_columns = ['product_name']

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
    description='Extract App Annie Store Stats Review data \
                 via App Annie API')
parser.add_argument(
    "-i", "--id", dest="opts_id", metavar="ID", default="477865384",
    help="specify an app id (e.g. 477865384) compatible with GP class codes")
parser.add_argument(
    "-s", "--store", dest="opts_store", metavar="STORE", default="iphone",
    help="specify a type of device (Options: ios | iphone | ipad | android)")
parser.add_argument(
    "-c", "--country", dest="opts_country", metavar="CCODE", required=True,
    help="specify a country code (a two-letter code e.g. JP, US, CN)")
parser.add_argument(
    "-p", "--page_index", dest="opts_page_index", metavar="PAGEINDEX",
    default="0", help="for the large response")
parser.add_argument(
    "-b", "--start_date", dest="opts_start_date", metavar="STARTDATE",
    help="default is the beggining date", required=True)
parser.add_argument(
    "-e", "--end_date", dest="opts_end_date", metavar="ENDDATE",
    help="dafault is today", required=True)
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
    product_id = opts.opts_id

# Request URI for Intelligence Top Chart
url = "https://api.appannie.com/v1.2/apps/" + \
    query_market + "/app/" + str(product_id) + "/reviews?"

if isinstance(opts.opts_country, str):
    url = url + "countries=" + opts.opts_country

# Result File
filename = "result_StoreStats_Reviews_" + opts.opts_store + \
          "_" + opts.opts_country + \
          "_" + str(product_id) + \
          "_" + str(opts.opts_start_date) + \
          "_" + str(opts.opts_end_date) + \
          ".tsv"

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

start_date = datetime.datetime.strptime(opts.opts_start_date, '%Y-%m-%d')
end_date = datetime.datetime.strptime(opts.opts_end_date, '%Y-%m-%d')
run_date = start_date


while (end_date - run_date).days + 1 > 0:
    request_url = url + "&start_date=" + run_date.strftime('%Y-%m-%d') + \
                "&end_date=" + run_date.strftime('%Y-%m-%d')
    print request_url
    response = request.get_response(request_url, key, user_agent)

    # Write data to the output file
    exporter.response = response
    exporter.to_tsv()

    while response['next_page'] is not None:
        next_page_url = "https://api.appannie.com" + \
                        response['next_page']
        response = request.get_response(next_page_url, key, user_agent)
        exporter.response = response
        exporter.to_tsv()

    run_date = run_date + datetime.timedelta(days=1)

sys.exit()
