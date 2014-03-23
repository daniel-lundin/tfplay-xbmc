import urllib


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

    def add_movie_list_item(self, caption, url, thumb_url=None):
        params = {
            'action': 'open_item',
            'title': caption,
            'item_url': url,
        }
        is_folder = True
        action_url = self.plugin_url + Navigation.encode_parameters(params)
        list_item = self.xbmcgui.ListItem(caption)
        if thumb_url:
            list_item.setThumbnailImage(thumb_url)
        return self.xbmcplugin.addDirectoryItem(handle=self.handle,
                                                url=action_url,
                                                listitem=list_item,
                                                isFolder=is_folder)

    def add_season_list_item(self, title, season_number, serie_url):
        params = {
            'action': 'list_episodes',
            'season_number': season_number,
            'title': title,
            'serie_url': serie_url
        }
        name = 'Season %d' % (season_number + 1)
        action_url = self.plugin_url + Navigation.encode_parameters(params)
        list_item = self.xbmcgui.ListItem(name)
        list_item.setInfo(type='Video', infoLabels={'Title': name})
        return self.xbmcplugin.addDirectoryItem(handle=self.handle,
                                                url=action_url,
                                                listitem=list_item,
                                                isFolder=True)

    def add_episode_list_item(self, title, season_number,
                              episode_number, episode_name, episode_url):
        params = {
            'action': 'play_episode',
            'title': title,
            'season_number': season_number,
            'episode_number': episode_number,
            'episode_url': episode_url
        }
        name = episode_name
        action_url = self.plugin_url + Navigation.encode_parameters(params)
        list_item = self.xbmcgui.ListItem(name)
        list_item.setInfo(type='Video', infoLabels={'Title': name})
        return self.xbmcplugin.addDirectoryItem(handle=self.handle,
                                                url=action_url,
                                                listitem=list_item,
                                                isFolder=False)

    def build_main_menu(self):
        self.add_menu_item('Search', {'action': 'search'})
        self.add_menu_item('Popular movies', {'action': 'popular_movies'})
        self.add_menu_item('Newest movies', {'action': 'newest_movies'})
        self.add_menu_item('Newest series', {'action': 'newest_series'})
        self.add_menu_item('Newest for kids', {'action': 'newest_for_kids'})
        return self.xbmcplugin.endOfDirectory(self.handle)

    def search(self):
        kb = self.xbmc.Keyboard('', 'Search', False)
        kb.doModal()
        if kb.isConfirmed():
            text = kb.getText()
            matches = self.tf.search(text)
            for m in matches:
                self.add_movie_list_item(m[0], m[1])
            return self.xbmcplugin.endOfDirectory(self.handle)

    def list_movie_items(self, items):
        for item in items:
            self.add_movie_list_item(item.title, item.url, item.thumb_url)
        return self.xbmcplugin.endOfDirectory(self.handle)

    def list_popular_movies(self):
        self.list_movie_items(self.tf.list_popular_movies())

    def list_newest_movies(self):
        self.list_movie_items(self.tf.list_newest_movies())

    def list_newest_series(self):
        self.list_movie_items(self.tf.list_newest_series())

    def list_newest_for_kids(self):
        self.list_movie_items(self.tf.list_newest_for_kids())

    def open_item(self, title, url):
        html = self.tf._get(url)
        if self.tf.is_serie(html):
            return self.list_seasons(title, url, html)
        player_url = self.tf.parse_movie_page(html)
        stream_url = self.tf.parse_player_page(self.tf._get(player_url))
        return self.play_stream(title, stream_url)

    def play_stream(self, title, stream):
        li = self.xbmcgui.ListItem(label=title, path=stream)
        li.setInfo(type='Video', infoLabels={"Title": title})
        return self.xbmc.Player().play(item=stream, listitem=li)

    def play_episode(self, title, season_number, episode_number, episode_url):
        html = self.tf._get(episode_url)
        stream = self.tf.parse_player_page(html)
        return self.play_stream(title, stream)

    def list_seasons(self, title, url, html):
        seasons = self.tf.parse_serie_page(html)
        for idx, s in enumerate(seasons):
            self.add_season_list_item(title, idx, url)
        return self.xbmcplugin.endOfDirectory(self.handle)

    def list_episodes(self, title, season_number, url):
        html = self.tf._get(url)
        serie_info = self.tf.parse_serie_page(html)
        season_name, episodes = serie_info[season_number]
        for epi_idx, epi_info in enumerate(episodes):
            epi_name, epi_url = epi_info
            self.add_episode_list_item(title, season_number, epi_idx, epi_name, epi_url)
        return self.xbmcplugin.endOfDirectory(self.handle)

    def dispatch(self):
        if not self.params:
            return self.build_main_menu()
        if 'action' in self.params:
            action = self.params['action']
            if action == 'search':
                return self.search()
            if action == 'popular_movies':
                return self.list_popular_movies()
            if action == 'newest_movies':
                return self.list_newest_movies()
            if action == 'newest_series':
                return self.list_newest_series()
            if action == 'newest_for_kids':
                return self.list_newest_for_kids()
            if action == 'open_item':
                return self.open_item(self.params['title'],
                                      self.params['item_url'])
            if action == 'list_episodes':
                return self.list_episodes(self.params['title'],
                                          int(self.params['season_number']),
                                          self.params['serie_url'])
            if action == 'play_episode':
                return self.play_episode(self.params['title'],
                                         int(self.params['season_number']),
                                         int(self.params['episode_number']),
                                         self.params['episode_url'])
