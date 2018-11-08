#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright Shigenori Suzuki <suzuki@appannie.com>
#

import sys
import urllib2
import datetime
import simplejson as json


def request_api(url, key, user_agent):
    headers = {'Authorization': key, 'User-Agent': user_agent}
    api_req = urllib2.Request(url, headers=headers)
    try:
        api_response = urllib2.urlopen(api_req)
    except urllib2.HTTPError as e:
        error_msg = json.loads(e.read())
        print "HTTP Error: ", e.code, e.msg
        print "Reason: ", error_msg['error']
        sys.exit()
    except urllib2.URLError as e:
        print "URL Error", e
        sys.exit()
    api_response_body = json.loads(api_response.read())
    return api_response_body


def next_month(d):
    if d.month == 12:
        return datetime.datetime(d.year + 1, 1, d.day)
    else:
        return datetime.datetime(d.year, d.month + 1, d.day)


class Request:
    """ Class for API Request """
    def __init__(self):
        self.url = ""
        self.key = ""
        self.user_agent = ""

    def get_response(self, url, key, user_agent):
        api_response = request_api(url, key, user_agent)
        return api_response


class Exporter:
    """ Class for exporting data """
    def __init__(self):
        self.columns = ""
        self.main_element = ""
        self.columns2 = ""
        self.main_element2 = ""
        self.filename = "default.tsv"
        self.delimiter = "\t"
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
            if self.columns2:
                f.write(self.delimiter)
                f.write(self.delimiter.join(self.columns2))
                f.write(self.delimiter)
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
                elif j == "text":
                    text = "\"" + str(i[j].encode('utf_8')
                                          .replace('\n', '  ')
                                          .replace('\r', ' ')
                                          .replace('\t', ' ')
                                          .replace('"', '\'')) + "\""
                    data.append(text)
                elif isinstance(i[j], int):
                    data.append(str(i[j]))
                elif isinstance(i[j], float):
                    data.append(str(i[j]))
                elif isinstance(i[j], list):
                    data.append(", ".join(i[j]))
                else:
                    data.append(i[j])
            f.write(self.delimiter.join(data))
            f.write('\n')
        f.close()

    def to_tsv_ss_details(self):
        f = open(self.filename, "a")
        i = self.response[self.main_element]
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
            elif j == "description":
                text = "\"" + str(i[j].encode('utf_8')
                                      .replace('\n', '  ')
                                      .replace('\r', ' ')
                                      .replace('\t', ' ')
                                      .replace('"', '\'')) + "\""
                data.append(text)
            elif isinstance(i[j], int):
                data.append(str(i[j]))
            elif isinstance(i[j], float):
                data.append(str(i[j]))
            elif isinstance(i[j], list):
                data.append(", ".join(i[j]))
            else:
                data.append(i[j])
        f.write(self.delimiter.join(data))
        f.write('\n')
        f.close()

    def to_tsv_ss_topiap(self):
        f = open(self.filename, "a")
        i = self.response[self.main_element]
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
        for k in i['top_iaps']:
            for j in self.columns:
                if i[j] is None:
                    data.append("")
                elif j == "description":
                    text = "\"" + str(i[j].encode('utf_8')
                                        .replace('\n', '  ')
                                        .replace('\r', ' ')
                                        .replace('\t', ' ')
                                        .replace('"', '\'')) + "\""
                    data.append(text)
                    data.append(text)
                elif isinstance(i[j], int):
                    data.append(str(i[j]))
                elif isinstance(i[j], float):
                    data.append(str(i[j]))
                elif isinstance(i[j], list):
                    data.append(", ".join(i[j]))
                else:
                    data.append(i[j])
            data.append(str(k['rank']))
            data.append(str(k['name']))
            data.append(str(k['price']))
            f.write(self.delimiter.join(data))
            f.write('\n')
            data = []        
        f.close()

    def to_tsv_features(self):
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
                elif j == "text":
                    text = "\"" + str(i[j].encode('utf_8')
                                          .replace('\n', '  ')
                                          .replace('\r', ' ')
                                          .replace('\t', ' ')
                                          .replace('"', '\'')) + "\""
                    data.append(text)
                elif isinstance(i[j], int):
                    data.append(str(i[j]))
                elif isinstance(i[j], float):
                    data.append(str(i[j]))
                elif isinstance(i[j], list):
                    data.append(", ".join(i[j]))
                else:
                    data.append(i[j])

            for k in self.columns2:
                if i[self.main_element2][k] is None:
                    data.append("")
                elif isinstance(i[self.main_element2][k], int):
                    data.append(str(i[self.main_element2][k]))
                elif isinstance(i[self.main_element2][k], float):
                    data.append(str(i[self.main_element2][k]))
                elif isinstance(i[self.main_element2][k], list):
                    data.append(", ".join(i[self.main_element2][k]))
                else:
                    data.append(i[self.main_element2][k])
            f.write(self.delimiter.join(data))
            f.write('\n')
        f.close()

    def to_tsv_retention(self):
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
            for j in i[self.main_element2]:
                data = []
                data.append(str(j))
                for k in i[self.main_element2][j]:
                    data.append(str(k))
                f.write(self.delimiter.join(prefix_data))
                f.write(self.delimiter)
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
