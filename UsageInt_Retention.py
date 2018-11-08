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

response_main_element = 'list'
columns = ['device']
response_main_element2 = 'user_retention'
columns2 = ['user_retention']
# columns2 = ['user_retention', 'category_benchmark']

# set prefix_columns to put some specific data ahead of main data
# check exporter.prefix_data when you changed prefix_columns
prefix_columns = ['market', 'country', 'product_id', 'product_name',
                  'publisher_id', 'publisher_name', 'unified_product_id',
                  'unified_product_name', 'product_category']

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
    description='Retrieve Usage Retention data \
                 via App Annie API')
parser.add_argument(
    "-i", "--id", dest="opts_id", metavar="ID", default="477865384",
    help="specify an app id (e.g. 477865384) compatible with GP class codes")
parser.add_argument(
    "-s", "--store", dest="opts_store", metavar="STORE", default="android",
    help="specify a type of device (Options: iphone+ipad | android)")
parser.add_argument(
    "-c", "--country", dest="opts_country", metavar="CCODE",
    help="specify a country code (a two-letter code e.g. JP, US, CN)")
parser.add_argument(
    "-b", "--start_date", dest="opts_start_date", metavar="STARTDATE",
    help="default is the beggining date")
parser.add_argument(
    "-e", "--end_date", dest="opts_end_date", metavar="ENDDATE",
    help="dafault is today")
parser.add_argument(
    "-t", "--types", dest="opts_types", metavar="TYPES",
    default="All", help="retrieve results for a specific feature type")
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
    query_market = "all-android"
    product_id = opts.opts_id
else:
    query_market = "ios"
    product_id = opts.opts_id

# Request URI for Intelligence Top Chart
url = "https://api.appannie.com/v1.2/intelligence/apps/" + \
    query_market + "/app/" + str(product_id) + "/user-retention?"

if isinstance(opts.opts_country, str):
    url = url + "&countries=" + opts.opts_country


# Result File
filename = "result/result_Usage_Retention_" + opts.opts_store + \
          "_" + str(product_id) + \
          "_" + str(opts.opts_start_date) + \
          "_" + str(opts.opts_end_date) + \
          ".tsv"

if isinstance(opts.opts_file_prefix, str):
    filename = opts.opts_file_prefix + "_" + filename

# Make a Request insatance
request = annieapi.Request()
exporter = annieapi.Exporter()

# Prepare for a file
exporter.filename = filename
exporter.prefix_columns = prefix_columns
exporter.main_element = response_main_element
exporter.columns = columns
exporter.main_element2 = response_main_element2
exporter.columns2 = columns2
exporter.is_write_header = int(opts.opts_write_header)
exporter.create_file()

start_date = datetime.datetime.strptime(opts.opts_start_date, '%Y-%m-%d')
end_date = datetime.datetime.strptime(opts.opts_end_date, '%Y-%m-%d')
request_url = url + "&start_date=" + start_date.strftime('%Y-%m-%d') + \
            "&end_date=" + end_date.strftime('%Y-%m-%d')
print request_url
response = request.get_response(request_url, key, user_agent)

# Write data to the output file
exporter.response = response
exporter.to_tsv_retention()

sys.exit()
