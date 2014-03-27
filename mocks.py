# Mocks for testing


class Xbmc(object):
    BACK = 1

    class Keyboard(object):
        def __init__(self, placeholder, header, hidden):
            self.placeholder = placeholder
            self.header = header
            self.hidden = hidden

        def doModal(self):
            pass

        def isConfirmed(self):
            return True

        def getText(self):
            return raw_input('search>> ')

    def log(self, msg, level):
        pass

    class Player(object):
        def __init__(self):
            self.is_playing = False

        def play(self, *args, **kwargs):
            self.is_playing = True
            print 'playing stream %s (%s)'  % (kwargs['listitem'].infoLabels['Title'], kwargs['item'])
            return Xbmc.BACK

        def isPlaying(self):
            return self.is_playing

        def setSubtitles(self, sub_url):
            pass

        def showSubtitles(self, show):
            pass

    LOGERROR = 'ERROR'
    LOGNOTICE = 'NOTICE'


class Xbmcplugin(object):

    def __init__(self):
        self.dir_items = []

    def addDirectoryItem(self, handle, url, listitem, isFolder):
        self.dir_items.append((handle, url, listitem, isFolder))

    def endOfDirectory(self, handle):
        pass


class Xbmcgui(object):
    class ListItem(object):

        def __init__(self, *args, **kwargs):
            if len(args) == 1:
                self.caption = args[0]

        def setInfo(self, type, infoLabels):
            self.type = type
            self.infoLabels = infoLabels

        def setThumbnailImage(self, thumb_url):
            pass

    class Dialog(object):
        def ok(self, title, msg):
            print '[DIALOG] %s - %s' % (title, msg)
            return Xbmc.BACK

        def select(self, title, alternatives):
            print '[DIALOG SELECT] %s' % title
            print "\n".join(alternatives)
            return 0  # Select first one"

