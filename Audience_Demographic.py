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
prefix_columns = ['market', 'country',
                  'product_id', 'product_code', 'product_name',
                  'device', 'product_category',
                  'unified_product_id', 'unified_product_name',
                  'publisher_id', 'publisher_name',
                  'company_id', 'company_name',
                  'parent_company_id', 'parent_company_name',
                  ]

# Element name for main contents
response_main_element = 'list'

# Need to set the exact same name as in API response
columns = ['start_date',
           'gender_index_male', 'gender_index_female',
           'age_index_13_24', 'age_index_25_44', 'age_index_45_plus',
           'gender_percent_male', 'gender_percent_female',
           'age_percent_13_24', 'age_percent_25_44', 'age_percent_45_plus'
           ]

# for Brazil, Hong Kong, Indonesia, Italy, Mexico, Spain, Taiwan, Turkey
two_grp_countries = ['BR', 'HK', 'ID', 'IT', 'MX', 'ES', 'TW', 'TR']
columns2 = ['start_date',
            'gender_index_male', 'gender_index_female',
            'age_index_13_24', 'age_index_25_plus',
            'gender_percent_male', 'gender_percent_female',
            'age_percent_13_24', 'age_percent_25_plus'
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
    description='Extract App Annie Audiecne Intelligence App Demographic \
                 data via App Annie API')
parser.add_argument(
    "-s", "--store", dest="opts_store", metavar="STORE", default="ios",
    help="specify a type of device (Options: ios | gooogle-play)")
parser.add_argument(
    "-i", "--id", dest="opts_id", metavar="ID", default="443904275",
    help="specify an app id (e.g. 443904275) compatible with GP class codes")
parser.add_argument(
    "-c", "--country", dest="opts_country", metavar="CCODE", default="JP",
    help="specify a country code (a two-letter code e.g. JP, US, CN)")
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
    query_market = "all-android"
    if "." in opts.opts_id:
        url = "https://api.appannie.com/v1.2/apps/google-play" + \
             "/package-codes2ids?package_codes=" + str(product_id)
        # API Call & Response
        android_app_id = annieapi.request_api(url, key, user_agent)
        product_id = android_app_id['items'][0]['product_id']
else:
    query_market = opts.opts_store

# Request URI for Store Intelligence App History
url = "https://api.appannie.com/v1.2/intelligence/apps/" + \
    query_market + "/app/" + str(product_id) + "/demographics?" + \
    "countries=" + opts.opts_country


# Create a result file
filename = "result_Audience_Demographics_" + opts.opts_store + \
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
exporter = annieapi.Exporter()

# Prepare for a file
exporter.filename = filename
exporter.prefix_columns = prefix_columns
exporter.main_element = response_main_element
if opts.opts_country in two_grp_countries:
    exporter.columns = columns2
else:
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
