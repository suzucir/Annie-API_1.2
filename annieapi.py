#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright Shigenori Suzuki <suzuki@appannie.com>
#

import urllib2
import datetime
import simplejson as json


def request_api(url, key, user_agent):
    headers = {'Authorization': key, 'User-Agent': user_agent}
    api_req = urllib2.Request(url, headers=headers)
    api_response = urllib2.urlopen(api_req)
    api_response_body = json.loads(api_response.read())
    return api_response_body


def next_month(d):
    if d.month == 12:
        return datetime.datetime(d.year + 1, 1, d.day)
    else:
        return datetime.datetime(d.year, d.month + 1, d.day)


class Request:
    """docstring for """
    def __init__(self):
        self.url = ""
        self.key = ""
        self.user_agent = ""

    def get_response(self, url, key, user_agent):
        request_headers = {'Authorization': key, 'User-Agent': user_agent}
        api_request = urllib2.Request(url, headers=request_headers)
        api_open = urllib2.urlopen(api_request)
        api_response = json.loads(api_open.read())
        return api_response


class Exporter:
    """docstring for """
    def __init__(self):
        self.columns = ""
        self.filename = "default.tsv"
        self.delimiter = "\t"
        self.main_element = ""
        self.response = ""
        self.is_write_header = 1
        self.prefix_columns = ""

    def create_file(self):
        f = open(self.filename, "w")
        if self.is_write_header:
            if self.prefix_columns:
                f.write(self.delimiter.join(self.prefix_columns))
                f.write(self.delimiter)
            f.write(self.delimiter.join(self.columns))
            f.write('\n')
        f.close()

    def to_tsv(self):
        f = open(self.filename, "a")
        for i in self.response[self.main_element]:
            if self.prefix_columns:
                prefix_data = []
                for j in self.prefix_columns:
                    if self.response[j] is None:
                        prefix_data.append("")
                    elif isinstance(self.response[j], int):
                        prefix_data.append(str(self.response[j]))
                    elif isinstance(self.response[j], float):
                        prefix_data.append(str(self.response[j]))
                    else:
                        prefix_data.append(self.response[j])
                f.write(self.delimiter.join(prefix_data))
                f.write(self.delimiter)

            data = []
            for j in self.columns:
                if i[j] is None:
                    data.append("")
                elif isinstance(i[j], int):
                    data.append(str(i[j]))
                elif isinstance(i[j], float):
                    data.append(str(i[j]))
                else:
                    data.append(i[j])
            f.write(self.delimiter.join(data))
            f.write('\n')
        f.close()

    def print_json(self):
        if self.is_write_header:
            print self.delimiter.join(self.columns)
        for i in self.jsondata:
            data = []
            for j in self.columns:
                if isinstance(i[j], int):
                    data.append(str(i[j]))
                else:
                    data.append(i[j])
            print self.delimiter.join(data)

    def print_columns(self):
        print self.delimiter.join(self.columns)
