#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 Deepin, Inc.
#               2012 Hailong Qiu
#
# Author:     Hailong Qiu <356752238@qq.com>
# Maintainer: Hailong Qiu <356752238@qq.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import urllib
import re
import threading
import gobject

#进入字幕下载页面
# http://yyets.com/ (链接地址)showsubtitle-2070.html
#下载字幕链接
# http://yyets.com/ (下载链接)?mod=2&ac=download_attachment&id=2070&type=sub
# 下载链接: /?mod=2&ac=download_attachment&id=2070&type=sub
#人人影视

# http://yyets.com/?mod=2&ac=search_result&op=normal&class=subtitle&keyword=%E5%8A%9F%E5%A4%AB%E7%86%8A%E7%8C%AB &search=&page=2

# http://yyets.com/?mod=2&ac=search_result&op=normal&class=subtitle&keyword=%E5%8A%9F%E5%A4%AB%E7%86%8A%E7%8C%AB&search=&page2= (页码)


# main_http = "http://yyets.com/listsubtitle.html"

# HTTP_ADDRES = "http://yyets.com/listsubtitle.html"



class SubTitle(gobject.GObject):
    __gsignals__ = {
        "get-subtitle-info":(gobject.SIGNAL_RUN_LAST,
                           gobject.TYPE_NONE,(gobject.TYPE_STRING, gobject.TYPE_STRING,))
        }
    def __init__(self):
        gobject.GObject.__init__(self)        
        #用于下载和进入下载页面的.
        self.html_main = "http://yyets.com/"
        #用于搜索下载用的链接地址.[搜索]
        self.html_sourct = "http://yyets.com/?mod=2&ac=search_result&op=normal&class=subtitle&keyword="        
        self.html_page = "&search=&page=" #翻页.
        self.subtitle_num = 0 #搜索的个数.
        self.down_url_dict = {} #保存字幕下载链接的字典类型.
        self.down_url_list = [] #保存搜索到的字符串
        self.file_name = ""
        
        
        
        
    def Find(self, file_name):     
        '''find subtitle.'''
        self.file_name = file_name
        html_search = urllib.urlopen(self.html_sourct + file_name).read()
        fp = open(self.file_name, "w")
        fp.write(html_search)
        fp.close()
                
        self.subtitle_num = self.get_find_subtitle_num() #获取字幕的个数        
        print "Test:Get subtitle:" + str(self.subtitle_num)
        
        self.get_down_url_address() #得到字幕下载链接地址字符串,并保存在字典类型中.                    

            
    def get_find_subtitle_num(self):    
        fp = open(self.file_name, "r")
        str_fp = unicode(fp.read(), "utf-8")
        fp.close()        
        p = re.compile(ur"(共有.+个搜索结果)")
        str_line = p.findall(str_fp)
        p2 = re.compile(ur"(>\d+<)")
        str_num = p2.findall(str_line[0])[0]        
        str_num = str_num.strip("<")
        str_num = str_num.strip(">")
        return int(str_num)
        
    def get_down_url_address(self):
        # Init.
        self.down_url_dict = {}
        self.down_url_list = []
        subtitle_sum = 0
        i = 0
        while subtitle_sum < self.subtitle_num:
            i += 1
            html_search = urllib.urlopen(self.html_sourct + self.file_name + "&search=&page=%d" % (i)).read()
            fp = open(self.file_name, "w")
            fp.write(html_search)
            fp.close()
            
            fp = open(self.file_name, "r")
            str_fp = unicode(fp.read(), "utf-8")
            fp.close()                
            p = re.compile(ur'(<li class="name"><font color.+%s.+</a> <em>  </em></li>)' % (self.file_name.decode('UTF-8')))
            str_line = p.findall(str_fp)                        
            for i_str in str_line: # save down_url_list.
                self.down_url_list.append(i_str)
            subtitle_sum += len(str_line)
            
        # subtitle down url to dict.    
        # print self.down_url_list
        path_thread_id = threading.Thread(target=self.down_list_to_dict)
        path_thread_id.start()                        
        
    def down_list_to_dict(self):        
        for list_i in self.down_url_list:
            # get subtitle name.
            p = re.compile(ur'(%s.+</a>)' % (self.file_name.decode('UTF-8')))
            str_line = p.findall(list_i)                                    
            subtitle_pos = str_line[0].index('<')
            subtitle_name = str_line[0][0:subtitle_pos] +  str_line[0][subtitle_pos+7:]
            subtitle_name = subtitle_name[:-4]
            # print subtitle_name
            # get subtitle down address.            
            p = re.compile(ur'(<a href=.+html\">)')
            str_line = p.findall(list_i)                                    
            subtitle_down_address = str_line[0][11:]
            subtitle_down_address = subtitle_down_address.strip(">")
            subtitle_down_address = self.html_main + subtitle_down_address.strip('"')
            # print subtitle_down_address
            
            #Save subtitle name and down address.
            self.down_url_dict[subtitle_name] = subtitle_down_address                        
            self.emit("get-subtitle-info", subtitle_name, subtitle_down_address)
                        
        
    def down_url_to_path(self, down_url, file_path_and_name):
        #local down.
        html_search = unicode(urllib.urlopen(down_url).read(), "utf-8")
        p = re.compile(ur'(本地下载.+sub\">)')
        subtitle_down_address = p.findall(html_search)[0][16:].strip(">")
        subtitle_down_address = self.html_main + subtitle_down_address.strip('"')           
        urllib.urlretrieve(subtitle_down_address, file_path_and_name)
                
        
        
# Test get info.        
def test(subtitle, name, address):        
    print "'===' + test: ====",
    print '==' + name + '===='
    print '==' + address + '==='
    subtitle.down_url_to_path(address, "/home/long/" + name + ".rar")
    
if __name__ == "__main__":        
    sub_title = SubTitle()        
    sub_title.connect("get-subtitle-info", test)
    sub_title.Find("黑侠")
    # sub_title.Find("功夫熊猫")
    #sub_title.Find("黑")
    
    
    
        
        
# 要得到搜索结果的个数
# 将各个字幕链接地址保存起来. (有多页,自动进行翻页下载)
# 字典类型. 名字 对应下载地址
