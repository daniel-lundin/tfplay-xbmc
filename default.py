import sys
import xbmcplugin
import xbmcgui
import xbmc

from navigation import Navigation
import tfplay


if __name__ == '__main__':
    navigation = Navigation(tfplay.TFPlay(), xbmc, xbmcplugin, xbmcgui, sys.argv)
    navigation.dispatch()


