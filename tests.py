import unittest
import tfplay
import navigation
import mocks


class ParseTests(unittest.TestCase):
    def test_search_parse(self):
        with open('fixtures/search.html') as f:
            tf = tfplay.TFPlay()
            search_results = tf.parse_search(f.read())
            self.assertEqual(len(search_results), 24, "Failed parsing search")

    def test_movie_parse(self):
        with open('fixtures/movie.html') as f:
            tf = tfplay.TFPlay()
            player_url = tf.parse_movie_page(f.read())
            expected_url = "http://tfplay.org/media/play/?video=153023e475de9c"
            self.assertEqual(player_url, expected_url, "Error parsing movie page")

    def test_serie_parse(self):
        with open('fixtures/serie.html') as f:
            tf = tfplay.TFPlay()
            seasons = tf.parse_serie_page(f.read())
            self.assertEqual(len(seasons), 9, "Wrong number of seasons")

    def test_player_parse(self):
        with open('fixtures/player.html') as f:
            tf = tfplay.TFPlay()
            stream_url, subtitles = tf.parse_player_page(f.read())
            expected_url = "http://server1.media.tfplay.org/d3/d191515232ae70c3d33de440d6628bf6613a0ce8.mp4"
            self.assertEqual(stream_url, expected_url, "Error parsing movie player")

    def test_player_parse_with_subs(self):
        with open('fixtures/movie_subs.html') as f:
            tf = tfplay.TFPlay()
            stream_url, subtitles = tf.parse_player_page(f.read())
            self.assertEqual(len(subtitles), 1, "Expected one subtitle")

    def test_parse_startpage(self):
        with open('fixtures/startpage.html') as f:
            tf = tfplay.TFPlay()
            startpage = tf.parse_start_page(f.read())
            self.assertEqual(len(startpage.popular_movies), 30)
            self.assertEqual(len(startpage.newest_movies), 30)
            self.assertEqual(len(startpage.newest_series), 30)
            self.assertEqual(len(startpage.newest_for_kids), 30)

    def test_movie_item_has_subtitles(self):
        with open('fixtures/startpage.html') as f:
            tf = tfplay.TFPlay()
            startpage = tf.parse_start_page(f.read())
            hunger_game_movie = startpage.popular_movies[0]
            flygplan_movie = startpage.popular_movies[5]
            self.assertTrue(hunger_game_movie.has_subs, "Hunger games should have subs")
            self.assertFalse(flygplan_movie.has_subs, "Flygplan should have no subs")

    def test_parse_tv_series(self):
        with open('fixtures/tvseries.html') as f:
            tf = tfplay.TFPlay()
            items = tf.parse_series_list(f.read())
            self.assertEqual(len(items), 69)


class NavigationTests(unittest.TestCase):
    def setUp(self):
        self.nav = navigation.Navigation(tfplay.TFPlay(), mocks.Xbmc(),
                                         mocks.Xbmcplugin(),
                                         mocks.Xbmcgui,
                                         ['plugin.video.tfplay', 1])

    def test_main_menu(self):
        self.nav.build_main_menu()
        self.assertEqual(len(self.nav.xbmcplugin.dir_items), 7)


if __name__ == '__main__':
    unittest.main()
