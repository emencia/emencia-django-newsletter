# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# Author: Eugene Kin Chee Yip
# Date:   16 January 2010
# Modified by: Fantomas42

import copy

from django.utils.simplejson import dumps


class Chart(dict):
    replaceKeyDictionary = {
        'on_show': 'on-show', 'on_click': 'on-click',
        'start_angle': 'start-angle', 'javascript_function': 'javascript-function',
        'threeD': '3d', 'tick_height': 'tick-height',
        'grid_colour': 'grid-colour', 'tick_length': 'tick-length',
        'spoke_labels': 'spoke-labels', 'barb_length': 'barb-length',
        'dot_style': 'dot-style', 'dot_size': 'dot-size',
        'halo_size': 'halo-size', 'line_style': 'line-style',
        'outline_colour': 'outline-colour', 'fill_alpha': 'fill-alpha',
        'gradient_fill': 'gradient-fill', 'negative_colour': 'negative-colour'}

    def __init__(self, *ka, **kw):
        for key, value in kw.items():
            self.__dict__[key] = value

    def __getattribute__(self, key):
        try:
            return dict.__getattribute__(self, key)
        except AttributeError:
            self.__dict__[key] = Chart()
            return dict.__getattribute__(self, key)

    def __copy__(self):
        attributes = dict()
        for key, value in self.__dict__.items():
            if isinstance(value, list):
                attributes[self.replaceKey(key)] = [copy.copy(item) for item in value]
            else:
                attributes[self.replaceKey(key)] = copy.copy(value)
        return attributes

    def replaceKey(self, key):
        if (key in self.replaceKeyDictionary):
            return self.replaceKeyDictionary[key]
        else:
            return key

    def render(self):
        attributes = copy.copy(self)
        return dumps(attributes)
