import urllib2
from collections import namedtuple
import json

MovieItem = namedtuple('MovieItem', ['title', 'poster', 'video_url', 'is_serie'])
SerieItem = namedtuple('SerieItem', ['title', 'seasons'])
EpisodeItem = namedtuple('EpisodeItem', ['video_url', 'poster', 'episode'])

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

class TFPlay(object):

    def _get(self, url):
        content = urllib2.urlopen(url=url).read()
        return content

    def _api_url(self, q=None, genre=None, limit=None):
        url = 'http://tfplay.org/api/v2/?'
        params = []
        if q:
            params.append(("q", q))
        if genre:
            params.append(("genre", genre))
        if limit:
            params.append(("limit", limit))
        url += "&".join([("%s=%s" % (a,b)) for a, b in params])
        return url

    def _api_query(self, q=None, genre=None, limit=None):
        # Filter out the nones
        url = self._api_url(q, genre, limit)

        content = urllib2.urlopen(url=url).read()
        return content

    def _parse_result_list(self, result):
        data = json.loads(result)
        items = []
        titles = []
        for d in data:
            if d['title'] in titles:
                continue
            is_serie = int('season' in d)
            items.append(MovieItem(d['title'], d['poster'], d['video'], is_serie))
            titles.append(d['title'])
        return items

    def search(self, search_string):
        return self._parse_result_list(self._api_query(q=search_string))

    def list_genres(self):
        return GENRES

    def list_genre(self, genre):
        return self._parse_result_list(self._api_query(q=None, genre=genre, limit=100))

    def list_serie(self, serie_name):
        data = json.loads(self._api_query(q=serie_name))
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
            episode = EpisodeItem(d['video'], d['poster'], int(d['episode']))
            serie.seasons[season_nr].append(episode)
        # Sort episodes
        for s in serie.seasons:
            serie.seasons[s].sort(key=lambda x: x.episode)
        return serie


if __name__ == '__main__':
    tf = TFPlay()
    print tf.search('bad')
