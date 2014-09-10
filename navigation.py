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
        quoted_params = []
        for key in params:
            value = unicode(params[key])
            quoted_params.append((urllib.quote(key), urllib.quote(value.encode('unicode_escape'))))
        return "?" + "&".join(["%s=%s" % (a, b) for a, b in quoted_params])

    @staticmethod
    def decode_parameters(parameters):
        query = parameters[1:]
        params = query.split('&')
        result = {}
        for p in params:
            key, value = p.split('=')
            key = urllib.unquote(key)
            value = urllib.unquote(value.decode('unicode_escape')) #.decode('utf-8')
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
            'subtitles': json.dumps(item.subtitles)
        }
        is_folder = True
        try:
            action_url = self.plugin_url + Navigation.encode_parameters(params)
        except Exception, e:
            print 'Failed encoding skipping', str(e)
            print json.dumps(params)
            return

        caption = item.title
        if len(item.subtitles.keys()):
            caption += ' (with subtitles)'
        list_item = self.xbmcgui.ListItem(caption)
        list_item.setThumbnailImage(item.poster)
        return self.xbmcplugin.addDirectoryItem(handle=self.handle,
                                                url=action_url,
                                                listitem=list_item,
                                                isFolder=is_folder)

    def add_season_list_item(self, title, season_number):
        params = {
            'action': 'episodes',
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
                              episode_index, episode_name, episode_url, subtitles):
        params = {
            'action': 'play_episode',
            'title': title,
            'season_number': season_number,
            'episode_number': episode_index,
            'episode_url': episode_url,
            'subtitles': json.dumps(subtitles)
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
        self.add_menu_item('Movies', {'action': 'list_movies'})
        self.add_menu_item('Series', {'action': 'list_series'})
        self.add_menu_item('Just for kids', {'action': 'just_for_kids'})
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

    def just_for_kids(self):
        for item in self.tf.just_for_kids():
            self.add_movie_list_item(item)
        return self.xbmcplugin.endOfDirectory(self.handle)

    def list_movies(self):
        for item in self.tf.list_movies():
            self.add_movie_list_item(item)
        return self.xbmcplugin.endOfDirectory(self.handle)

    def list_series(self):
        for item in self.tf.list_series():
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

    def seasons(self, title, url, html):
        seasons = self.tf.parse_serie_page(html)
        for idx, s in enumerate(seasons):
            self.add_season_list_item(title, idx, url)
        return self.xbmcplugin.endOfDirectory(self.handle)

    def episodes(self, title, season_number):
        serie = self.tf.serie(title)

        for idx, e in enumerate(serie.seasons[season_number]):
            #epi_name, epi_url = epi_info
            self.add_episode_list_item(title, season_number,
                                       idx, e.episode, e.video_url, e.subtitles)
        return self.xbmcplugin.endOfDirectory(self.handle)

    def open_item(self, title, url, is_serie, subtitles):
        # TODO: check if serie
        if is_serie:
            serie = self.tf.serie(title)
            for s in serie.seasons:
                self.add_season_list_item(title, s)
            return self.xbmcplugin.endOfDirectory(self.handle)
        return self.play_stream(title, url, subtitles)

    def play_stream(self, title, stream, subtitles):
        has_subtitles = len(subtitles.keys())
        li = self.xbmcgui.ListItem(label=title, path=stream)
        li.setInfo(type='Video', infoLabels={"Title": title})

        selected_subtitle_url = None
        if has_subtitles:
            keys = subtitles.keys()
            subtitle_dialog = self.xbmcgui.Dialog()
            subs = [subtitles[x]['language'] for x in keys]
            answer = subtitle_dialog.select("Subtitle select", subs)
            if answer != -1:
                selected_subtitle_url = subtitles[keys[answer]]['file']

        player = self.xbmc.Player()
        player.play(item=stream, listitem=li)

        if selected_subtitle_url:
            while not player.isPlaying():
                self.xbmc.log('Not playing...', self.xbmc.LOGERROR)
                time.sleep(0.5)
            self.xbmc.log('Enabling subtitles', self.xbmc.LOGERROR)
            player.setSubtitles(selected_subtitle_url)
            player.showSubtitles(True)
        # This is just for the offline runner
        try:
            return self.xbmc.BACK
        except:
            pass

    def play_episode(self, title, season_number, episode_index, subtitles):
        serie = self.tf.serie(title)
        episode = serie.seasons[season_number][episode_index]
        return self.play_stream(title, episode.video_url, subtitles)

    def dispatch(self):
        if not self.params:
            return self.build_main_menu()
        if 'action' in self.params:
            action = self.params['action']
            if action == 'search':
                return self.search()
            if action == 'just_for_kids':
                return self.just_for_kids()
            if action == 'list_movies':
                return self.list_movies()
            if action == 'list_series':
                return self.list_series()
            if action == 'list_genres':
                return self.list_genres()
            if action == 'list_genre':
                return self.list_genre(self.params['genre'])
            if action == 'open_item':
                return self.open_item(self.params['title'],
                                      self.params['video_url'],
                                      int(self.params['is_serie']),
                                      json.loads(self.params['subtitles']))
            if action == 'episodes':
                return self.episodes(self.params['title'],
                                          int(self.params['season_number']))
            if action == 'play_episode':
                return self.play_episode(self.params['title'],
                                         int(self.params['season_number']),
                                         int(self.params['episode_number']),
                                         json.loads(self.params['subtitles']))

