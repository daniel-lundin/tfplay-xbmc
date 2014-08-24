import urllib
import time
import json


class Navigation(object):

    def __init__(self, tf, xbmc, xbmcplugin, xbmcgui, argv):
        self.tf = tf
        self.xbmc = xbmc
        self.xbmcplugin = xbmcplugin
        self.xbmcgui = xbmcgui
        self.plugin_url = argv[0]
        self.handle = int(argv[1])
        try:
            self.params = Navigation.decode_parameters(argv[2])
        except:
            self.params = None

    @staticmethod
    def encode_parameters(params):
        return '?' + urllib.urlencode(params)

    @staticmethod
    def decode_parameters(parameters):
        query = parameters[1:]
        params = query.split('&')
        result = {}
        for p in params:
            key, value = p.split('=')
            key = urllib.unquote(key)
            value = urllib.unquote(value).decode('utf-8')
            result[key] = value
        return result

    def add_menu_item(self, caption, params):
        url = self.plugin_url + Navigation.encode_parameters(params)

        list_item = self.xbmcgui.ListItem(caption)
        list_item.setInfo(type="Video", infoLabels={
            "Title": caption,
        })
        return self.xbmcplugin.addDirectoryItem(handle=self.handle, url=url,
                                                listitem=list_item,
                                                isFolder=True)

    def add_movie_list_item(self, item):
        params = {
            'action': 'open_item',
            'title': item.title,
            'video_url': item.video_url,
            'is_serie': item.is_serie,
        }
        is_folder = True
        try:
            action_url = self.plugin_url + Navigation.encode_parameters(params)
        except Exception, e:
            print 'Failed encoding skipping', str(e)
            print json.dumps(params)
            return

        caption = item.title
        ##if item.has_subs:
        ##    caption += ' (with subtitles)'
        list_item = self.xbmcgui.ListItem(caption)
        list_item.setThumbnailImage('http://tfplay.org/' + item.poster)
        return self.xbmcplugin.addDirectoryItem(handle=self.handle,
                                                url=action_url,
                                                listitem=list_item,
                                                isFolder=is_folder)

    def add_season_list_item(self, title, season_number):
        params = {
            'action': 'list_episodes',
            'season_number': season_number,
            'title': title
        }
        name = 'Season %d' % (season_number)
        action_url = self.plugin_url + Navigation.encode_parameters(params)
        list_item = self.xbmcgui.ListItem(name)
        list_item.setInfo(type='Video', infoLabels={'Title': name})
        return self.xbmcplugin.addDirectoryItem(handle=self.handle,
                                                url=action_url,
                                                listitem=list_item,
                                                isFolder=True)

    def add_episode_list_item(self, title, season_number,
                              episode_index, episode_name, episode_url):
        params = {
            'action': 'play_episode',
            'title': title,
            'season_number': season_number,
            'episode_number': episode_index,
            'episode_url': episode_url
        }

        name = '%s S%dE%d' % (title, season_number, episode_name)
        action_url = self.plugin_url + Navigation.encode_parameters(params)
        list_item = self.xbmcgui.ListItem(name)
        list_item.setInfo(type='Video', infoLabels={'Title': name})
        return self.xbmcplugin.addDirectoryItem(handle=self.handle,
                                                url=action_url,
                                                listitem=list_item,
                                                isFolder=False)

    def build_main_menu(self):
        self.add_menu_item('Search', {'action': 'search'})
        self.add_menu_item('Genres', {'action': 'list_genres'})
        return self.xbmcplugin.endOfDirectory(self.handle)

    def search(self):
        kb = self.xbmc.Keyboard('', 'Search', False)
        kb.doModal()
        if kb.isConfirmed():
            text = kb.getText()
            items = self.tf.search(text)
            for item in items:
                self.add_movie_list_item(item)
            return self.xbmcplugin.endOfDirectory(self.handle)

    def list_movie_items(self, items):
        for item in items:
            self.add_movie_list_item(item)
        return self.xbmcplugin.endOfDirectory(self.handle)

    def list_genres(self):
        for genre in self.tf.list_genres():
            self.add_menu_item(genre, {'action': 'list_genre', 'genre': genre})
        return self.xbmcplugin.endOfDirectory(self.handle)

    def list_genre(self, genre):
        items = self.tf.list_genre(genre)
        for item in items:
            self.add_movie_list_item(item)
        return self.xbmcplugin.endOfDirectory(self.handle)

    def open_item(self, title, url, is_serie):
        # TODO: check if serie
        if is_serie:
            serie = self.tf.list_serie(title)
            for s in serie.seasons:
                self.add_season_list_item(title, s)
            return self.xbmcplugin.endOfDirectory(self.handle)
        return self.play_stream(title, url)
        #html = self.tf._get(url)
        #if self.tf.is_serie(html):
        #    return self.list_seasons(title, url, html)
        #player_url = self.tf.parse_movie_page(html)
        #stream_url, subtitles = self.tf.parse_player_page(self.tf._get(player_url))

        #return self.play_stream(title, stream_url, subtitles)

    def play_stream(self, title, stream):#, subtitles):
        li = self.xbmcgui.ListItem(label=title, path=stream)
        li.setInfo(type='Video', infoLabels={"Title": title})

        #selected_subtitle_url = None
        #if subtitles:
        #    subtitle_dialog = self.xbmcgui.Dialog()
        #    subs = [s.label for s in subtitles]
        #    answer = subtitle_dialog.select("Subtitle select", subs)
        #    if answer != -1:
        #        selected_subtitle_url = subtitles[answer].url

        player = self.xbmc.Player()
        player.play(item=stream, listitem=li)

        #if selected_subtitle_url:
        #    while not player.isPlaying():
        #        self.xbmc.log('Not playing...', self.xbmc.LOGERROR)
        #        time.sleep(0.5)
        #    self.xbmc.log('Enabling subtitles', self.xbmc.LOGERROR)
        #    player.setSubtitles(selected_subtitle_url)
        #    player.showSubtitles(True)
        # This is just for the offline runner
        try:
            return self.xbmc.BACK
        except:
            pass

    def play_episode(self, title, season_number, episode_index):
        serie = self.tf.list_serie(title)
        episode = serie.seasons[season_number][episode_index]
        return self.play_stream(title, episode.video_url)

    def list_seasons(self, title, url, html):
        seasons = self.tf.parse_serie_page(html)
        for idx, s in enumerate(seasons):
            self.add_season_list_item(title, idx, url)
        return self.xbmcplugin.endOfDirectory(self.handle)

    def list_episodes(self, title, season_number):
        serie = self.tf.list_serie(title)

        for idx, e in enumerate(serie.seasons[season_number]):
            #epi_name, epi_url = epi_info
            self.add_episode_list_item(title, season_number,
                                       idx, e.episode, e.video_url)
        return self.xbmcplugin.endOfDirectory(self.handle)

    def dispatch(self):
        if not self.params:
            return self.build_main_menu()
        if 'action' in self.params:
            action = self.params['action']
            if action == 'search':
                return self.search()
            if action == 'list_genres':
                return self.list_genres()
            if action == 'list_genre':
                return self.list_genre(self.params['genre'])
            if action == 'open_item':
                return self.open_item(self.params['title'],
                                      self.params['video_url'],
                                      int(self.params['is_serie']))
            if action == 'list_episodes':
                return self.list_episodes(self.params['title'],
                                          int(self.params['season_number']))
            if action == 'play_episode':
                return self.play_episode(self.params['title'],
                                         int(self.params['season_number']),
                                         int(self.params['episode_number']))

