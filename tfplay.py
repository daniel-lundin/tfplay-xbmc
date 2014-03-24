import urllib2
from collections import namedtuple

SEARCH_URL = 'http://tfplay.org/search/'
STARTPAGE_URL = 'http://tfplay.org/'
TVSERIES_URL = 'http://tfplay.org/media/tv-series/'

MovieItem = namedtuple('MovieItem', ['title', 'url', 'thumb_url'])
StartPage = namedtuple('StartPage', ['popular_movies',
                                     'newest_movies',
                                     'newest_series',
                                     'newest_for_kids'])

Subtitle = namedtuple('Subtitle', ['url', 'label'])


class TFPlay(object):

    def _get(self, url):
        content = urllib2.urlopen(url=url).read()
        return content

    def _search(self, search_string):
        res = self._get(SEARCH_URL + '?q=' + search_string)
        return res

    def _startpage(self):
        return self._get(STARTPAGE_URL)

    def _tvseries(self):
        return self._get(TVSERIES_URL)

    def search(self, search_string):
        return self.parse_search(self._search(search_string))

    def is_serie(self, html):
        return 'Season 1' in html

    def list_popular_movies(self):
        return self.parse_start_page(self._startpage()).popular_movies

    def list_newest_movies(self):
        return self.parse_start_page(self._startpage()).newest_movies

    def list_newest_series(self):
        return self.parse_start_page(self._startpage()).newest_series

    def list_newest_for_kids(self):
        return self.parse_start_page(self._startpage()).newest_for_kids

    def list_tv_series(self):
        return self.parse_series_list(self._tvseries())

    def parse_search(self, html):
        RES = '<div class="item-poster'
        r_idx = html.find(RES)
        matches = []
        while r_idx != -1:
            url_start = html.find('data-href="', r_idx) + 11
            url_end = html.find('"', url_start)
            url = html[url_start: url_end]
            title_start = html.find('title="', url_end) + 7
            title_end = html.find('"', title_start)
            title = html[title_start:title_end]
            matches.append((title, url))
            r_idx = html.find(RES, r_idx + 1)
        return matches

    def parse_video_list(self, html):
        item_start = html.find('<div class="item"')
        items = []
        while item_start != -1:
            title_start = html.find('title="', item_start) + 7
            title_end = html.find('"', title_start)
            a_start = html.find('<a href="', item_start) + 9
            a_end = html.find('"', a_start)
            thumb_start = html.find('<img src="', a_start) + 10
            thumb_end = html.find('"', thumb_start)
            items.append(MovieItem(html[title_start:title_end],
                                   html[a_start:a_end],
                                   html[thumb_start:thumb_end]))
            item_start = html.find('<div class="item"', item_start + 1)
        return items

    def parse_start_page(self, html):
        parts = html.split('videos-list')
        return StartPage(self.parse_video_list(parts[1]),
                         self.parse_video_list(parts[2]),
                         self.parse_video_list(parts[3]),
                         self.parse_video_list(parts[4]))

    def parse_series_list(self, html):
        item_poster_start = html.find('<div class="item-poster')
        items = []
        while item_poster_start != -1:
            data_href_start = html.find('data-href', item_poster_start) + 11
            data_href_end = html.find('"', data_href_start)
            url = html[data_href_start:data_href_end]
            title_start = html.find("title", item_poster_start) + 7
            title_end = html.find('"', title_start)
            title = html[title_start:title_end]
            img_start = html.find('<img class="poster" src="', item_poster_start) + 25
            img_end = html.find('"', img_start)
            thumb_url = html[img_start:img_end]
            items.append(MovieItem(title, url, thumb_url))
            item_poster_start = html.find('<div class="item-poster', item_poster_start+1)
        return items

    def parse_movie_page(self, html):
        LINK = '<a href="http://tfplay.org/media/play/'
        start = html.find(LINK)
        end = html.find('"', start + 9)
        return html[start + 9:end]

    def parse_serie_page(self, html):
        seasons = []
        season_idx = html.find('<a href="#season')
        while season_idx != -1:
            season_start = html.find(">", season_idx + 1) + 1
            season_end = html.find("<", season_start)
            seasons.append(html[season_start:season_end])
            season_idx = html.find('<a href="#season', season_idx + 1)

        serie_info = []
        episode_lists = html.split('<ul class="nav nav-pills"')

        PLAY_LINK = '<a href="http://tfplay.org/media/play'
        for season_idx, epi_list in enumerate(episode_lists[2:]):
            epi_idx = epi_list.find(PLAY_LINK)
            episodes = []
            while epi_idx != -1:
                url_start = epi_idx + 9
                url_end = epi_list.find('"', url_start)
                url = epi_list[url_start:url_end]
                epi_name_start = epi_list.find('>', url_end) + 1
                epi_name_end = epi_list.find('<', epi_name_start)
                epi_name = epi_list[epi_name_start:epi_name_end]
                episodes.append((epi_name, url))
                #print epi_name, url
                epi_idx = epi_list.find(PLAY_LINK, epi_idx + 1)
            serie_info.append((seasons[season_idx], episodes))

        return serie_info

    def parse_player_page(self, html):
        # Media url
        SOURCE = '<source src="'
        start = html.find(SOURCE)
        end = html.find('"', start + 13)
        url = html[start + 13:end]

        # Find subtitles
        subtitles = []
        TRACK = '<track src="'
        track_src_start = html.find(TRACK)
        while track_src_start != -1:
            track_src_end = html.find('"', track_src_start + len(TRACK))
            track_src = html[track_src_start + len(TRACK):track_src_end]

            label_start = html.find('label=', track_src_start) + 7
            label_end = html.find('"', label_start)
            label = html[label_start:label_end]

            subtitles.append(Subtitle(track_src, label))
            track_src_start = html.find(TRACK, track_src_start + 1)

        return url, subtitles


if __name__ == '__main__':
    tf = TFPlay()
    print tf.search('bad')
