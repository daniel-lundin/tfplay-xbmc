import urllib2

SEARCH_URL = 'http://tfplay.org/search/'


class TFPlay(object):

    def _get(self, url):
        content = urllib2.urlopen(url=url).read()
        return content

    def _search(self, search_string):
        res = self._get(SEARCH_URL + '?q=' + search_string)
        return res

    def search(self, search_string):
        return self.parse_search(self._search(search_string))

    def is_serie(self, html):
        return 'Season 1' in html

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
        return url

        # TODO: Subtitles
        #TRACK = '<track src="'
        #start = html.find(TRACK)
        #end = html.find('"', start + 13)
        #url = html[start + 13:end]

if __name__ == '__main__':
    tf = TFPlay()
    print tf.search('bad')
