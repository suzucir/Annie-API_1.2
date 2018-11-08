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
prefix_columns = ['market', 'granularity', 'country', 'segment',
                  'product_id', 'product_code', 'product_name',
                  'product_category',
                  'unified_product_id', 'unified_product_name',
                  'publisher_id', 'publisher_name',
                  'company_id', 'company_name',
                  'parent_company_id', 'parent_company_name'
                  ]

# Element name for main contents
response_main_element = 'list'

# Need to set the exact same name as in API response
columns = ['device', 'date',
           'usage_penetration', 'active_users', 'install_penetration',
           'open_rate', 'total_minutes',
           'total_sessions', 'avg_sessions_per_user',
           'avg_session_duration', 'avg_time_per_user', 'avg_active_days',
           'mb_per_user', 'mb_per_session'
           ]

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
    description='Extract App Annie Usage Intelligence App History data \
                 via App Annie API')
parser.add_argument(
    "-d", "--device", dest="opts_device", metavar="DEVICE", default="iphone",
    help="specify a type of device (Options	ios | iphone | ipad | android \
         | android_phone | android_tablet )")
parser.add_argument(
    "-i", "--id", dest="opts_id", metavar="ID", default="443904275",
    help="specify an app id (e.g. 443904275) compatible with GP class codes")
parser.add_argument(
    "-c", "--country", dest="opts_country", metavar="CCODE", default="JP",
    help="specify a country code (a two-letter code e.g. JP, US, CN)")
parser.add_argument(
    "-g", "--granularity", dest="opts_granularity",
    metavar="GRANULARITY", default="daily",
    help="specify data granularity (Options: monthly | weekly | daily)")
parser.add_argument(
    "-s", "--segment", dest="opts_segment", metavar="SEGMENT",
    default="all_users",
    help="specify a type of user segments (Options: all_users | all_13_24 \
          | all_25_44 | all_25_plus | all_45_plus | all_females \
          | females_13_24 | females_25_44 | females_25_plus | females_45_plus \
          | all_males | males_13-24 | males_25-44 | males_25_plus \
          | males_45_plus | product_id (product ID for iOS and GP app used)")
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
if opts.opts_device in ["android", "android_phone", "android_tablet"]:
    query_market = "all-android"
    if "." in opts.opts_id:
        url = "https://api.appannie.com/v1.2/apps/" + query_market + \
             "/package-codes2ids?package_codes=" + str(product_id)
        # API Call & Response
        android_app_id = annieapi.request_api(url, key, user_agent)
        product_id = android_app_id['items'][0]['product_id']
else:
    query_market = "ios"

# Request URI for Store Intelligence App History
url = "https://api.appannie.com/v1.2/intelligence/apps/" + \
    query_market + "/app/" + str(product_id) + "/usage-history?" + \
    "countries=" + opts.opts_country

# Add optional parameters to the Request URI
if isinstance(opts.opts_granularity, str):
    url = url + "&granularity=" + opts.opts_granularity
if isinstance(opts.opts_device, str):
    url = url + "&device=" + opts.opts_device
if isinstance(opts.opts_segment, str):
    url = url + "&segment=" + opts.opts_segment

# Create a result file
filename = "result_Usage_AppHistory_" + opts.opts_device + \
          "_" + str(product_id) + \
          "_" + str(opts.opts_country) + \
          "_" + str(opts.opts_granularity) + \
          "_" + str(opts.opts_segment) + \
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
