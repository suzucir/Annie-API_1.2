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
prefix_columns = ['code']

# Element name for main contents
response_main_element = 'product'

# Need to set the exact same name as in API response
columns = ['market', 'product_id', 'product_name',
           'publisher_id', 'publisher_name', 'release_date', 'size',
           'languages', 'main_category', 'other_categories', 'description'
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
    description='Extracting App Annie Store Intelligence App History data \
                 via App Annie API')
parser.add_argument(
    "-s", "--store", dest="opts_store", metavar="STORE", default="ios",
    help="specify a type of device (Options: all | iphone | ipad | android)")
parser.add_argument(
    "-i", "--id", dest="opts_id", metavar="ID", default="443904275",
    help="specify an app id (e.g. 443904275) compatible with GP class codes")
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
else:
    query_market = opts.opts_store

if "." in opts.opts_id:
    url = "https://api.appannie.com/v1.2/apps/" + query_market + \
            "/package-codes2ids?package_codes=" + str(product_id)
    # API Call & Response
    android_app_id = annieapi.request_api(url, key, user_agent)
    product_id = android_app_id['items'][0]['product_id']


# Request URI for Store Intelligence App History
url = "https://api.appannie.com/v1.2/apps/" + \
    query_market + "/app/" + str(product_id) + "/details"


# Create a result file
filename = "result_StoreStat_Details_" + opts.opts_store + \
          "_" + str(product_id) + \
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

# Main
request_url = url
print request_url

# Retrieve a JSON response
try:
    response = request.get_response(request_url, key, user_agent)
except:
    sys.exit()

# Write data to the output file
exporter.response = response
exporter.to_tsv2()

sys.exit()
