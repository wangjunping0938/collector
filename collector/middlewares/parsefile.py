# -*- coding: utf-8 -*-
#
# Parsing configuration file content

from configparser import ConfigParser


class ParseFile(object):

    @classmethod
    def parse2dict(cls, filename, option_name):
        CP = ConfigParser()
        CP.read(filename)
        options = CP.items(option_name)
        keys, values = (o[0] for o in options), (o[1] for o in options)
        return dict(zip(keys, values))


if __name__ == '__main__':
    filename = 'collector/settings/.config.cfg'
    result = ParseFile.parse2dict(filename, 'webinterface')
    from pprint import pprint
    pprint(result)
