#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2013 Deepin, Inc.
#               2013 Hailong Qiu
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


from utils import propagate_expose
import math
import cairo
import gtk


class MenuWindow(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self, gtk.WINDOW_POPUP)
        self.__init_values()
        self.__init_settings()
        self.__init_events()

    def __init_values(self):
        self.on_paint_expose_event = None
        self.alpha = 1.0
        # 阴影.
        self.__sahow_check = True
        self.__sahow_value = 2
        self.__sahow_color = ("#FFFFFF", 0.5)
        #
        self.__surface = None
        #
        self.__old_w, self.__old_h = 0, 0

    def get_sahow_value(self):
        return self.__sahow_value

    def __init_settings(self):
        self.set_colormap(gtk.gdk.Screen().get_rgba_colormap())
        self.set_decorated(False)
        self.set_app_paintable(True)
        self.set_skip_pager_hint(True)
        self.set_skip_taskbar_hint(True)
        self.set_position(gtk.WIN_POS_NONE)
        self.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_MENU)
        self.set_opacity(self.alpha)

    def __init_events(self):
        self.add_events(gtk.gdk.ALL_EVENTS_MASK)
        self.connect("size-allocate", self.__on_size_allocate)
        self.connect("expose-event", self.__expose_event)
        self.connect("destroy", lambda w : gtk.main_quit())
    
    def __on_size_allocate(self, widget, alloc):
        x, y, w, h = self.allocation
        # 防止重复的加载.
        if (self.__old_w == w and self.__old_h == h):
            return False

        self.__surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        self.__surface_context = cairo.Context(self.__surface)
        self.__compute_shadow(w, h)
        #
        self.__old_w = w
        self.__old_h = h

    def __compute_shadow(self, w, h):
        #cr = self.__surface_context
        x, y = 0, 0
        '''
        self.on_draw_rectangle(x, y, w, h)
        cr.set_source_rgba(*alpha_color_hex_to_cairo((self.__sahow_color)))
        cr.fill_preserve()
        gaussian_blur(self.__surface, self.__sahow_value)
        # 画外边框.
        cr.clip()
        self.on_draw_rectangle(x, y, w, h)
        self.__border_out_color = ("#000000", 1.0)
        cr.set_source_rgba(*alpha_color_hex_to_cairo((self.__border_out_color)))
        cr.fill_preserve()
        # 画内边框.
        cr.clip()
        self.on_draw_rectangle(x + 0.5, y + 0.5, w, h)
        self.__border_out_color = ("#FFFFFF", 0.9)
        cr.set_source_rgba(*alpha_color_hex_to_cairo((self.__border_out_color)))
        cr.fill_preserve()
        '''

    def on_draw_rectangle(self, x, y, w, h):
        cr = self.__surface_context
        radius = 5
        x += radius
        y += radius
        w =  w - x * 2
        h =  h - y * 2
        # 集合.
        arc_set = [
            (x + radius,      y + radius,     radius, 1 * math.pi,   1.5 * math.pi),
            (x + w - radius,  y + radius,     radius, math.pi * 1.5, math.pi * 2.0),
            (x + w - radius,  y + h - radius, radius, 0,             math.pi * 0.5),
            (x + radius,      y + h - radius, radius, math.pi * 0.5, math.pi)
            ]
        #
        for x, y, r, start, end in arc_set:
            cr.arc(x, y, r, start, end)
        cr.close_path()

    def __expose_event(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        #
        cr.rectangle(*rect)
        cr.set_source_rgba(1, 1, 1, 0)
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.paint()
        #
        cr = widget.window.cairo_create()
        #
        '''
        if self.__sahow_check: # 是否显示阴影.
            self.draw_surface_expose_event(cr)
        else: # 如果不开启阴影.
            cr.set_source_rgba(1, 1, 1, 1.0)
            cr.paint()
        #
        '''
        if self.on_paint_expose_event:
            self.on_paint_expose_event(widget, event)
        #
        propagate_expose(widget, event)
        return True

    def draw_surface_expose_event(self, cr):
        if self.__surface:
            cr.set_source_surface(self.__surface, 0, 0)
            cr.paint()

if __name__ == "__main__":
    win = MenuWindow()
    win.move(300, 300)
    win.set_size_request(300, 300)
    win.show_all()
    gtk.main()



