import urllib2
from collections import namedtuple
import json

MovieItem = namedtuple('MovieItem', ['title', 'poster', 'video_url', 'subtitles', 'is_serie'])
SerieItem = namedtuple('SerieItem', ['title', 'seasons'])
EpisodeItem = namedtuple('EpisodeItem', ['video_url', 'poster', 'episode', 'subtitles'])

GENRES = [
    "Action",
    "Adventure",
    "Animation",
    "Biography",
    "Comedy",
    "Crime",
    "Documentary",
    "Drama",
    "Family",
    "Fantasy",
    "Film-Noir",
    "Game-Show",
    "History",
    "Horror",
    "Music",
    "Musical",
    "Mystery",
    "News",
    "Reality-TV",
    "Romance",
    "Sci-Fi",
    "Short",
    "Sport",
    "Talk-Show",
    "Thriller",
    "War",
    "Western"
]

ITEMS_PER_PAGE = 30

class TFPlay(object):

    def _get(self, url):
        content = urllib2.urlopen(url=url).read()
        return content

    def _api_url(self, **kwargs):
        url = 'http://tfplay.org/api/v2/?'
        params = []
        for key in kwargs:
            params.append((key, kwargs[key]))
        url += "&".join([("%s=%s" % (a,b)) for a, b in params])
        return url

    def _api_query(self, **kwargs):
        url = self._api_url(**kwargs)

        content = urllib2.urlopen(url=url).read()
        return content

    def _parse_result_list(self, result):
        data = json.loads(result, 'latin-1')
        items = []
        titles = []
        for d in data:
            if d['title'] in titles:
                continue
            is_serie = int('season' in d)
            items.append(MovieItem(d['title'], d['poster'], d['video'], d['subtitles'], is_serie))
            titles.append(d['title'])
        return items

    def search(self, search_string):
        return self._parse_result_list(self._api_query(q=search_string, limit=20))

    def list_just_for_kids(self, page=0):
        limit = '%s,%s' % (page * ITEMS_PER_PAGE + 1, ITEMS_PER_PAGE)
        return self._parse_result_list(self._api_query(kids='true', limit=limit))

    def list_movies(self, page=0):
        limit = '%s,%s' % (page * ITEMS_PER_PAGE + 1, ITEMS_PER_PAGE)
        return self._parse_result_list(self._api_query(movies='true', limit=limit))

    def list_series(self, page=0):
        limit = '%s,%s' % (page * ITEMS_PER_PAGE + 1, ITEMS_PER_PAGE)
        return self._parse_result_list(self._api_query(series='true', group='true', limit=limit))

    def list_genres(self):
        return GENRES

    def list_genre(self, genre, page=0):
        limit = '%s,%s' % (page * ITEMS_PER_PAGE + 1, ITEMS_PER_PAGE)
        return self._parse_result_list(self._api_query(genre=genre, limit=limit))

    def serie(self, serie_name):
        data = json.loads(self._api_query(q=serie_name), 'latin-1')
        serie = None
        for d in data:
            if d['title'].lower() != serie_name.lower():
                continue
            if 'season' not in d:
                continue
            season_nr = int(d['season'])
            if not serie:
                serie = SerieItem(d['title'], {})
            if season_nr not in serie.seasons:
                serie.seasons[season_nr] = []
            episode = EpisodeItem(d['video'], d['poster'], int(d['episode']), d['subtitles'])
            serie.seasons[season_nr].append(episode)
        # Sort episodes
        for s in serie.seasons:
            serie.seasons[s].sort(key=lambda x: x.episode)
        return serie


if __name__ == '__main__':
    tf = TFPlay()
    #print tf.search('bad')
    print tf._api_url(q='balla')
    print tf._api_url(q='balla', limit='10')
    print tf._api_url(q='balla', limit='10', kids='true')
