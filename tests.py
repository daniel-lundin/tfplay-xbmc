import unittest
import tfplay


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
            stream_url = tf.parse_player_page(f.read())
            expected_url = "http://server1.media.tfplay.org/d3/d191515232ae70c3d33de440d6628bf6613a0ce8.mp4"
            self.assertEqual(stream_url, expected_url, "Error parsing movie player")

    def test_parse_startpage(self):
        with open('fixtures/startpage.html') as f:
            tf = tfplay.TFPlay()
            startpage = tf.parse_start_page(f.read())
            print startpage.popular_movies
            self.assertEqual(len(startpage.popular_movies), 30)
            self.assertEqual(len(startpage.newest_movies), 30)
            self.assertEqual(len(startpage.newest_series), 30)
            self.assertEqual(len(startpage.newest_for_kids), 30)

if __name__ == '__main__':
    unittest.main()
