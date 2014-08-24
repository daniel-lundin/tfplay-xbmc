import unittest
import tfplay
import navigation
import mocks


class Tests(unittest.TestCase):

    def test_api_url(self):
        tf = tfplay.TFPlay()
        genre_url = tf._api_url(q=None, genre="action")
        genre_url_limit = tf._api_url(q=None, genre="action", limit=10)
        search_url = tf._api_url(q='godzilla')
        self.assertEqual(genre_url, 'http://tfplay.org/api/v2/?genre=action')
        self.assertEqual(genre_url_limit, 'http://tfplay.org/api/v2/?genre=action&limit=10')
        self.assertEqual(search_url, 'http://tfplay.org/api/v2/?q=godzilla')

    def test_search(self):
        with open('fixtures/godzilla.json') as f:
            tf = tfplay.TFPlay()
            def mock(*args, **kwargs): return f.read()
            tf._api_query = mock
            search_results = tf.search('godzilla')
            self.assertEqual(len(search_results), 1, "Failed search")

    def test_movie_list(self):
        with open('fixtures/genre_50.json') as f:
            tf = tfplay.TFPlay()
            def mock(*args, **kwargs): return f.read()
            tf._api_query = mock
            search_results = tf.list_genre('action')
            self.assertEqual(len(search_results), 21, "Movie list")

    def test_serie_list(self):
        with open('fixtures/serie.json') as f:
            tf = tfplay.TFPlay()
            def mock(*args, **kwargs): return f.read()
            tf._api_query = mock
            serie = tf.list_serie('arrow')
            self.assertEqual(len(serie.seasons.keys()), 2, "Error listing seasons")
            self.assertEqual(len(serie.seasons[1]), 22, "Error listing seasons")



class NavigationTests(unittest.TestCase):
    def setUp(self):
        self.nav = navigation.Navigation(tfplay.TFPlay(), mocks.Xbmc(),
                                         mocks.Xbmcplugin(),
                                         mocks.Xbmcgui,
                                         ['plugin.video.tfplay', 1])

    def test_main_menu(self):
        self.nav.build_main_menu()
        self.assertEqual(len(self.nav.xbmcplugin.dir_items), 2)


if __name__ == '__main__':
    unittest.main()
